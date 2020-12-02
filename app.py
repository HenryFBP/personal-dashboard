#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM, timeout
from threading import TIMEOUT_MAX
import py_cui
import json
import threading
import time
import os
import random
import datetime

from py_cui.widgets import Widget

QUITWORDS = [
    'Quit?',
    'Leave?',
    'Skedaddle?',
    'Scram?',
    'Turn tail?',
    'Make like a tree?',
    'Run away?',
]

with open('config.jsonc', 'r') as f:
    JSON_DATA = json.load(f)

IP_DATA = JSON_DATA['tcp_monitoring'][0]

IP = IP_DATA['ip']
NAME = IP_DATA['name']
MASKED_IP = IP_DATA['ip'].split('.')[-1]
PORT = IP_DATA['port']
TIMEOUT = IP_DATA['timeout']


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

    if try_connect_ip_port(IP, PORT, TIMEOUT):
        print(f"Connected to ?.?.?.{MASKED_IP}:{PORT}")
    else:
        print(f"TIMED OUT trying to connect to ?.?.?.{MASKED_IP}:{PORT}")
        exit()

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
        column_span=4, row_span=6)
    text_block_log.set_selectable(False)

    def printl(s, end='\n',
               timestampfn=lambda: "{}: ".format(datetime.datetime.now().strftime("%H:%M:%S"))):
        text_block_log.set_text(timestampfn()+s+end+text_block_log.get())

    label_status_name = root.add_block_label(
        NAME,
        1, 0,
        column_span=2)

    label_status = root.add_label(
        '??.??.??.??: [ ... ]',
        1, 0,
        column_span=2) 
    label_status.add_text_color_rule('\\+', py_cui.GREEN_ON_BLACK,'contains')
    label_status.add_text_color_rule('x', py_cui.RED_ON_BLACK,'contains')

    def update_label_status(sleeptime=5):
        while True:
            time.sleep(sleeptime)
            s = "{}: [ {} ]".format(IP, "{}")
            if try_connect_ip_port(IP, PORT, TIMEOUT):
                printl("socket conn succeeded")
                s = s.format(" + ")
            else:
                printl("socket conn failed")
                s = s.format(" x ")
            label_status.set_title(s)

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
