#!/usr/bin/python3

from socket import socket, AF_INET, SOCK_STREAM
import py_cui
import json

with open('config.json', 'r') as f:
    data = json.load(f)

IP = data['ip']
PORT = data['port']


s = socket(AF_INET, SOCK_STREAM)
s.connect((IP, PORT))  # The address of the TCP server listening


print(f"Connected to {IP[-3:]}:{PORT}")

if __name__ == "__main__":
    root = py_cui.PyCUI(7, 9)

    label = root.add_label('Label Text', 0, 0)
    button = root.add_button(
        'Button Text', 1, 2, column_span=2, command=lambda: print("click"))

    root.start()
