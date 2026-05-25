# Quickstart: Banking MVP

This quickstart describes local macOS setup for the planned server-rendered
Django MVP. It is not production deployment guidance.

## Prerequisites

- Python 3.11 or later.
- Git.
- macOS terminal.

## Create a Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## Install Minimal Dependencies

```bash
pip install Django waitress
```

No frontend framework, REST framework, CSS framework, payment SDK, queue, cloud
SDK, external auth SDK, or alternate database driver is required for the MVP.

## Environment Variables

Set local environment variables before running Django:

```bash
export DJANGO_SECRET_KEY='replace-with-local-development-secret'
export DJANGO_DEBUG='1'
export DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost'
```

Do not commit `.env`, local secret files, or generated SQLite database files.

## Database Setup

The MVP uses local SQLite:

```bash
python manage.py migrate
```

## Run Tests

```bash
python manage.py test
```

The test suite must cover the mandatory `TEST-###` cases from the
specification before the feature is treated as complete.

## Run Locally With Django During Development

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Run Locally With Waitress

After implementation provides the Django WSGI module and Waitress entry point,
launch with a command equivalent to:

```bash
python -m waitress --listen=127.0.0.1:8000 bankapp.wsgi:application
```

Open:

```text
http://127.0.0.1:8000/
```

## Static Files

For local use, custom CSS may be served by Django during development. If the
implementation uses collected static files for Waitress execution, run:

```bash
python manage.py collectstatic
```

## Local MVP Disclaimer

This project is a local learning MVP. It must not be connected to real banking
systems, real money movement, public production traffic, or external payment
providers. SQLite and local Waitress execution are intentionally scoped for
simple macOS demonstration and testing only.
