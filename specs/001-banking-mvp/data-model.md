# Data Model: Banking MVP Constitution v3.0.0

This document defines planned entities, fields, relationships, constraints, statuses, validation responsibilities, UUID usage, and rationale. It is not executable schema.

## Model Overview

```text
CustomUser(PERSONAL) 1--1 PersonalAccount
CustomUser(BUSINESS_EMPLOYEE) 1--1 BusinessEmployeeAccess *--1 BusinessAccount
BusinessAccount 1--* BusinessOutgoingRequest
BusinessAccount 1--* AccessAuditEvent
PersonalAccount / BusinessAccount 1--* CompletedFinancialTransaction
TransferOperation 1--2 CompletedFinancialTransaction
BusinessOutgoingRequest 0..1--0..1 TransferOperation
```

## CustomUser

**Purpose**: Authenticated login identity.

**Planned fields/responsibilities**:

- internal Django user identifier;
- `email`: globally unique login identifier;
- `username` or `display_name`;
- Django-managed password hash;
- `login_context`: `PERSONAL` or `BUSINESS_EMPLOYEE`;
- standard Django auth metadata.

**Rules and constraints**:

- Email is unique across all login identities.
- Login context is required and not editable through ordinary MVP actions.
- A `PERSONAL` user may own one Personal Account.
- A `BUSINESS_EMPLOYEE` user may have one Business Employee Access record.
- Password values are never displayed in ordinary pages or audit histories.

## PersonalAccount

**Purpose**: Individual SGD financial account.

**Planned fields**:

- `account_id`: UUID;
- `owner`: one-to-one `CustomUser` with `login_context=PERSONAL`;
- `phone_number`: unique receiving phone number;
- `balance`: Decimal SGD;
- `created_at`: timestamp.

**Rules and constraints**:

- One Personal Account per Personal user.
- Only Personal users may own Personal Accounts.
- Phone number is unique.
- Starts at `SGD 0.00`.
- No opening deposit.
- No retained minimum.
- Balance must never become negative.

## BusinessAccount

**Purpose**: Company-owned SGD financial account.

**Planned fields**:

- `account_id`: UUID;
- `business_display_name`;
- `uen`: unique company UEN for incoming transfers;
- `balance`: Decimal SGD;
- `created_at`: timestamp.

**Rules and constraints**:

- UEN is unique.
- Opening deposit must be at least `SGD 7,000.00`.
- Incoming transfers by UEN do not require approval.
- Deposits do not require approval.
- Completed outgoing withdrawals/transfers must leave at least `SGD 7,000.00`.
- Must always have at least one active AUTHORISER employee access record.

## BusinessEmployeeAccess

**Purpose**: Connect one Business employee login to one Business Account and define role/access state.

**Planned fields**:

- `access_id`: UUID;
- `user`: one-to-one `CustomUser` with `login_context=BUSINESS_EMPLOYEE`;
- `business_account`: foreign key to Business Account;
- `role`: `MEMBER` or `AUTHORISER`;
- `access_status`: `PASSWORD_CHANGE_REQUIRED`, `ACTIVE`, or `DEACTIVATED`;
- `created_at`;
- `activated_at`: nullable;
- `deactivated_at`: nullable;
- `deactivated_by`: nullable reference to acting Business employee user/access;
- `reactivated_at`: nullable.

**Constraints**:

- Only `BUSINESS_EMPLOYEE` users may have Business Employee Access.
- Each Business employee login belongs to exactly one Business Account.
- A Business Account may have many employee access records.
- A Business Account may have many AUTHORISERS.
- Deactivation must not leave zero active AUTHORISERS.
- Demotion from AUTHORISER to MEMBER is unsupported.
- Employee access is retained for auditability rather than deleted through ordinary workflows.

**State transitions**:

```text
Provisioned employee: PASSWORD_CHANGE_REQUIRED -> ACTIVE
Password reset: ACTIVE/DEACTIVATED? -> PASSWORD_CHANGE_REQUIRED after allowed reset/reactivation
Deactivation: ACTIVE or PASSWORD_CHANGE_REQUIRED -> DEACTIVATED
Reactivation: DEACTIVATED -> PASSWORD_CHANGE_REQUIRED
```

Reactivation requires a new temporary password. Initial Business creator starts as `ACTIVE`.

## CompletedFinancialTransaction

**Purpose**: Immutable completed monetary audit trail.

**Types**:

- `DEPOSIT`;
- `WITHDRAWAL`;
- `TRANSFER_DEBIT`;
- `TRANSFER_CREDIT`;
- `BUSINESS_OPENING_DEPOSIT`.

**Planned fields**:

- `transaction_id`: UUID;
- `personal_account`: nullable Personal Account;
- `business_account`: nullable Business Account;
- `transaction_type`;
- `amount`: Decimal SGD;
- `completed_at`;
- `transfer_operation`: nullable Transfer Operation;
- `business_outgoing_request`: nullable Business Outgoing Request;
- `actor_user`: nullable authenticated user;
- `description`: safe display text.

**Rules and constraints**:

- Exactly one of `personal_account` or `business_account` is set.
- Amount is positive.
- Rows represent completed movement only.
- User-facing workflows cannot edit or delete completed rows.
- Access/security audit events are never stored here.

## TransferOperation

**Purpose**: Represent one completed transfer between two financial accounts.

**Planned fields**:

- `operation_id`: UUID;
- `sender_personal_account`: nullable;
- `sender_business_account`: nullable;
- `recipient_personal_account`: nullable;
- `recipient_business_account`: nullable;
- `amount`: Decimal SGD;
- `completed_at`;
- `business_outgoing_request`: nullable.

**Rules and constraints**:

- Exactly one sender account is set.
- Exactly one recipient account is set.
- Sender and recipient cannot be the same account.
- Each completed transfer creates exactly one debit transaction and one credit transaction.
- Pending Business transfer requests do not create TransferOperation rows.

## BusinessOutgoingRequest

**Purpose**: Workflow record for outgoing Business withdrawals and transfers requiring AUTHORISER action.

**Types**:

- `BUSINESS_WITHDRAWAL`;
- `BUSINESS_TRANSFER`.

**Persisted statuses**:

- `PENDING`;
- `COMPLETED`;
- `REJECTED`;
- `CANCELLED`;
- `FAILED`.

No `APPROVED` status exists.

**Planned fields**:

- `request_id`: UUID;
- `business_account`;
- `requested_by`: BusinessEmployeeAccess or employee user reference;
- `request_type`;
- `amount`: Decimal SGD;
- destination account fields for transfer requests only;
- `status`;
- `actioned_by`: nullable AUTHORISER;
- `requested_at`;
- `resolved_at`: nullable;
- `safe_reason`: nullable safe text;
- optional completed transaction/transfer links.

**Rules and constraints**:

- Only active employees may submit.
- Pending requests move no funds and reserve no funds.
- Multiple Pending requests may coexist.
- Only active AUTHORISERS may approve or reject.
- MEMBER may cancel only own Pending request.
- AUTHORISER may cancel any Pending request.
- Terminal statuses cannot be acted on again.

## AccessAuditEvent

**Purpose**: Immutable Business access-security and employee-administration audit record.

**Event types**:

- `BUSINESS_ACCOUNT_CREATED`;
- `INITIAL_AUTHORISER_CREATED`;
- `EMPLOYEE_ACCESS_CREATED`;
- `TEMPORARY_PASSWORD_ISSUED`;
- `PASSWORD_CHANGE_COMPLETED`;
- `EMPLOYEE_ACTIVATED`;
- `TEMPORARY_PASSWORD_RESET`;
- `MEMBER_PROMOTED_TO_AUTHORISER`;
- `EMPLOYEE_DEACTIVATED`;
- `EMPLOYEE_REACTIVATED`;
- `FINAL_AUTHORISER_DEACTIVATION_REJECTED`.

**Planned fields**:

- `event_id`: UUID;
- `business_account`;
- `acting_employee`: nullable BusinessEmployeeAccess/user;
- `affected_employee`: nullable BusinessEmployeeAccess/user;
- `event_type`;
- `previous_role`: nullable;
- `new_role`: nullable;
- `previous_status`: nullable;
- `new_status`: nullable;
- `outcome`: success/rejected;
- `safe_metadata`: safe JSON/text;
- `created_at`.

**Rules and constraints**:

- Never store password values, password hashes, or secrets.
- Distinct from Transaction History and Approval History.
- Immutable through ordinary user workflows.
- Visible only to active employees of the relevant Business Account.

## Structural Constraint Notes for SQLite

- Use database uniqueness for email, phone number, UEN, and one access row per Business employee user.
- Use choice fields for roles/statuses/types.
- Use model `clean()` and services for cross-row constraints SQLite cannot express, especially last-active-AUTHORISER protection and exactly-one-account references.
- Use service-layer transactions for multi-row financial and access-governance operations.
