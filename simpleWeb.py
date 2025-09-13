from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from collections import defaultdict

#This file is to test dirfinder tool...
#USAGE: python3 simpleWeb.py


RATE_LIMIT = 10
RATE_PERIOD = 5
request_times = defaultdict(list)

class MyHandler(BaseHTTPRequestHandler):
    def rate_limited(self):
        ip = self.client_address[0]
        now = time.time()
        # Remove timestamps older than RATE_PERIOD
        request_times[ip] = [t for t in request_times[ip] if now - t < RATE_PERIOD]
        if len(request_times[ip]) >= RATE_LIMIT:
            return True
        request_times[ip].append(now)
        return False

    def do_GET(self):
        if self.rate_limited():
            self.send_response(429)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Too Many Requests")
            return

        print(">>> do_GET called for", self.path)  # debug
        # redirections
        if self.path == "/old":
            self.send_response(301)
            self.send_header("Location", "/new")  # ou URL absolue
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Redirecting...")
            return

        # 308 Permanent Redirect
        elif self.path == "/try":
            self.send_response(308)
            self.send_header("Location", "/new")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Permanent Redirect (308)")
            return

        # forbidden
        elif self.path == "/admin":
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden")

        # unauthorized
        elif self.path == "/unauth":
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"Unauthorized")

        # method not allowed
        elif self.path == "/notallowed":
            self.send_response(405)
            self.end_headers()
            self.wfile.write(b"Method Not Allowed")

        # bad request
        elif self.path == "/bad":
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad Request")

        # server error
        elif self.path == "/error":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Server Error")

        # service unavailable
        elif self.path == "/unavail":
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b"Service Unavailable")

        # accepted
        elif self.path == "/accepted":
            self.send_response(202)
            self.end_headers()
            self.wfile.write(b"Accepted")

        # created
        elif self.path == "/created":
            self.send_response(201)
            self.end_headers()
            self.wfile.write(b"Created")

        # no content
        elif self.path == "/nocontent":
            self.send_response(204)
            self.end_headers()
            # No body for 204

        # page valide
        elif self.path == "/login":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Login page")

        elif self.path == "/new":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"New page after redirect")

        # not found
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

if __name__ == "__main__":
    port = 8000
    print(f"Server running at http://localhost:{port}")
    server = HTTPServer(("0.0.0.0", port), MyHandler)
    server.serve_forever()
