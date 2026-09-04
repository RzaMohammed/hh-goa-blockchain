"""
Web Frontend Launcher for Face Identification & Blockchain Verification Pipeline.
Serves the React frontend (or static fallback) and opens the browser.
"""
import os
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REACT_DIST_DIR = os.path.join(BASE_DIR, "frontend", "dist")

# Prefer compiled React distribution if built, else serve root directory
SERVE_DIR = REACT_DIST_DIR if os.path.exists(os.path.join(REACT_DIST_DIR, "index.html")) else BASE_DIR


class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_DIR, **kwargs)


def main():
    os.chdir(SERVE_DIR)
    url = f"http://localhost:{PORT}/"
    app_type = "React + Vite Production Bundle" if SERVE_DIR == REACT_DIST_DIR else "Static Dashboard"

    print("=" * 65)
    print("  CYBERSIGHT // FACE ID & BLOCKCHAIN VERIFICATION DASHBOARD")
    print("=" * 65)
    print(f"  App Type:                      {app_type}")
    print(f"  Local Web UI Server running at: {url}")
    print(f"  Serving directory:             {SERVE_DIR}")
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
