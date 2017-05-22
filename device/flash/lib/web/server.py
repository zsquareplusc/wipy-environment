#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
import socket
import sys
import gc
import micropython
from .connection import Connection
import ulog
gc.collect()

log = ulog.Logger('HTTPD: ')


class Server(object):
    def __init__(self, app, port=80):
        self.app = app

        self.listening_socket = socket.socket()

        # Binding to all interfaces - server will be accessible to other hosts!
        ai = socket.getaddrinfo('0.0.0.0', port)
        log.info('Bind address info: {}'.format(ai))
        addr = ai[0][-1]

        try:
            self.listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
            log.warn('setsockopt not supported')
        self.listening_socket.bind(addr)
        self.listening_socket.listen(1)

    def wait_for_client(self):
        client_socket, client_addr = self.listening_socket.accept()
        #~ client_socket.settimeout(5)
        try:
            connection = Connection(
                '{}:{}'.format(*client_addr).encode('utf-8'),
                client_socket.makefile('rb'),
                client_socket.makefile('wb'),
                #~ keep=True)
                keep=False)
            connection.do_request(self.app)
        finally:
            #~ print("terminate")
            gc.collect()
            client_socket.close()

    def loop(self):
        self.app.optimize_routes()
        gc.collect()
        micropython.mem_info(1)
        while True:
            try:
                self.wait_for_client()
                #~ socket.print_pcbs()
                #~ gc.collect()
            except OSError as e:
                sys.print_exception(e)
                #~ if 'ENOMEM' in str(e):
                    #~ micropython.mem_info(1)
                    #~ socket.print_pcbs()
                    #~ machine.reset()
            except Exception as e:
                #~ raise
                sys.print_exception(e)
