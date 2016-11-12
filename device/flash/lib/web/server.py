#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
import socket
import json
import sys
import os
import gc
from . import umimetypes, url
from .response import STATUS204, STATUS500
gc.collect()



class Request(object):

    def __init__(self, rfile, wfile, method=None, path=None):
        self.rfile = rfile
        self.wfile = wfile
        self.method = method
        self.path = path
        self._read = False
        self.headers = {}
        if method:
            self._read_headers()

    def _read_headers(self):
        self.headers.clear()
        self._read = False
        while True:
            line = self.rfile.readline().rstrip()
            if not line: break
            key, value = line.split(b':', 1)
            # XXX urldecode key, value, multiline values
            self.parse_header(key, value)

    def raw(self):
        self._read = True
        return self.rfile.read(int(self.headers.get(b'Content-Length', b'0')))

    def text(self):
        return self.raw().decode(self.headers.get(b'Content-Encoding', 'utf-8'))

    def json(self):
        return json.loads(self.text())

    def parse_header(self, key, value):
        # XXX store the interesting ones
        if key in [b'Content-Length', b'Content-Type', b'Content-Encoding']:
            self.headers[key] = value
        #~ print(key, value)

    def send_error(self, status):
        self.send_response(status)
        self.end_headers()
        self.wfile.write(status)

    def send_response(self, status):
        if not self._read and b'Content-Length' in self.headers:
            self.raw()  # read and drop data  XXX do it in small chunks
        self.wfile.write(b'HTTP/1.1 ')
        self.wfile.write(status)
        self.wfile.write(b'\r\n')

    def send_header(self, key, value):
        self.wfile.write(key)
        self.wfile.write(b': ')
        self.wfile.write(value)
        self.wfile.write(b'\r\n')

    def end_headers(self):
        self.wfile.write(b'\r\n')


class Server(object):
    def __init__(self, app, port=80):
        self.app = app

        self.listening_socket = socket.socket()

        # Binding to all interfaces - server will be accessible to other hosts!
        ai = socket.getaddrinfo("0.0.0.0", port)
        print("Bind address info:", ai)
        addr = ai[0][-1]

        try:
            self.listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
            print("setsockopt not supported")
        self.listening_socket.bind(addr)
        self.listening_socket.listen(1)

    def wait_for_client(self):
        client_socket, addr = self.listening_socket.accept()
        try:
            #~ print(client_addr)
            rfile = client_socket.makefile('rb')
            request = Request(rfile, client_socket.makefile('wb'))
            while True:
                gc.collect()
                print("ready")
                commandline = rfile.readline()
                print(addr, commandline)
                request.method, request.path, _ = commandline.strip().split(None, 2)
                request._read_headers()
                try:
                    response = self.app.handle_request(request, url.decode(request.path))
                    if response is None:
                        response = STATUS204
                    response.emit(request)
                    print(response.status)
                except Exception as e:
                    sys.print_exception(e)
                    STATUS500.emit(request)
                    print(STATUS500.status)
                    break
                #~ gc.collect()
                if response.headers.get(b'Connection') != b'keep-alive':
                    break
        finally:
            print("terminate")
            gc.collect()
            client_socket.close()

    def loop(self):
        self.app.optimize_routes()
        gc.collect()
        while True:
            try:
                self.wait_for_client()
                #~ socket.print_pcbs()
                #~ gc.collect()
            except Exception as e:
                #~ raise
                sys.print_exception(e)

