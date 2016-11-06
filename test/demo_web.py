#! /usr/bin/env python3
# encoding: utf-8
#
# (C) 2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Demo for the web service.
"""

import os
import sys

if __name__ == '__main__':
    import traceback
    sys.path.append(os.path.join(os.path.dirname(__file__), '../device/flash/lib'))
    sys.print_exception = lambda e: traceback.print_tb(e.__traceback__) or print(e)


def main():
    from web.server import Server, HtmlResponse
    from web.app import App
    app = App()

    @app.route('/')
    def index(request):
        return HtmlResponse("Success")

    @app.route('/thing/(.*)')
    def thing(request, t):
        return HtmlResponse("Thing: {!r}".format(t))

    @app.route('/echo', b'POST')
    def echo(request):
        data = request.rfile.read(int(request.headers[b'Content-Length']))
        return HtmlResponse("Echo: {!r}".format(data))

    # apps can be nested with a little code
    app2 = App()

    @app2.route('/')
    def index(request):
        return HtmlResponse("Success 2")

    app2.optimize_routes() # must be called manually

    # delegate everything under a path to an other app, note that the slash is included in the regexp group
    @app.route('/app2(/.*)')
    def subapp(request, path):
        return app2.handle_request(request, path)

    server = Server(app, port=8080)
    server.loop()


if __name__ == '__main__':
    main()
