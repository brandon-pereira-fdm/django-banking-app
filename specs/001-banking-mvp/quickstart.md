# Quickstart: Banking MVP Constitution v3.0.0

This is a local learning MVP. It is not suitable for real banking, real money movement, public hosting, production compliance, or customer data.

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
```

If `requirements.txt` exists after implementation:

```bash
pip install -r requirements.txt
```

## Configure Environment

```bash
export DJANGO_SECRET_KEY="replace-with-a-local-development-secret"
export DJANGO_DEBUG="1"
```

Do not commit `.env`, local secret files, real credentials, temporary passwords, local SQLite databases, virtual environments, Python caches, or collected generated assets.

## Superseded v2 Implementation Reset Guidance

Constitution v3.0.0 supersedes invitation acceptance, multi-Business memberships, Business Account selectors, and invitation-specific registration. The preferred local MVP implementation path is:

1. Confirm no local development data requires preservation.
2. Archive or remove active v2 checklist gates before implementation gate scanning.
3. Remove/reset the local SQLite database when implementation tasks explicitly reach the migration/reset step.
4. Replace superseded uncommitted development migrations where safe.
5. Generate fresh v3 migrations during implementation.
6. Recreate sample data through tests or documented setup only.

Do not execute database reset or migration generation during planning.

## Database Setup After v3 Implementation

```bash
python3 manage.py migrate
```

## Run Tests

```bash
python3 manage.py test
```

The suite must cover Personal and Business login-context isolation, provisioned employee access, mandatory password change, password reset, deactivation/reactivation, final AUTHORISER protection, money validation, transfers, Business approvals, histories, security, and Midnight Ledger UI flows.

## Manual MVP Flow After Implementation

1. Open the product selection page.
2. Register a Personal Account and verify balance `SGD 0.00` plus phone recipient identifier.
3. Register a Business Account with opening deposit `SGD 7,000.00` or more.
4. Sign in as the initial AUTHORISER and open Team Access.
5. Add MEMBER employee access with a temporary password.
6. Sign in as the employee and verify mandatory password change blocks normal Business pages.
7. Change password and verify MEMBER access.
8. Test Business deposit, outgoing request submission, AUTHORISER approval/rejection/cancellation, and histories.

No invitation or multi-Business Account selector flow should appear.

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

```bash
waitress-serve --listen=127.0.0.1:8000 bankapp.wsgi:application
```

If implementation provides `bankapp/waitress_server.py`, an equivalent local command may be documented there.

## Local MVP Disclaimer

This application is for local learning only. It does not integrate with banks, payment networks, identity providers, email delivery, government UEN registries, OTP systems, fraud controls, or production infrastructure. Do not use it for real funds or public banking.
