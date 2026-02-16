#LOAD BALANCER

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import requests
import json
import time

backends = []
current = 0

class LoadBalancerHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == "/register":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))
            backends.append(data["url"])
            print("Backend registrado:", data["url"])
            self.send_response(200)
            self.end_headers()

    def do_GET(self):
        global current

        if not backends:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b"No backends available")
            return

        backend = backends[current % len(backends)]
        current += 1

        try:
            response = requests.get(f"{backend}/data")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(response.content)
        except:
            self.send_response(500)
            self.end_headers()

    def log_message(self, format, *args):
        return


def health_check():
    while True:
        time.sleep(5)
        for backend in backends[:]:
            try:
                requests.get(f"{backend}/health", timeout=2)
            except:
                print("Backend caído:", backend)
                backends.remove(backend)


def run():
    threading.Thread(target=health_check, daemon=True).start()
    server = HTTPServer(("localhost", 8000), LoadBalancerHandler)
    print("Load Balancer en puerto 8000")
    server.serve_forever()


if __name__ == "__main__":
    run()
