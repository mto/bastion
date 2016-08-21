#!/usr/bin/env python

__author__ = 'hoang281283@gmail.com'

import config
import curses
import os
import datetime


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


def open_ssh_in_tmux_and_record(host):
    assert isinstance(host, SSHConnectParam)

    now = datetime.datetime.now()
    log_dst = "../asciinema_logs/%s-%s-%s-%s-%s-%s_%s_%s.log" % (
        host.user, host.domain, now.year, now.month, now.day, now.hour, now.minute, now.second)

    ascii_cmd = "asciinema rec -c '%s' %s" % (host.ssh_command(), log_dst)

    cmd = "tmux new-window -n %s \"%s ;read\"" % (host.connect_title(), ascii_cmd)
    execute_cmd(cmd)


def append_spaces(text, length):
    size = len(text)
    if size >= length:
        return text
    else:
        return text + ' ' * (length - size)


class Picker(object):
    def __init__(self):
        self.total = 0
        self.selected_index = 0
        self.hosts = []
        self.loaded_hosts = []
        self.total_loaded = 0

    def load_config(self):
        for host in config.hosts:
            user = host.get('user', config.default_user)
            domain = host.get('domain')
            port = host.get('port', config.default_port)
            category = host.get('category', 'N/A')
            desc = host.get('desc', 'N/A')

            sshcp = SSHConnectParam(user, domain, port, category, desc)
            self.loaded_hosts.append(sshcp)
            self.total_loaded += 1
            self.hosts.append(sshcp)
            self.total += 1

    def all_hosts(self):
        return self.hosts

    def current(self):
        return self.hosts[self.selected_index]

    def move_down(self):
        self.selected_index = (self.selected_index + 1) % self.total

    def move_up(self):
        self.selected_index = (self.selected_index - 1) % self.total

    def update(self, hosts, selected_idx):
        self.hosts = hosts
        self.total = len(self.hosts)
        self.selected_index = selected_idx

    def reset(self):
        self.hosts = self.loaded_hosts
        self.total = self.total_loaded
        self.selected_index = 0

    def search(self, exp):
        ret = list()
        for host in self.loaded_hosts:
            if host.contain(exp):
                ret.append(host)

        return ret


class SSHConnectParam(object):
    def __init__(self, user, domain, port, category, desc):
        self.user = user
        self.domain = domain
        self.port = port
        self.category = category
        self.desc = desc

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
        return str.find(self.content(), exp) >= 0


class Screen(object):
    def __init__(self, window):
        self.window = window
        self.search_mode = False
        self.search_txt = ''

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

    def display_header(self):
        txt = append_spaces('Username', 22) + append_spaces('Domain', 52) + append_spaces('Port', 12) + append_spaces(
            'Category', 30)
        self.window.addstr(1, 1, txt)
        self.window.hline(2, 1, '-', len(txt))

    def display_hosts(self, hosts, sidx):
        for i in range(len(hosts)):
            host = hosts[i]
            if i == sidx:
                self.window.addstr(i + 4, 1, host.content(), curses.A_STANDOUT)
            else:
                self.window.addstr(i + 4, 1, host.content())

    def display_search_box(self):
        if not self.search_mode:
            return
        txt = '[SEARCH MODE] type something to search | [DEL] Remove last typed character | [ESC] Exit Search Mode'
        h = self.get_height()
        self.window.addstr(h - 2, 1, txt)
        self.window.addstr(h - 4, 1, self.search_txt)

    def redraw(self, hosts, sidx):
        self.clear()
        self.window.border(0)
        self.display_header()
        self.display_hosts(hosts, sidx)
        self.display_search_box()
        self.refresh()


class Bastion(object):
    def __init__(self, picker, screen):
        assert isinstance(picker, Picker)
        assert isinstance(screen, Screen)

        self.picker = picker
        self.screen = screen

    def start(self):
        self.screen.display_header()
        self.screen.display_hosts(self.picker.all_hosts(), self.picker.selected_index)

        self.start_event_loop()

    def start_event_loop(self):
        while True:
            key = self.screen.getch()

            if self.screen.search_mode:
                self.handle_event_in_search_mode(key)
            else:
                if key == 113:  # Quit q
                    break

                elif key == curses.KEY_UP:
                    self.picker.move_up()
                    self.screen.redraw(self.picker.all_hosts(), self.picker.selected_index)

                elif key == curses.KEY_DOWN:
                    self.picker.move_down()
                    self.screen.redraw(self.picker.all_hosts(), self.picker.selected_index)

                elif key == 10:  # Press ENTER
                    host = picker.current()
                    open_ssh_in_tmux_and_record(host)

                elif key == 47:  # Press '/'
                    self.screen.enter_search_mode()
                    self.screen.redraw(self.picker.all_hosts(), self.picker.selected_index)

        curses.endwin()
        kill_tmux_session('bastion')

    def handle_event_in_search_mode(self, key):
        if key == 27:  # Press 'ESC'
            self.screen.exit_search_mode()
            self.picker.reset()
            self.screen.redraw(self.picker.all_hosts(), self.picker.selected_index)

        elif key == curses.KEY_UP:
            self.picker.move_up()
            self.screen.redraw(self.picker.all_hosts(), self.picker.selected_index)

        elif key == curses.KEY_DOWN:
            self.picker.move_down()
            self.screen.redraw(self.picker.all_hosts(), self.picker.selected_index)

        elif key == 127: #The DEL key
            self.screen.delete_search_char()
            hosts = self.picker.search(self.screen.search_txt)
            self.picker.update(hosts, 0)

            self.screen.redraw(self.picker.all_hosts(), self.picker.selected_index)

        else:
            self.screen.type_search_char(chr(key))
            hosts = self.picker.search(self.screen.search_txt)
            self.picker.update(hosts, 0)

            self.screen.redraw(self.picker.all_hosts(), self.picker.selected_index)

if __name__ == '__main__':
    window = curses.initscr()
    window.border(0)
    curses.noecho()
    curses.cbreak()
    window.keypad(1)

    screen = Screen(window)

    picker = Picker()
    picker.load_config()

    Bastion(picker, screen).start()
