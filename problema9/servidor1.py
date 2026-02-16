#BACKEND

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import requests
import json
import sys

LOAD_BALANCER = "http://localhost:8000/register"
PORT = int(sys.argv[1])

shared_data = {"contador": 0}
other_servers = []

class BackendHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        elif self.path == "/data":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(shared_data).encode())

        elif self.path == "/increment":
            shared_data["contador"] += 1
            sync_data()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(shared_data).encode())

    def log_message(self, format, *args):
        return


def register():
    requests.post(LOAD_BALANCER, json={"url": f"http://localhost:{PORT}"})


def sync_data():
    for server in other_servers:
        try:
            requests.post(f"{server}/sync", json=shared_data)
        except:
            pass


def run():
    register()
    server = HTTPServer(("localhost", PORT), BackendHandler)
    print(f"Backend corriendo en puerto {PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
