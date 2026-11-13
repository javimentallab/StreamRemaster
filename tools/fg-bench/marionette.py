"""A minimal Marionette client for driving Firefox-family browsers in the benches."""
import json
import socket
import time


class Marionette:
    def __init__(self, port):
        deadline = time.time() + 30
        while True:
            try:
                self.sock = socket.create_connection(("127.0.0.1", port), timeout=5)
                break
            except OSError:
                if time.time() > deadline:
                    raise
                time.sleep(0.5)
        self.sock.settimeout(90)
        self.id = 0
        self.read()

    def read(self):
        size = b""
        while True:
            c = self.sock.recv(1)
            if not c:
                raise ConnectionError("Marionette closed the connection")
            if c == b":":
                break
            size += c
        left = int(size)
        data = b""
        while left:
            part = self.sock.recv(left)
            if not part:
                raise ConnectionError("Marionette closed the connection")
            data += part
            left -= len(part)
        return json.loads(data)

    def cmd(self, name, params=None):
        self.id += 1
        data = json.dumps([0, self.id, name, params or {}]).encode()
        self.sock.sendall(str(len(data)).encode() + b":" + data)
        while True:
            reply = self.read()
            if reply[0] == 1 and reply[1] == self.id:
                if reply[2]:
                    raise RuntimeError(f"{name}: {reply[2]}")
                return reply[3]

    def js(self, script, sandbox="default"):
        return self.cmd("WebDriver:ExecuteScript", {"script": script, "args": [], "sandbox": sandbox}).get("value")
