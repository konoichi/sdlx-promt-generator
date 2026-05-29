"""
Einstiegspunkt der Anwendung.
Starten mit: python run.py
"""

import os
from app.web.app import app

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    print(f"\n SDXL Prompt Generator")
    print(f" ─────────────────────────────────")
    print(f" http://{host}:{port}")
    print(f" Debug: {debug}")
    print(f" Daten: {os.getenv('DATA_DIR', 'data')}/")
    print(f" ─────────────────────────────────\n")

    app.run(host=host, port=port, debug=debug)
