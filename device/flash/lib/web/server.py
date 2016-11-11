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
gc.collect()

class Response(object):

    def __init__(self, status):
        self.status = status
        self.headers = {    # mapping of header name -> value
            b'Cache-Control': b'no-cache,no-store,must-revalidate',
            b'Connection': b'close',
            #~ b'Connection': b'keep-alive',
        }

    def emit_content(self, server):
        pass

    def emit(self, server):
        server.send_response(self.status)
        for header_name, header_value  in self.headers.items():
            if not isinstance(header_value, (bytes, bytearray, memoryview)):
                header_value = str(header_value).encode('utf-8')
            server.send_header(header_name, header_value)
        server.end_headers()
        self.emit_content(server)


class SimpleResponse(Response):

    def __init__(self, content, content_type, status=b'200 OK'):
        super().__init__(status)
        if isinstance(content, (bytes, bytearray, memoryview)):
            self.content = content
        else:
            self.content = str(content).encode('utf-8')
        self.headers[b'Content-Encoding'] = b'utf-8'
        self.headers[b'Content-Type'] = content_type
        self.headers[b'Content-Length'] = len(self.content)

    def emit_content(self, server):
        server.wfile.write(self.content)


class StreamResponse(Response):

    def __init__(self, stream, length, content_type, status=b'200 OK'):
        super().__init__(status)
        self.stream = stream
        self.headers[b'Content-Type'] = content_type
        self.headers[b'Content-Length'] = length

    def emit_content(self, server):
        while True:
            chunk = self.stream.read(256)
            if not chunk: break
            server.wfile.write(chunk)
        try:
            self.stream.close()
        except:
            sys.print_exception()
        self.stream = None


class RedirectResponse(Response):
    def __init__(self, url):
        super().__init__(b'302 Moved Temporarily')
        self.headers[b'Location'] = url.encode('utf-8')  # XXX encoding of url


class HtmlResponse(SimpleResponse):
    def __init__(self, content, status=b'200 OK'):
        super().__init__(content, b'text/html', status)


class JsonResponse(SimpleResponse):
    def __init__(self, obj):
        super().__init__(json.dumps(obj), b'application/json')


def FileResponse(path):
    try:
        s = os.stat(path)
    except OSError:
        return STATUS404
    else:
        fileext = path.split('.')[-1]
        mime_type =  umimetypes.type_map.get(fileext, b'application/octet-stream')
        response = StreamResponse(open(path, 'rb'), s[6], mime_type)  # stream, len
        response.headers[b'Cache-Control'] = b'max-age: 30'
        return response


class ErrorResponse(HtmlResponse):
    def __init__(self, status):
        super().__init__(b'<div style="font-size:60">', status)
        self.headers[b'Content-Length'] = len(self.content) + len(self.status)

    def emit_content(self, server):
        server.wfile.write(self.content)
        server.wfile.write(self.status)


STATUS200 = Response(b'200 OK')
STATUS204 = Response(b'204 No Content')
STATUS500 = ErrorResponse(b'500 Internal Server Error')
STATUS404 = ErrorResponse(b'404 Not Found')



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
                        response = STATUS200
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

