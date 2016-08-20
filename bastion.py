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


def start_command_executor(bastion):
    while True:
        if len(bastion.cmds) > 0:
            cmd = bastion.cmds.pop(0)
            os.system(cmd)


class Picker(object):
    def __init__(self):
        self.total = 0
        self.selected_index = 0
        self.change_viewport = False
        self.hosts = []

    def load_config(self):
        for host in config.hosts:
            user = host.get('user', config.default_user)
            domain = host.get('domain')
            port = host.get('port', config.default_port)
            category = host.get('category', 'N/A')
            desc = host.get('desc', 'N/A')

            self.hosts.append(SSHConnectParam(user, domain, port, category, desc))
            self.total += 1

    def all_hosts(self):
        return self.hosts

    def current(self):
        return self.hosts[self.selected_index]

    def move_down(self):
        self.selected_index = (self.selected_index + 1) % self.total

    def move_up(self):
        self.selected_index = (self.selected_index - 1) % self.total


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
        return '%s  |  %s | %s ' % (self.domain, self.category, self.desc)


class Screen(object):
    def __init__(self, window):
        self.window = window
        self.search_mode = False

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

    def search_mode(self):
        return self.search_mode

    def get_width(self):
        return self.window.getmaxyx()[1]

    def get_height(self):
        return self.window.getmaxyx()[0]

    def display_header(self):
        txt = 'Hosts'
        if self.search_mode:
            txt = 'Matched Hosts'

        self.window.addstr(1, 4, txt)
        self.window.hline(2, 1, '#', self.get_width() - 2)

    def display_hosts(self, hosts, sidx):
        for i in range(len(hosts)):
            host = hosts[i]
            if i == sidx:
                self.window.addstr(i + 4, 4, host.content(), curses.A_STANDOUT)
            else:
                self.window.addstr(i + 4, 4, host.content())

    def display_search_box(self):
        if not self.search_mode:
            return
        txt = '[SEARCH] type something to search | [ENTER] run | [ESC] quit'
        self.window.addstr(self.get_height() - 2, 0, txt)

    def redraw(self, hosts, sidx):
        self.clear()
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
