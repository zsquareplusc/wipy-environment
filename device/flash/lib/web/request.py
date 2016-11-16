#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
import json


class Request(object):

    def __init__(self, connection):
        self.connection = connection
        self.method = None
        self.path = None
        self._read = False
        self.headers = {}

    def _read_headers(self):
        while True:
            line = self.connection.rfile.readline().rstrip()
            if not line: break
            key, value = line.split(b':', 1)
            # XXX urldecode key, value, multiline values
            self.parse_header(key, value)

    def _read_request(self):
        self.headers.clear()
        self._read = False
        commandline = self.connection.rfile.readline()
        #~ print(self.connection.name, commandline)
        self.method, self.path, _ = commandline.strip().split(None, 2)
        self._read_headers()

    def raw(self):
        self._read = True
        return self.connection.rfile.read(int(self.headers.get(b'Content-Length', b'0')))

    def text(self):
        return self.raw().decode(self.headers.get(b'Content-Encoding', 'utf-8'))

    def json(self):
        return json.loads(self.text())

    def parse_header(self, key, value):
        # XXX store the interesting ones, XXX case senitivity
        if key in [b'Content-Length', b'Content-Type', b'Content-Encoding']:
            self.headers[key] = value
        #~ print(key, value)

    def cleanup(self):
        if not self._read and b'Content-Length' in self.headers:
            self.raw()  # read and drop data  XXX do it in small chunks
