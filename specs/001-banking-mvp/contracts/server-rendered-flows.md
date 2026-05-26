# Contracts: Server-Rendered Page and Action Flows v3.0.0

These contracts describe user-facing Django page and form flows. They are not REST API contracts.

## Shared Rules

- All state-changing submissions use POST and CSRF protection.
- Authenticated pages require login.
- Personal pages require `PERSONAL` login context.
- Business operational pages require `BUSINESS_EMPLOYEE` login context plus `ACTIVE` Business Employee Access.
- Employees in `PASSWORD_CHANGE_REQUIRED` may access only mandatory password change and sign-out.
- `DEACTIVATED` employees are denied Business functionality and data.
- AUTHORISER-only actions are enforced server-side.
- Money forms use SGD only and show `SGD 0.00` formatting.
- Consequential financial and access-management actions use confirmation/review pages where appropriate.
- Errors are specific but do not expose secrets, password state details, or unnecessary recipient data.

## Public and Authentication Flows

### Product Selection

**Purpose**: Present separate Personal Account and Business Account registration paths.

**Content**:

| Product | Identifier | Opening Requirement | Access Model |
|---|---|---|---|
| Personal Account | Phone number | No opening deposit | Individual Personal Login |
| Business Account | UEN | Minimum SGD 7,000.00 | Company account with provisioned employee access |

### Personal Registration

**Inputs**: display name, unique email, password, confirmation, unique phone number.

**Success**: create Personal Login and Personal Account at `SGD 0.00`; redirect to Personal Dashboard.

**Failures**: duplicate email, duplicate phone, invalid password confirmation, required fields missing.

### Business Account Registration

**Inputs**: initial AUTHORISER display name, unique email, password, confirmation, business display name, UEN, opening deposit.

**Success**: create Business Account, creator `BUSINESS_EMPLOYEE` login, active AUTHORISER access, opening transaction, and initial Access Audit events; redirect to Business Dashboard.

**Failures**: duplicate email, missing business display name, missing/duplicate UEN, invalid amount, opening deposit below `SGD 7,000.00`, partial creation failure.

### Sign-In

**Inputs**: email, password.

**Success routing**:

- Personal Login -> Personal Dashboard.
- Active Business Employee -> Business Dashboard.
- Business Employee in `PASSWORD_CHANGE_REQUIRED` -> mandatory password-change page.
- Deactivated employee -> denied with safe message.

**Failures**: invalid credentials without identifying whether email or password was wrong.

### Mandatory Password Change

**Actor**: authenticated Business employee in `PASSWORD_CHANGE_REQUIRED`.

**Inputs**: new password, confirmation.

**Success**: password changed, access status becomes `ACTIVE`, Access Audit event recorded, redirect to Business Dashboard.

**Failures**: mismatched/invalid password, wrong context, active/deactivated state not eligible.

## Personal Banking Flows

### Personal Dashboard and Account Detail

Displays balance, receiving phone number, no-minimum-balance message, quick actions, and recent completed transactions. No Business navigation appears.

### Personal Deposit

Inputs amount. Review shows account, amount, and resulting balance where practical. Success updates balance and creates completed `DEPOSIT` transaction.

### Personal Withdrawal

Inputs amount. Review shows projected balance. Success may leave exactly `SGD 0.00`; insufficient funds are rejected with no transaction.

### Personal Transfer

Inputs destination type, matching phone/UEN identifier, amount. Review shows safe recipient confirmation. Success completes sender debit, recipient credit, Transfer Operation, and linked transaction records atomically.

## Business Banking Flows

### Business Dashboard

Displays business name, UEN, employee role, access state where relevant, balance, retained-minimum notice, available outgoing capacity indicator, pending approval count, recent financial activity, recent approval activity, and AUTHORISER Team Access summary where applicable.

### Business Deposit

**Actor**: active MEMBER or AUTHORISER.

**Success**: balance increases and completed `DEPOSIT` transaction is recorded. No approval request is created.

### Business Withdrawal Request

**Actor**: active MEMBER or AUTHORISER.

**Success**: creates `PENDING` Business outgoing request only. No balance movement or completed transaction occurs.

### Business Transfer Request

**Actor**: active MEMBER or AUTHORISER.

**Inputs**: destination type, phone/UEN, amount.

**Success**: recipient is resolved and a `PENDING` request is created only. No Transfer Operation or completed transaction exists yet.

### Approval Detail and Actions

Displays requester, requester role, request type, recipient if any, amount, current balance, projected post-approval balance, retained-minimum result, status, and permitted actions.

**Approve**: active AUTHORISER only; self-approval allowed; valid requests move directly `PENDING` -> `COMPLETED`; failed financial revalidation moves `PENDING` -> `FAILED` with no movement.

**Reject**: active AUTHORISER only; `PENDING` -> `REJECTED`.

**Cancel**: requester MEMBER may cancel own `PENDING`; AUTHORISER may cancel any `PENDING`; result `CANCELLED`.

## Team Access Flows

### Team Access Overview

**Actor**: active Business employee. Access-management controls are AUTHORISER-only.

Displays business name, UEN, current role, active employee count, active AUTHORISER count, password-change-required count, deactivated count, employee list, roles, statuses, and permitted actions. No Invitation terminology appears.

### Add Employee Access

**Actor**: active AUTHORISER.

**Inputs**: employee display name, unique email, role, temporary password, confirmation.

**Review**: heightened confirmation when role is AUTHORISER.

**Success**: creates employee login/access in `PASSWORD_CHANGE_REQUIRED`, records access-created and temporary-password-issued audit events, shows next-step instruction without persistent password retrieval.

### Promote Member

**Actor**: active AUTHORISER.

**Success**: MEMBER becomes AUTHORISER and Access Audit event is recorded. Demotion is unsupported.

### Reset Temporary Password

**Actor**: active AUTHORISER for another employee in same Business Account.

**Inputs**: new temporary password and confirmation.

**Success**: password hash replaced, access status becomes `PASSWORD_CHANGE_REQUIRED`, audit event recorded, prior password no longer authenticates.

### Deactivate Access

**Actor**: active AUTHORISER.

**Success**: eligible employee status becomes `DEACTIVATED`; access denied immediately; audit event recorded.

**Blocked**: final active AUTHORISER deactivation, with clear message and retained audit event where recorded.

### Reactivate Access

**Actor**: active AUTHORISER.

**Inputs**: new temporary password and confirmation.

**Success**: status becomes `PASSWORD_CHANGE_REQUIRED`, audit events recorded, employee must change password before normal access.

## History Flows

### Transaction History

Shows completed financial movement only: deposits, withdrawals, opening deposits, transfer debits, and transfer credits with UUID transaction IDs and transfer operation IDs where applicable.

### Approval History

Shows Business outgoing request workflow records: requester, role, type, amount, destination, status, actioning AUTHORISER, timestamps, and safe reason text.

### Access Audit History

Shows Business access-security events: account creation, initial AUTHORISER, employee access creation, temporary password issuance/reset, password activation, promotion, deactivation, reactivation, final-AUTHORISER rejection. Passwords and hashes never appear.

## Explicitly Inactive v3 Routes

- Invitation issue, acceptance, cancellation, and invitation-specific registration routes are inactive and must be removed/refactored.
- Multi-Business Account selector routes are inactive and must be removed/refactored.
