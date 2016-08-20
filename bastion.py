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

    ascii_cmd = "asciinema rec -c '%s' %s" % (host.connect_title(), log_dst)

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

    def display_hosts(self, screen):
        #screen.addstr(2, 4, 'Hosts:')
        for i in range(len(self.hosts)):
            host = self.hosts[i]
            if i == self.selected_index:
                screen.addstr(i + 4, 4, host.content() , curses.A_STANDOUT)
            else:
                screen.addstr(i + 4, 4, host.content())

    def redraw(self, screen):
        screen.clear()
        self.display_hosts(screen)
        screen.refresh()


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


class Bastion(object):
    def __init__(self, picker, screen):
        self.picker = picker
        self.screen = screen

    def start(self):
        picker.display_hosts(screen)
        self.start_event_loop()

    def start_event_loop(self):
        while True:
            key = self.screen.getch()

            if key == 113:  # Quit q
                break

            elif key == curses.KEY_UP:
                self.picker.move_up()
                picker.redraw(self.screen)

            elif key == curses.KEY_DOWN:
                self.picker.move_down()
                picker.redraw(self.screen)

            elif key == 10:  # Press ENTER
                host = picker.current()
                open_ssh_in_tmux_and_record(host)

        curses.endwin()
        kill_tmux_session('bastion')


if __name__ == '__main__':
    screen = curses.initscr()
    screen.border(0)
    picker = Picker()
    picker.load_config()

    curses.noecho()
    curses.cbreak()
    screen.keypad(1)

    Bastion(picker, screen).start()
