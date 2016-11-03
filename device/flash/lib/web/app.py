import re

class App(object):
    def __init__(self):
        self.routes = {}

    def handle_request(self, request, path):
        for priority, _, regexp, function in self.routes[request.method]:
            m = regexp.match(path)
            # collect regexp groups to pass as args
            if m is not None:
                args = []
                try:
                    for i in range(1, 10):
                        args.append(m.group(i))
                except IndexError:
                    pass
                #~ print(args)
                return function(request, *args)
        else:
            request.send_error(404)

    def optimize_routes(self):
        # must sort handlers to get best matches first
        for handlers in self.routes.values():
            handlers.sort()
            handlers.reverse()
        #~ print(self.routes)

    def add_route(self, verb, path, function):
        # default priority is number of slashes -> longer matches preferred
        priority = path.count('/')
        if not path.endswith('$'):
            path = path + '$'
        self.routes.setdefault(verb, []).append((priority, path, re.compile(path), function))
        return function

    # meant to be used as decorator
    def route(self, path, method=b'GET'):
        return lambda fn: self.add_route(method, path, fn)

