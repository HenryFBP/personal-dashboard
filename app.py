#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM
import py_cui
import json
import threading
import time
import os
import random

QUITWORDS=[
    'Quit?',
    'Leave?',
    'Skedaddle?',
    'Scram?',
]

with open('config.json', 'r') as f:
    data = json.load(f)

IP = data['ip']
MASKED_IP = data['ip'].split('.')[-1]
PORT = data['port']


s = socket(AF_INET, SOCK_STREAM)
s.connect((IP, PORT))  # The address of the TCP server listening


print(f"Connected to ?.?.?.{MASKED_IP}:{PORT}")

if __name__ == "__main__":
    root = py_cui.PyCUI(16, 16)

    label = root.add_label('Label Text', 0, 0)
    button = root.add_button(
        'Quit', 0, 12, 
        column_span=3,row_span=2,
        command=lambda: exit(0))

    text_block_log = root.add_text_block(
        'Log', 3, 3, column_span=3, row_span=6)

    def printl(s, end='\n'):
        text_block_log.set_text(s+end+text_block_log.get())

    root.set_refresh_timeout(1)

    cuiThread = threading.Thread(target=lambda: root.start())
    cuiThread.daemon = True
    cuiThread.start()

    while(True):
        printl("sleepin for 1s...")
        button.set_title(random.choice(QUITWORDS))
        printl(button.get_title())
        time.sleep(1)
