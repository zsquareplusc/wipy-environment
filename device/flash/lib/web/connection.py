#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
import sys
import gc
from . import url
from .response import STATUS204, STATUS500
gc.collect()
from .request import Request
gc.collect()


class Connection(object):
    def __init__(self, name, rfile, wfile, keep=False):
        self.name = name
        self.rfile = rfile
        self.wfile = wfile
        self._keep = keep

    def send_response(self, status):
        self.wfile.write(b'HTTP/1.1 ')
        self.wfile.write(status)
        self.wfile.write(b'\r\n')

    def send_header(self, key, value):
        self.wfile.write(key)
        self.wfile.write(b': ')
        self.wfile.write(value)
        self.wfile.write(b'\r\n')

    def end_headers(self):
        self.send_header(b'Server', b'femtoweb')
        self.send_header(b'Connection', b'keep-alive' if self._keep else b'close')
        self.wfile.write(b'\r\n')

    def do_request(self, app):
        request = Request(self)
        while True:
            gc.collect()
            #~ print("ready")
            try:
                request._read_request()
                response = app.handle_request(request, url.decode(request.path))
                if response is None:
                    response = STATUS204
                request.cleanup()
            except Exception as e:
                sys.print_exception(e)
                response = STATUS500
                self._keep = False
            response.emit(self)
            for s in (self.name, b': ', request.method, b' ', request.path, b' -> ', response.status, b'\n'):
                sys.stderr.buffer.write(s)
            #~ gc.collect()
            if not self._keep:
                break
