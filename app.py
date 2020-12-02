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

QUITWORDS = [
    'Quit?',
    'Leave?',
    'Skedaddle?',
    'Scram?',
]

with open('config.jsonc', 'r') as f:
    JSON_DATA = json.load(f)

IP_DATA = JSON_DATA['tcp_monitoring'][0]

IP = IP_DATA['ip']
MASKED_IP = IP_DATA['ip'].split('.')[-1]
PORT = IP_DATA['port']
TIMEOUT = IP_DATA['timeout']


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

    root = py_cui.PyCUI(16, 16)

    label = root.add_label('Label Text', 0, 0)
    button = root.add_button(
        'Quit', 0, 14,
        column_span=2, row_span=1,
        command=lambda: root.stop())

    text_block_log = root.add_text_block(
        'Log', 5, 0, column_span=4, row_span=6)

    def printl(s, end='\n',
               timestampfn=lambda: "{}: ".format(datetime.datetime.now().strftime("%H:%M:%S"))):
        text_block_log.set_text(timestampfn()+s+end+text_block_log.get())

    root.set_refresh_timeout(1)

    cuiThread = threading.Thread(target=lambda: root.start())
    cuiThread.daemon = True
    cuiThread.start()

    while(not root._stopped):  # Main update loop
        printl("sleepin for 1s...")
        button.set_title(random.choice(QUITWORDS))
        # printl(button.get_title())
        time.sleep(1)
