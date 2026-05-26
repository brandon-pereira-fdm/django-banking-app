# Quickstart: Banking MVP Constitution v2.0.0

This is a local learning MVP. It is not suitable for real banking, real money movement, public hosting, or production use.

## Prerequisites

- macOS
- Python 3.11 or later
- Git

## Create a Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## Install Dependencies

The approved MVP dependencies are Django and Waitress.

```bash
pip install Django waitress
pip freeze > requirements.txt
```

If `requirements.txt` already exists after implementation, use:

```bash
pip install -r requirements.txt
```

## Configure Environment

Set a local Django secret key through an environment variable.

```bash
export DJANGO_SECRET_KEY="replace-with-a-local-development-secret"
export DJANGO_DEBUG="1"
```

Do not commit `.env`, local secret files, or real credentials. The project `.gitignore` should exclude local secrets, virtual environments, Python caches, SQLite database files, and local generated assets.

## Database Setup

After implementation creates the Django project and migrations:

```bash
python3 manage.py migrate
```

## Superseded Development Model Reset Guidance

Constitution v2.0.0 replaces the earlier Personal-Account-authorises-Business-Account design. If a local SQLite database or old migrations were created from the superseded model during development, the recommended local MVP path is:

1. Ensure no valuable local-only data needs preservation.
2. Remove the old local SQLite database file.
3. Regenerate/apply the v2.0.0 migrations.

Example after implementation, if the database file is `db.sqlite3`:

```bash
rm db.sqlite3
python3 manage.py migrate
```

Do not use this reset guidance for any real or production data. This MVP is local-only.

## Run Tests

```bash
python3 manage.py test
```

The test suite must cover separate Personal and Business identities, memberships, invitations, money validation, transfer records, approval workflow, Access Audit History, and access control.

## Create Test Users

Use normal registration flows in the browser:

- Open a Personal Account for Personal-only access.
- Open a Business Account for Business-only access and initial AUTHORISER membership.
- Use Business invitation flows to add additional Business Users.

## Static Files

For local Django development, static files can be served by Django when debug mode is enabled. For Waitress-style local execution, collect static files if implementation config requires it:

```bash
python3 manage.py collectstatic
```

## Run Locally With Django Development Server

```bash
python3 manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Run Locally With Waitress

After implementation provides a WSGI app and optional Waitress entry point:

```bash
waitress-serve --listen=127.0.0.1:8000 bankapp.wsgi:application
```

Open:

```text
http://127.0.0.1:8000/
```

## Local MVP Disclaimer

This application is a training/local MVP. It does not integrate with banks, payment networks, external identity providers, real email delivery, government UEN registries, OTP systems, fraud controls, or production-grade financial infrastructure. Do not use it for real funds or public production banking.
