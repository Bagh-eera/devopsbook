import socket
import redis

def app(environ, start_response):

        r = redis.Redis(host="192.167.32.5", password="foobared")
        
        if r.exists("hit_count"):
            hit_count = int(r.get("hit_count"))
        else:
            hit_count = 1
        
        hit_count = hit_count + 1
        r.set("hit_count", hit_count)


        data = bytes("Hello World, this website has been visited {0} times".format(hit_count), 'utf-8')

        start_response("200 OK", [
            ("Content-Type", "text/plain"),
            ("Content-Length", str(len(data)))
        ])
        return iter([data])


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, app)
    srv.serve_forever()
