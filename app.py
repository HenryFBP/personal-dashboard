#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, timeout
from threading import TIMEOUT_MAX
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
    def from_ip_data(data: dict):
        return TCPQueryWidget(
            ip=data['ip'], name=data['name'], port=data['port'], timeout=data['timeout'])

    STATUS_FSTRING = "({}s) {}: [ {} ]"
    STATUS_FSTRING_UNKNOWN = STATUS_FSTRING.format("{}","???.???.???.???", "?")

    def __init__(self, ip, name, port, timeout) -> None:
        self.ip = ip
        self.name = name
        self.port = port
        self.timeout = timeout
        self.up = None
    
    def status_unknown(self)->str:
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

    def is_up(self) -> bool:
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(self.timeout)

        try:
            s.connect((self.ip, self.port))
            s.close()
            self.up = True
        except Exception as e:  # Must be generic as socket exception class does not inherit from BaseException... why?!
            self.up = False

        return self.up

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

    IP_DATA = JSON_DATA['tcp_monitoring'][0]

    tcpQueryWidget = TCPQueryWidget.from_ip_data(IP_DATA)

    root = py_cui.PyCUI(24, 16)
    root.set_refresh_timeout(1)

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

    label_status_name = root.add_block_label(
        tcpQueryWidget.name,
        1, 0,
        column_span=3)

    label_status = root.add_label(
        tcpQueryWidget.status_unknown(),
        1, 0,
        column_span=3)
    label_status.add_text_color_rule('\\+', py_cui.GREEN_ON_BLACK, 'contains')
    label_status.add_text_color_rule('x', py_cui.RED_ON_BLACK, 'contains')

    def update_label_status(sleeptime=5):
        while True:
            time.sleep(sleeptime)

            if tcpQueryWidget.is_up():
                printl("socket conn for {} succeeded".format(tcpQueryWidget.name))
            else:
                printl("socket conn for {} failed".format(tcpQueryWidget.name))

            label_status.set_title(str(tcpQueryWidget))

    labelStatusThread = threading.Thread(target=lambda: update_label_status())
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
