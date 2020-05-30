import socket

def app(environ, start_response):

        with open('custom_message.txt') as file:
            contents = "".join(file.readlines())

        data = bytes(contents, 'utf-8')

        start_response("200 OK", [
            ("Content-Type", "text/plain"),
            ("Content-Length", str(len(data)))
        ])
        return iter([data])


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, app)
    srv.serve_forever()
