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


def open_tmux_window(session, title):
    execute_cmd("tmux new-window -n %s &" % title)


def open_ssh_in_tmux(session, host):
    ssh_cmd = "ssh %s@%s -p %s" % (config.username, host, config.port)
    title = '%s@%s' % (config.username, host)

    cmd = "tmux new-window -n %s '%s ;read'" % (title, ssh_cmd)
    execute_cmd(cmd)


def open_ssh_in_tmux_and_record(host):
    now = datetime.datetime.now()
    log_dst = "../asciinema_logs/%s-%s_%s_%s_%s_%s_%s_%s.log" % (
    config.username, host, now.year, now.month, now.day, now.hour, now.minute, now.second)

    ascii_cmd = "asciinema rec -c 'ssh %s@%s -p %s' %s" % (config.username, host, config.port, log_dst)
    title = '%s@%s' % (config.username, host)

    cmd = "tmux new-window -n %s \"%s ;read\"" % (title, ascii_cmd)
    execute_cmd(cmd)


def start_command_executor(bastion):
    while True:
        if len(bastion.cmds) > 0:
            cmd = bastion.cmds.pop(0)
            os.system(cmd)


class Picker(object):
    def __init__(self):
        self.total_lines = len(config.hosts)
        self.selected_line = 0
        self.change_viewport = False

    def lines(self):
        return config.hosts

    def current(self):
        return self.lines()[self.selected_line]

    def move_down(self):
        self.selected_line = (self.selected_line + 1) % self.total_lines

    def move_up(self):
        self.selected_line = (self.selected_line - 1) % self.total_lines

    def select(self):
        pass

    def display_hosts(self, screen):
        screen.addstr(2, 4, 'Hosts:')
        hosts = self.lines()
        for i in range(len(self.lines())):
            if i == self.selected_line:
                screen.addstr(i + 4, 4, hosts[i], curses.A_STANDOUT)
            else:
                screen.addstr(i + 4, 4, hosts[i])

    def redraw(self, screen):
        screen.clear()
        self.display_hosts(screen)
        screen.refresh()


class Bastion(object):
    def __init__(self, picker, screen):
        self.picker = picker
        self.screen = screen
        self.cmds = []

    def start(self):
        picker.display_hosts(screen)

        # thread.start_new_thread(start_command_executor, (self,))
        self.start_event_loop()

    def post_command(self, cmd):
        self.cmds.append(cmd)

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

    curses.noecho()
    curses.cbreak()
    screen.keypad(1)

    Bastion(picker, screen).start()
