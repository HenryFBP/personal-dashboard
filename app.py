#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, timeout
from threading import TIMEOUT_MAX
from typing import List
import py_cui
import json
import threading
import time
import os
import shutil
import random
import datetime

from py_cui.widgets import Widget

CONFIG_FILE = ['config.jsonc', 'config.example.jsonc']

QUITWORDS = [
    'Quit?',
    'Leave?',
    'Skedaddle?',
    'Scram?',
    'Turn tail?',
    'Make like a tree?',
    'Run away?',
]


class TCPQueryWidget():

    @staticmethod
    def from_ip_data(data: dict, *args, **kwargs):

        ip = data['ip']
        name = data['name']
        port = data['port']

        timeout = data['timeout']
        queryInterval = data.get('queryInterval', 3)

        return TCPQueryWidget(
            ip, name, port, timeout, queryInterval,
            *args, **kwargs)

    STATUS_FSTRING = "({}s) {}: [ {} ]"
    STATUS_FSTRING_UNKNOWN = STATUS_FSTRING.format(
        "{}", "???.???.???.???", "?")

    def __init__(self, ip: str, name: str, port: int, timeout: int, queryInterval: int,
                 root: py_cui.PyCUI,
                 row: int = 0, col: int = 0,
                 col_span: int = 1, row_span: int = 1,
                 log_fn=lambda *args, **kwargs: print(*args, **kwargs)) -> None:
        self.ip = ip
        self.name = name
        self.port = port
        self.timeout = timeout
        self.queryInterval = queryInterval
        self.up = None
        self.log_fn = log_fn

        self.root = root
        self.row = row
        self.column = col
        self.col_span = col_span
        self.row_span = row_span

        self.block_label_status_name = root.add_block_label(
            self.name,
            self.row, self.column,
            column_span=self.col_span, row_span=self.row_span)

        self.label_status = root.add_label(
            self.status_unknown(),
            self.row, self.column,
            column_span=self.col_span, row_span=self.row_span)

        self.label_status.add_text_color_rule(
            '\\+', py_cui.GREEN_ON_BLACK, 'contains')
        self.label_status.add_text_color_rule(
            'x', py_cui.RED_ON_BLACK, 'contains')

    def status_unknown(self) -> str:
        return self.STATUS_FSTRING_UNKNOWN.format(self.timeout)

    def status(self) -> str:
        if self.up == None:
            return self.STATUS_FSTRING.format(self.timeout, self.ip, " ? ")

        if self.up == True:
            return self.STATUS_FSTRING.format(self.timeout, self.ip, " + ")

        if self.up == False:
            return self.STATUS_FSTRING.format(self.timeout, self.ip, " x ")

    def __str__(self) -> str:
        return self.status()

    def refresh_status(self) -> bool:
        """Determine if I'm up or not. Also update graphical status."""
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(self.timeout)

        try:
            s.connect((self.ip, self.port))
            s.close()
            self.up = True
        except Exception as e:  # Must be generic as socket exception class does not inherit from BaseException... why?!
            self.up = False

        self.label_status.set_title(self.status())

        return self.up

    def blocking_update_label_status(self):
        while True:
            time.sleep(self.queryInterval)

            if self.refresh_status():
                self.log_fn("socket conn for {} succeeded".format(self.name))
            else:
                self.log_fn("socket conn for {} failed".format(self.name))

    def masked_ip(self) -> str:
        return self.ip.split('.')[-1]


def below_widget(w: Widget) -> int:
    return w.get_grid_cell()[0]+1


def above_widget(w: Widget) -> int:
    return w.get_grid_cell()[0]+1


def left_of_widget(w: Widget) -> int:
    return w.get_grid_cell()[1]-1


def right_of_widget(w: Widget) -> int:
    return w.get_grid_cell()[1]+1


def try_connect_ip_port(ip, port, timeout=5) -> bool:
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(timeout)

    try:
        s.connect((ip, port))
        s.close()
        return True
    except Exception as e:  # Must be generic as socket exception class does not inherit from BaseException... why?!
        return False


if __name__ == "__main__":

    if not os.path.exists(CONFIG_FILE[0]):
        CONFIG_FILE[0] = CONFIG_FILE[1]

    with open(CONFIG_FILE[0], 'r') as f:
        JSON_DATA = json.load(f)

    root = py_cui.PyCUI(24, 16)
    root.set_refresh_timeout(1)

    # tcpQueryWidget = TCPQueryWidget.from_ip_data(JSON_DATA['tcp_monitoring'][0],
    #                                              root=root, row=0, col=0, col_span=3, row_span=1)

    tcpQueryWidgets: List[TCPQueryWidget] = []

    row = 0
    col = 0
    col_span = 3
    row_span = 1
    for ip_data in JSON_DATA['tcp_monitoring']:

        tcpQueryWidgets.append(
            TCPQueryWidget.from_ip_data(
                ip_data, root=root, row=row, col=col, col_span=col_span, row_span=row_span))

        row += 1

    button = root.add_button(
        'Quit',
        0, 14,
        column_span=2, row_span=2,
        command=lambda: root.stop())

    text_block_log = root.add_text_block(
        'Log',
        18, 0,
        column_span=8, row_span=6)
    text_block_log.set_selectable(False)

    def printl(s, end='\n',
               timestampfn=lambda: "{}: ".format(datetime.datetime.now().strftime("%H:%M:%S"))):
        text_block_log.set_text(timestampfn()+s+end+text_block_log.get())

    for tcpQueryWidget in tcpQueryWidgets:
        tcpQueryWidget.log_fn = printl

        # TODO store these threads...
        labelStatusThread = threading.Thread(
            target=tcpQueryWidget.blocking_update_label_status)
        labelStatusThread.daemon = True
        labelStatusThread.start()

    cuiThread = threading.Thread(target=lambda: root.start())
    cuiThread.daemon = True
    cuiThread.start()

    while(not root._stopped):  # Main update loop
        # printl("sleepin for 1s...")
        button.set_title(random.choice(QUITWORDS))
        # printl(button.get_title())
        time.sleep(1)
