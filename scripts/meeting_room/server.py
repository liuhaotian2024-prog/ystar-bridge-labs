"""
Y* Bridge Labs — Meeting Room scaffold server.
Serves static files from ./public on localhost:8765.
Future: gov_mcp SSE proxy endpoint at /api/gov.
"""
import http.server
import os
import sys

PORT = 8765
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[meeting-room] {fmt % args}\n")


def main():
    with http.server.HTTPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"[Y* Meeting Room] serving on http://127.0.0.1:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Y* Meeting Room] stopped.")


if __name__ == "__main__":
    main()
