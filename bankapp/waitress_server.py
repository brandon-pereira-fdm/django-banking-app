"""Local Waitress entry point for the macOS MVP."""
import os

from waitress import serve

from bankapp.wsgi import application


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bankapp.settings")
    serve(application, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
