#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
import socket
import sys
import os
import gc
from . import url
from .response import STATUS204, STATUS500
from .request import Request
gc.collect()



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
            response.emit(self)
            for s in (self.name, b': ', request.method, b' ', request.path, b' -> ', response.status, b'\n'):
                sys.stderr.buffer.write(s)
            #~ gc.collect()
            if response is STATUS500 or self.headers.get(b'Connection') != b'keep-alive':
                break


class Server(object):
    def __init__(self, app, port=80):
        self.app = app

        self.listening_socket = socket.socket()

        # Binding to all interfaces - server will be accessible to other hosts!
        ai = socket.getaddrinfo('0.0.0.0', port)
        print('Bind address info:', ai)
        addr = ai[0][-1]

        try:
            self.listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
            print('setsockopt not supported')
        self.listening_socket.bind(addr)
        self.listening_socket.listen(1)

    def wait_for_client(self):
        client_socket, client_addr = self.listening_socket.accept()
        try:
            connection = Connection(
                    '{}:{}'.format(*client_addr).encode('utf-8'),
                client_socket.makefile('rb'),
                client_socket.makefile('wb'))
            connection.do_request(self.app)
        finally:
            #~ print("terminate")
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

