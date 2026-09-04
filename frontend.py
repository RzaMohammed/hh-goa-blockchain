"""
Web Frontend Launcher for Face Identification & Blockchain Verification Pipeline.
Serves the React frontend bundle and opens the browser.
"""
import os
import subprocess
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
REACT_DIST_DIR = os.path.join(FRONTEND_DIR, "dist")


def ensure_react_built():
    """Ensure the React application is built into frontend/dist."""
    index_file = os.path.join(REACT_DIST_DIR, "index.html")
    if not os.path.exists(index_file):
        print("[INFO] React distribution not found. Building with Vite...")
        try:
            subprocess.run(["npm", "--prefix", "frontend", "run", "build"], check=True, shell=True)
            print("[INFO] React build successful.")
        except Exception as e:
            print(f"[WARN] Failed to build React app: {e}")


class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=REACT_DIST_DIR, **kwargs)


def main():
    ensure_react_built()

    if not os.path.exists(os.path.join(REACT_DIST_DIR, "index.html")):
        print(f"[ERROR] Could not find built React assets in {REACT_DIST_DIR}")
        print("        Please run: npm --prefix frontend run build")
        sys.exit(1)

    os.chdir(REACT_DIST_DIR)
    url = f"http://localhost:{PORT}/"

    print("=" * 65)
    print("  CYBERSIGHT // FACE ID & BLOCKCHAIN VERIFICATION DASHBOARD")
    print("=" * 65)
    print("  App Type:                      React + Vite Production Bundle")
    print(f"  Local Web UI Server running at: {url}")
    print(f"  Serving directory:             {REACT_DIST_DIR}")
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
