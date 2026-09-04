"""
Web Frontend Launcher for Face Identification & Blockchain Verification Pipeline.
Starts a lightweight local HTTP server and opens index.html in your default web browser.
"""
import os
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


def main():
    os.chdir(DIRECTORY)
    index_file = os.path.join(DIRECTORY, "index.html")

    if not os.path.exists(index_file):
        print(f"[ERROR] Frontend file index.html not found in {DIRECTORY}")
        sys.exit(1)

    url = f"http://localhost:{PORT}/index.html"
    print("=" * 65)
    print("  CYBERSIGHT // FACE ID & BLOCKCHAIN VERIFICATION FRONTEND")
    print("=" * 65)
    print(f"  Local Web UI Server running at: {url}")
    print(f"  Serving files from:            {DIRECTORY}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 65)

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        server = HTTPServer(("localhost", PORT), CustomHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Frontend server stopped.")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")


if __name__ == "__main__":
    main()
