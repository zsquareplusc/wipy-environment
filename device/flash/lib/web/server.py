import socket
import json
import sys
import os
from . import umimetypes

class Response(object):
    CONTENT_TYPE = 'text/plain'
    CACHE_CONTROL = {
        'Cache-Control': 'no-store, must-revalidate',
        'Expires': 'Fri, 01 Jan 1990 00:00:00 GMT',
        'Pragma': 'no-cache',
    }
    CONTENT_LENGTH = None

    def __init__(self, content=None, stream=None, status=200):
        self.content = content
        self.stream = stream
        self.status = status
        self.headers = {    # mapping of header name -> value
            'Content-Type': self.CONTENT_TYPE,
            'Connection': 'close',
        }
        self.headers.update(self.CACHE_CONTROL)
        if self.CONTENT_LENGTH and self.content is not None:
            length = self.CONTENT_LENGTH
            if length is None:
                length = len(self.content)
            self.headers["Content-Length"] = length

    def emit_headers(self, server):
        server.send_response(self.status)
        for header_name, header_value  in self.headers.items():
            server.send_header(header_name, header_value)
        server.end_headers()

    def emit_content(self, server):
        if self.stream is not None:
            while True:
                chunk = self.stream.read(1024)
                if not chunk: break
                server.wfile.write(chunk)
            try:
                self.stream.close()
            except:
                logging.exception('close failed in Response')
            self.stream = None
        else:
            server.wfile.write(self.content.encode('utf-8'))

    def emit(self, server):
        self.emit_headers(server)
        self.emit_content(server)


class HtmlResponse(Response):
    CONTENT_TYPE = 'text/html'


class JsonResponse(Response):
    CONTENT_TYPE = 'application/json'

    def __init__(self, obj):
        Response.__init__(self, json.dumps(obj))


class FileResponse(Response):
    def __init__(self, path):
        fileext = path.split('.')[-1]
        self.CONTENT_TYPE = mimetypes.type_map.get(fileext, 'application/octet-stream')
        stats = os.stat(path)
        self.CONTENT_LENGTH = len(stat.sz_size)
        super().__init__(stream=open(path, 'rb'))


errormessages = {
    200: 'OK',
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'Not Found',
    #~ 405: 'Method Not Allowed'
    #~ 414: 'Request-URI Too Long',
    500: 'Internal Server Error',
}

error_page = '<html><body>Error: {e}<br/>Message: {m}</body></html>'


class Request(object):

    def __init__(self, rfile, wfile, method, path):
        self.rfile = rfile
        self.wfile = wfile
        self.method = method
        self.path = path
        self.headers = {}
        self._read_headers()

    def _read_headers(self):
        while True:
            line = self.rfile.readline().rstrip()
            if not line: break
            key, value = line.split(b':', 1)
            # XXX urldecode key, value, multiline values
            self.parse_header(key, value)

    def raw(self):
        return self.rfile.read(int(self.headers[b'Content-Length']))

    def text(self):
        return self.raw().decode(self.headers[b'Content-Encoding'])

    def json(self):
        return json.loads(self.text())

    def parse_header(self, key, value):
        # XXX store the interesting ones
        if key in [b'Content-Length', b'Content-Type']:
            self.headers[key] = value
        print(key, value)

    def send_error(self, errorcode, message=None):
        self.send_response(errorcode)
        self.end_headers()
        self.wfile.write(error_page.format(e=errorcode, m=message).encode('utf-8'))

    def send_response(self, errorcode, message=None):
        #~ print(errorcode)
        if message is None:
            message = errormessages.get(errorcode, '')
        self.wfile.write('HTTP/1.0 {} {}\r\n'.format(errorcode, message).encode('utf-8'))

    def send_header(self, key, value):
        self.wfile.write('{}: {}\r\n'.format(key, value).encode('utf-8'))

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
        self.listening_socket.listen(5)

    def wait_for_client(self):
        client_socket, client_addr = self.listening_socket.accept()
        #~ print(client_addr)
        rfile = client_socket.makefile('rb')
        commandline = rfile.readline()
        verb, path, _ = commandline.strip().split(None, 2)
        #~ print(verb, path, _)
        request = Request(rfile, client_socket.makefile('wb'), verb, path)
        try:
            response = self.app.handle_request(request, path.decode('utf-8')) # XXX decode %nn first
            if response is not None:
                response.emit(request)
        except Exception as e:
            sys.print_exception(e)
            request.send_error(500)
        client_socket.close()

    def loop(self):
        self.app.optimize_routes()
        while True:
            try:
                self.wait_for_client()
            except Exception as e:
                raise
                #~ sys.print_exception(e)

