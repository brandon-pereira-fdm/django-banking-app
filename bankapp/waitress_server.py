"""Local Waitress entry point for the macOS MVP."""
import os
import sys
from pathlib import Path

from waitress import serve

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bankapp.settings")

from bankapp.wsgi import application  # noqa: E402


def main():
    serve(application, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
