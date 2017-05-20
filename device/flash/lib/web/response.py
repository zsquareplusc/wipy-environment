#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
import json
import sys
import os
from . import umimetypes


class Response(object):

    def __init__(self, status):
        self.status = status
        self.headers = {    # mapping of header name -> value
            b'Cache-Control': b'no-cache,no-store,must-revalidate',
        }

    def emit_content(self, server):
        pass

    def emit(self, server):
        server.send_response(self.status)
        for header_name, header_value in self.headers.items():
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
            if not chunk:
                break
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
        mime_type = umimetypes.type_map.get(fileext, b'application/octet-stream')
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
