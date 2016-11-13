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
        print(self.connection.name, commandline)
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


class Connection(object):
    def __init__(self, name, rfile, wfile):
        self.name = name
        self.rfile = rfile
        self.wfile = wfile
        self.headers = {
            b'Server': b'femtoweb',
            b'Connection': b'close',
            #~ b'Connection': b'keep-alive',
        }

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
        for header_name, header_value in self.headers.items():
            self.send_header(header_name, header_value)
        self.wfile.write(b'\r\n')

    def do_request(self, app):
        request = Request(self)
        while True:
            gc.collect()
            print("ready")
            try:
                request._read_request()
                response = app.handle_request(request, url.decode(request.path))
                if response is None:
                    response = STATUS204
                request.cleanup()
                response.emit(self)
                print(response.status)
            except Exception as e:
                sys.print_exception(e)
                STATUS500.emit(self)
                print(STATUS500.status)
                break
            #~ gc.collect()
            if self.headers.get(b'Connection') != b'keep-alive':
                break


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
        client_socket, client_addr = self.listening_socket.accept()
        try:
            connection = Connection(
                client_addr,
                client_socket.makefile('rb'),
                client_socket.makefile('wb'))
            connection.do_request(self.app)
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

