"""
FXMind Backend Server Startup Script.

Run from the backend/ directory:
    python start.py

Or from project root:
    python backend/start.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Fix Windows console encoding (cp1252 can't render emoji used in signal reasons)
os.environ.setdefault("PYTHONUTF8", "1")
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure backend/ is on the Python path when running from project root
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.chdir(backend_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(backend_dir / "app"), str(backend_dir / "ml")],
        log_level="info",
    )
