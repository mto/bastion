#!/usr/bin/env python

__author__ = 'hoang281283@gmail.com'

import curses
import curses.panel
import os
import datetime
import config
import time
from picker import Picker


def execute_cmd(cmd):
    os.system(cmd)


def start_tmux_session(name):
    execute_cmd("tmux new -s %s" % name)


def kill_tmux_session(name):
    execute_cmd("tmux kill-session -t %s" % name)


def open_tmux_window(title):
    execute_cmd("tmux new-window -n %s &" % title)


def open_ssh_in_tmux(host):
    assert isinstance(host, SSHConnectParam)

    cmd = "tmux new-window -n %s '%s ;read'" % (host.connect_title(), host.ssh_command())
    execute_cmd(cmd)


def open_multi_ssh_in_tmux(hosts):
    for host in hosts:
        if host.record:
            open_ssh_in_tmux_and_record(host)
        else:
            open_ssh_in_tmux(host)


def open_ssh_in_tmux_and_record(host):
    assert isinstance(host, SSHConnectParam)

    now = datetime.datetime.now()
    log_dst = "../asciinema_logs/%s-%s-%s-%s-%s-%s_%s_%s.log" % (
        host.user, host.domain, now.year, now.month, now.day, now.hour, now.minute, now.second)

    ascii_cmd = "asciinema rec -c '%s' %s" % (host.ssh_command(), log_dst)

    cmd = "tmux new-window -n %s \"%s ;read\"" % (host.connect_title(), ascii_cmd)
    execute_cmd(cmd)


def open_multi_ssh_in_tmux_and_record(hosts):
    for host in hosts:
        open_ssh_in_tmux_and_record(host)


def playback_asciinema_log_in_tmux(logfile):
    ascii_cmd = "asciinema play '%s'" % logfile

    cmd = "tmux new-window -n ShowLog \"%s ;read\"" % (ascii_cmd)
    execute_cmd(cmd)


def append_spaces(text, length):
    size = len(text)
    if size >= length:
        return text
    else:
        return text + ' ' * (length - size)


class Category(object):
    def __init__(self, name):
        self.name = name
        self.total_hosts = []
        self.count = 0

    def content(self):
        name = append_spaces(self.name, 20)
        total = append_spaces(str(self.count), 10)

        return ' %s  %s' % (name, total)

    def add_host(self, host):
        if isinstance(host, SSHConnectParam):
            self.total_hosts.append(host)
            self.count += 1


class SSHConnectParam(object):
    def __init__(self, number, user, domain, port, category, desc, record=False):
        self.number = number
        self.user = user
        self.domain = domain
        self.port = port
        self.category = category
        self.desc = desc
        self.record = record

    def connect_title(self):
        return '%s@%s' % (self.user, self.domain)

    def ssh_command(self):
        return 'ssh %s@%s -p %s' % (self.user, self.domain, self.port)

    def content(self):
        u = append_spaces(self.user, 20)
        d = append_spaces(self.domain, 50)
        p = append_spaces(str(self.port), 10)

        return ' %s  %s  %s  %s' % (u, d, p, self.category)

    def match(self, regex):
        pass

    def contain(self, exp):
        p = exp.lower()

        return str.find(self.user.lower(), p) >= 0 or \
               str.find(self.domain.lower(), p) >= 0 or \
               str.find(str(self.port), p) >= 0 or \
               str.find(self.category.lower(), p) >= 0 or \
               str.find(self.desc.lower(), p) >= 0

    def equals(self, host):
        return isinstance(host, SSHConnectParam) and self.number == host.number

    def belongs_to(self, hosts):
        for host in hosts:
            if self.equals(host):
                return True
        return False


class Screen(object):
    def __init__(self, bastion, window, admin_mode=False, logo_content=[]):
        self.bastion = bastion
        self.window = window
        self.search_mode = False
        self.search_txt = ''
        self.display_panel = curses.panel.new_panel(curses.newwin(30, 100, 5, 10))
        self.display_log_panel = curses.panel.new_panel(curses.newwin(30, 100, 5, 10))
        self.admin_mode = admin_mode
        self.logo_content = logo_content
        self.logo_height = len(self.logo_content) + 2
        self.host_table_header = append_spaces('Username', 22) + append_spaces('Domain', 52) + append_spaces('Port', 12) + append_spaces(
            'Category', 30)
        self.host_table_length = len(self.host_table_header)

    def refresh(self):
        self.window.refresh()

    def clear(self):
        self.window.clear()

    def getch(self):
        return self.window.getch()

    def enter_search_mode(self):
        self.search_mode = True

    def exit_search_mode(self):
        self.search_mode = False
        self.search_txt = ''

    def search_mode(self):
        return self.search_mode

    def type_search_char(self, ch):
        self.search_txt += ch

    def delete_search_char(self):
        self.search_txt = self.search_txt[:-1]

    def get_width(self):
        return self.window.getmaxyx()[1]

    def get_height(self):
        return self.window.getmaxyx()[0]

    def display_logo(self):
        for i in range(len(self.logo_content)):
            self.window.addstr(i + 1, 1, self.logo_content[i])

    def display_header(self):
        if self.bastion.showing_cat:
            pass
        else:
            self.window.hline(self.logo_height, 1, '-', self.host_table_length)
            self.window.addstr(self.logo_height + 1, 1, self.host_table_header)
            self.window.hline(self.logo_height + 2, 1, '-', self.host_table_length)

    def display_categories(self):
        categories = self.bastion.cat_picker.items
        sidx = self.bastion.cat_picker.selected_index

        for i in range(len(categories)):
            cat = categories[i]
            if i == sidx:
                self.window.addstr(i + 4 + self.logo_height, 1, cat.content(), curses.A_STANDOUT)
            else:
                self.window.addstr(i + 4 + self.logo_height, 1, cat.content())

    def display_hosts(self):
        vp_min = self.bastion.picker.viewport_min_idx
        vp_max = self.bastion.picker.viewport_max_idx
        hosts = self.bastion.picker.items
        sidx = self.bastion.picker.selected_index
        ms_idxs = self.bastion.picker.multi_selected_idxs

        row_idx = 0
        for i in range(vp_min, vp_max):
            host = hosts[i]
            if i == sidx:
                if i in ms_idxs:
                    self.window.addstr(row_idx + 4 + self.logo_height, 1, host.content() + '    X', curses.A_STANDOUT)
                else:
                    self.window.addstr(row_idx + 4 + self.logo_height, 1, host.content(), curses.A_STANDOUT)

            elif self.bastion.multi_select and i in ms_idxs:
                self.window.addstr(row_idx + 4 + self.logo_height, 1, host.content() + '    X')
            else:
                self.window.addstr(row_idx + 4 + self.logo_height, 1, host.content())

            row_idx += 1

    def display_search_box(self):
        if self.bastion.showing_cat:
            return

        h = self.get_height()
        self.window.hline(h-5, 1, '-', self.host_table_length)

        if not self.search_mode:
            if self.admin_mode:
                self.window.addstr(h - 2, 1, '[/] Enter SEARCH mode| [ENTER] Connect| [Shift+i] View Host| [q] Quit')
            else:
                self.window.addstr(h - 2, 1, '[/] Enter SEARCH mode| [ENTER] Connect| [Shift+i] View Host')

        else:
            txt = '[SEARCH MODE]: Type something to search' \
                  '| [ENTER] Connect| [Shift+i] View Host |[ESC]: Exit Search Mode'
            self.window.addstr(h - 2, 1, txt)
            self.window.addstr(h - 4, 1, self.search_txt)

    def redraw(self):
        self.clear()
        self.window.border(0)
        if self.bastion.showing_cat:
            self.display_logo()
            self.display_categories()
            self.refresh()
        else:
            self.display_logo()
            self.display_header()
            self.display_hosts()
            self.display_search_box()
            self.refresh()

    def show_host_detail(self, host):
        assert isinstance(host, SSHConnectParam)
        dpw = self.display_panel.window()
        dpw.clear()
        dpw.border(0)
        dpw.addstr(2, 1, 'USERNAME: %s' % host.user)
        dpw.addstr(4, 1, 'DOMAIN: %s' % host.domain)
        dpw.addstr(6, 1, 'PORT: %s' % host.port)
        dpw.addstr(8, 1, 'CATEGORY: %s' % host.category)
        dpw.addstr(10, 1, 'RECORD: %s' % str(host.record))
        dpw.addstr(12, 1, 'DESCRIPTION: %s' % host.desc)
        dpw.addstr(28, 1, '[ENTER]: Connect | [ESC]: Close dialog')

        self.display_panel.show()

        key = dpw.getch()
        if key == 27:  # Press ESC
            self.display_panel.hide()
        elif key == 10:
            if host.record:
                open_ssh_in_tmux_and_record(host)
            else:
                open_ssh_in_tmux(host)

    def show_log_files(self, logman):
        assert isinstance(logman, LogManager)

        dpw = self.display_log_panel.window()
        dpw.clear()
        dpw.border(0)

        dpw.addstr(1, 1, 'User activities records:')
        all_logs = logman.files
        for i in range(len(all_logs)):
            lf = all_logs[i]
            if i == logman.selected_index:
                dpw.addstr(i + 4, 1, lf, curses.A_STANDOUT)
            else:
                dpw.addstr(i + 4, 1, lf)
        dpw.refresh()

    def show_logs_panel(self, logman):
        assert isinstance(logman, LogManager)
        self.show_log_files(logman)

        dpw = self.display_log_panel.window()
        while True:
            key = dpw.getch()
            if key == 27:
                break
            elif key == 10:
                lf = logman.current()
                if lf is not None:
                    playback_asciinema_log_in_tmux('../asciinema_logs/%s' % lf)

            elif key == curses.KEY_UP:
                logman.move_up()
                self.show_log_files(logman)

            elif key == curses.KEY_DOWN:
                logman.move_down()
                self.show_log_files(logman)

        self.display_log_panel.hide()


class LogManager(object):
    def __init__(self, folder):
        self.folder = folder
        self.files = []
        self.total = 0
        self.selected_index = 0

    def reload(self):
        try:
            tmp = list()
            all_logs = os.listdir(self.folder)
            self.total = len(all_logs)
            for log in all_logs:
                if log.endswith('.log'):
                    tmp.append(log)

            self.files = tmp
        except Exception as e:
            pass

    def move_down(self):
        self.selected_index = (self.selected_index + 1) % self.total

    def move_up(self):
        self.selected_index = (self.selected_index - 1) % self.total

    def current(self):
        if self.selected_index < self.total:
            return self.files[self.selected_index]
        else:
            return None


class Bastion(object):
    def __init__(self, picker, cat_picker, sid, admin_mode=False, log_man=None):
        assert isinstance(picker, Picker)

        self.picker = picker
        self.screen = None
        self.tmux_name = 'bastion-' + sid
        self.multi_select = False
        self.admin_mode = admin_mode
        self.log_man = log_man
        self.start_time = int(time.time()*1000)
        self.cat_picker = cat_picker
        self.showing_cat = True

    def inject_screen(self, screen):
        assert isinstance(screen, Screen)
        self.screen = screen

    def start(self):
        self.screen.display_logo()
        if self.showing_cat:
            self.screen.display_categories()
        else:
            self.screen.display_header()
            self.screen.display_hosts()
            self.screen.display_search_box()

        self.start_event_loop()

    def event_loop(self):
        while True:
            key = self.screen.getch()

            if key == -1 and (self.start_time + config.idle_period) <= int(time.time()*1000):  # Timeout
                break

            if self.admin_mode and key == 113:  # Quit q
                break

            if self.showing_cat:
                self.handle_event_in_showing_category_mode(key)
            elif self.screen.search_mode:
                self.handle_event_in_search_mode(key)
            else:
                if key == curses.KEY_LEFT:
                    self.showing_cat = True
                    self.screen.redraw()

                elif key == curses.KEY_UP:
                    self.picker.move_up()
                    self.screen.redraw()

                elif key == curses.KEY_DOWN:
                    self.picker.move_down()
                    self.screen.redraw()

                elif key == 10: # Press Enter
                    if self.multi_select:
                        self.multi_select = False
                        ms_hosts = self.picker.ms_items()
                        self.picker.exit_multi_select()
                        if len(ms_hosts) > 0:
                            open_multi_ssh_in_tmux(ms_hosts)
                    else:
                        host = self.picker.current()
                        if host is not None:
                            if host.record:
                                open_ssh_in_tmux_and_record(host)
                            else:
                                open_ssh_in_tmux(host)

                elif key == ord(' '):
                    if self.multi_select:
                        self.picker.multi_select_add(self.picker.selected_index)
                        self.screen.redraw()

                elif key == ord('M'): # Enter multi-select
                    if self.multi_select:
                        self.multi_select = False
                        self.picker.exit_multi_select()
                    else:
                        self.multi_select = True
                        self.picker.enter_multi_select()

                    self.screen.redraw()

                elif key == ord('I'):  # Press Shift+i
                    curses.beep()
                    host = self.picker.current()
                    if host is not None:
                        self.screen.show_host_detail(host)

                elif key == 47:  # Press '/'
                    self.screen.enter_search_mode()
                    self.screen.redraw()

                #elif key == ord('L') and self.admin_mode:  # Press Shift+L
                #    self.log_man.reload()
                #    self.screen.show_logs_panel(self.log_man)

    def start_event_loop(self):
        try:
            self.event_loop()
        except Exception as e:
            print e
        finally:
            curses.nocbreak()
            self.screen.window.keypad(0)
            curses.echo()
            curses.endwin()
            kill_tmux_session(self.tmux_name)

    def handle_event_in_showing_category_mode(self, key):
        if key == curses.KEY_UP:
            self.cat_picker.move_up()
            self.screen.redraw()

        elif key == curses.KEY_DOWN:
            self.cat_picker.move_down()
            self.screen.redraw()

        elif key == 10: # Press Enter
            cate = self.cat_picker.current()
            assert isinstance(cate, Category)

            if cate is not None:
                self.showing_cat = False
                self.picker.update(cate.total_hosts, 0)
                self.screen.redraw()

    def handle_event_in_search_mode(self, key):
        if key == 27:  # Press 'ESC'
            self.screen.exit_search_mode()
            self.picker.reset()
            self.screen.redraw()

        elif key == curses.KEY_UP:
            self.picker.move_up()
            self.screen.redraw()

        elif key == curses.KEY_DOWN:
            self.picker.move_down()
            self.screen.redraw()

        elif key == 10: # Press Enter
            if self.multi_select:
                self.multi_select = False
                ms_hosts = self.picker.ms_items()
                self.picker.exit_multi_select()
                if len(ms_hosts) > 0:
                    open_multi_ssh_in_tmux(ms_hosts)
            else:
                host = self.picker.current()
                if host is not None:
                    if host.record:
                        open_ssh_in_tmux_and_record(host)
                    else:
                        open_ssh_in_tmux(host)

        elif key == curses.KEY_RESIZE:
            pass

        elif key == ord('M'):
            if self.multi_select:
                self.multi_select = False
                self.picker.exit_multi_select()
            else:
                self.multi_select = True
                self.picker.enter_multi_select()

        elif key == ord('I'):  # Press Shift+i
            curses.beep()
            host = self.picker.current()
            if host is not None:
                self.screen.show_host_detail(self.picker.current())

        elif key == 127:  # The DEL key
            self.screen.delete_search_char()
            hosts = self.picker.search(self.screen.search_txt)
            self.picker.update(hosts, 0)

            self.screen.redraw()

        elif key < 256:
            c = chr(key)
            if str.isalnum(c) or c == ' ' or c == ',' or c == '.' or c == '&':
                self.screen.type_search_char(chr(key))
                hosts = self.picker.search(self.screen.search_txt)
                self.picker.update(hosts, 0)

                self.screen.redraw()


def bootstrap(sid, admin_mode=False, logo_content=[]):
    window = curses.initscr()
    window.border(0)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    window.keypad(1)
    window.timeout(config.idle_period)

    picker = Picker(15)
    cat_picker = Picker(15)

    categories = {}
    cate_ALL = Category('_ALL_')

    for i in range(len(config.hosts)):
        host = config.hosts[i]
        user = host.get('user', config.default_user)
        domain = host.get('domain')
        port = host.get('port', config.default_port)
        category = host.get('category', 'Other')
        desc = host.get('desc', 'N/A')
        record = host.get('record', config.default_record)

        sshcp = SSHConnectParam(str(i), user, domain, port, category, desc, record)
        cate_ALL.add_host(sshcp)

        cate_names = [x.strip() for x in category.split(',')]
        for cate_name in cate_names:
            cate = categories.get(cate_name, None)
            if cate is None:
                cate = Category(cate_name)
                categories[cate_name] = cate
            cate.add_host(sshcp)

    sorted_keys = sorted(categories.keys())
    categos_as_list = list()
    for sk in sorted_keys:
        categos_as_list.append(categories.get(sk))
    categos_as_list.append(cate_ALL)

    if len(categos_as_list) > 0:
        picker.initialize(categos_as_list[0].total_hosts)
        cat_picker.initialize(categos_as_list)

    bastion = Bastion(picker, cat_picker, sid, admin_mode)
    screen = Screen(bastion, window, admin_mode, logo_content)
    bastion.inject_screen(screen)

    bastion.start()

