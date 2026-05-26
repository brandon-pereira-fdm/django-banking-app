# Data Model: Banking MVP Constitution v2.0.0

This document describes planned entities, relationships, constraints, state values, and validation responsibility. It is not a database schema.

## Model Overview

```text
CustomUser (PERSONAL) 1--1 PersonalAccount
CustomUser (BUSINESS) 1--* BusinessMembership *--1 BusinessAccount
BusinessAccount 1--* BusinessInvitation
BusinessAccount 1--* BusinessAccessAuditEvent
BusinessAccount 1--* BusinessApprovalRequest
PersonalAccount / BusinessAccount -- completed financial transactions
PersonalAccount / BusinessAccount -- completed transfer operations
```

Personal and Business accounts are separate concrete domain entities. Money records use explicit references to either a Personal Account or a Business Account.

## CustomUser

**Purpose**: Authenticated login identity.

**Fields / responsibilities**:

- UUID or integer internal user identifier.
- `email`: globally unique login identifier.
- `username`: user-facing display name.
- `password`: Django-managed password hash.
- `access_context`: `PERSONAL` or `BUSINESS`.
- Standard Django authentication metadata.

**Constraints**:

- Email is unique across all Personal and Business identities.
- Access context is required.
- Access context is not changed through ordinary MVP flows.
- Password is never stored or displayed in plaintext.

**Validation responsibility**:

- Forms validate required fields and password confirmation.
- User model/manager normalizes email and creates password hash.
- Services enforce that Personal registration creates `PERSONAL` and Business registration creates `BUSINESS`.

## PersonalAccount

**Purpose**: Individual SGD account for one Personal user.

**Fields**:

- `account_id`: UUID account identifier.
- `owner`: one-to-one reference to `CustomUser` with `access_context=PERSONAL`.
- `phone_number`: required unique receiving phone number.
- `balance`: exact decimal SGD balance.
- `created_at`: timestamp.

**Constraints**:

- One Personal Account per Personal user.
- Only a `PERSONAL` user may own a Personal Account.
- Phone number is unique among Personal Accounts.
- Balance starts at SGD 0.00.
- Balance must not be negative.
- No opening deposit or retained minimum exists.

**Validation responsibility**:

- Registration form normalizes and validates phone input.
- Service enforces Personal-only user creation and duplicate phone rejection.
- Model/database enforce uniqueness and non-negative balance where practical.

## BusinessAccount

**Purpose**: Company-owned shared SGD account.

**Fields**:

- `account_id`: UUID account identifier.
- `business_display_name`: required display name.
- `uen`: required unique UEN for receiving transfers.
- `balance`: exact decimal SGD balance.
- `created_at`: timestamp.
- `is_active`: optional; use only if needed for future account disablement. The approved creation flow rejects invalid setup instead of saving inactive accounts.

**Constraints**:

- UEN is unique among Business Accounts.
- Opening deposit must be at least SGD 7,000.00.
- Access is controlled through active Business Memberships, not Personal Account ownership.
- At least one active AUTHORISER membership must exist after creation and after every membership-management action.
- Completed outgoing withdrawals/transfers must leave balance at least SGD 7,000.00.
- Balance must not be negative.

**Validation responsibility**:

- Forms normalize UEN to uppercase and trim whitespace.
- Business registration service enforces opening deposit, UEN uniqueness, initial AUTHORISER, opening transaction, and audit events atomically.
- Approval service enforces retained minimum at completion time.

## BusinessMembership

**Purpose**: Active or historical access relationship between a Business user and a Business Account.

**Fields**:

- `membership_id`: UUID.
- `business_account`: reference to Business Account.
- `business_user`: reference to `CustomUser` with `access_context=BUSINESS`.
- `role`: `MEMBER` or `AUTHORISER`.
- `is_active`: boolean.
- `created_at`: timestamp.
- `removed_at`: nullable timestamp.
- `removed_by`: nullable Business user reference for accountability.

**Constraints**:

- Only `BUSINESS` users may have memberships.
- One active membership per Business user per Business Account.
- A Business user may have active memberships in multiple Business Accounts.
- A Business Account may have multiple AUTHORISERS.
- Removing or changing memberships must not leave zero active AUTHORISERS.
- Promotion from MEMBER to AUTHORISER is supported.
- Demotion from AUTHORISER to MEMBER is unsupported and rejected.

**Removal strategy**:

- Removal sets `is_active=false` and `removed_at`, rather than deleting the row.
- Permission checks use active memberships only.

## BusinessInvitation

**Purpose**: Pending or historical invitation for Business Account access.

**Fields**:

- `invitation_id`: UUID.
- `business_account`: reference to Business Account.
- `invited_email`: normalized invited email.
- `intended_role`: `MEMBER` or `AUTHORISER`.
- `invited_by`: active AUTHORISER Business user or membership.
- `status`: `PENDING`, `ACCEPTED`, or `CANCELLED`.
- `issued_at`: timestamp.
- `accepted_at`: nullable timestamp.
- `accepted_by`: nullable Business user.

**Constraints**:

- Only active AUTHORISER may issue invitations.
- Invitation grants no access until accepted.
- Only a `BUSINESS` user with email matching `invited_email` may accept.
- Personal users cannot accept.
- Duplicate `PENDING` invitation for the same Business Account and email is rejected.
- Invitation expiry is excluded from MVP.

**Validation responsibility**:

- Invitation service enforces inviter role, duplicate pending rule, status transition, matching email, and Business-only acceptance.

## BusinessAccessAuditEvent

**Purpose**: Immutable access-governance audit record.

**Event types**:

- `BUSINESS_ACCOUNT_CREATED`
- `INITIAL_AUTHORISER_ASSIGNED`
- `INVITATION_ISSUED`
- `INVITATION_ACCEPTED`
- `ROLE_ASSIGNED`
- `MEMBER_PROMOTED_TO_AUTHORISER`
- `MEMBER_REMOVED`
- `AUTHORISER_REMOVED`
- `LAST_AUTHORISER_REMOVAL_REJECTED`

**Fields**:

- `event_id`: UUID.
- `business_account`: reference to Business Account.
- `acting_user`: nullable Business user.
- `affected_user`: nullable Business user.
- `invited_email`: nullable email.
- `role`: nullable `MEMBER` or `AUTHORISER`.
- `event_type`: required event type.
- `outcome`: success or rejected/invalid status.
- `details`: safe explanatory text.
- `created_at`: timestamp.

**Constraints**:

- Audit events are not financial transactions.
- Audit events are not editable through ordinary user flows.
- Visible only to active members of the relevant Business Account.

## CompletedFinancialTransaction

**Purpose**: Immutable record for completed money movement.

**Transaction types**:

- `DEPOSIT`
- `WITHDRAWAL`
- `TRANSFER_DEBIT`
- `TRANSFER_CREDIT`
- `BUSINESS_OPENING_DEPOSIT`

**Fields**:

- `transaction_id`: UUID.
- `personal_account`: nullable Personal Account reference.
- `business_account`: nullable Business Account reference.
- `transaction_type`: required type.
- `amount`: exact decimal SGD amount.
- `status`: completed representation only; completed financial transaction rows are never PENDING/FAILED.
- `completed_at`: timestamp.
- `transfer_operation`: nullable Transfer Operation.
- `business_approval_request`: nullable Business Approval Request.
- `actor_user`: nullable user who initiated or caused the movement.
- `description`: safe display text.

**Constraints**:

- Exactly one of `personal_account` or `business_account` must be set.
- Amount must be positive.
- Completed rows are immutable through user-facing flows.
- Successful transfer creates exactly two transaction rows, one debit and one credit, sharing one Transfer Operation.
- Failed, PENDING, REJECTED, CANCELLED, or FAILED approval records do not create completed financial transactions.

## TransferOperation

**Purpose**: Shared identifier for a successfully completed transfer.

**Fields**:

- `transfer_operation_id`: UUID.
- `sender_personal_account`: nullable Personal Account.
- `sender_business_account`: nullable Business Account.
- `recipient_personal_account`: nullable Personal Account.
- `recipient_business_account`: nullable Business Account.
- `amount`: exact decimal SGD amount.
- `completed_at`: timestamp.
- `business_approval_request`: nullable Business Approval Request for completed Business outgoing transfers.

**Constraints**:

- Exactly one sender account is set.
- Exactly one recipient account is set.
- Sender and recipient cannot be the same account.
- PENDING Business transfer requests do not create Transfer Operation rows.
- Each completed Transfer Operation must link one debit and one credit CompletedFinancialTransaction.

## BusinessApprovalRequest

**Purpose**: Workflow record for outgoing Business withdrawal or transfer requiring AUTHORISER action.

**Request types**:

- `BUSINESS_WITHDRAWAL`
- `BUSINESS_TRANSFER`

**Persisted statuses**:

- `PENDING`
- `COMPLETED`
- `REJECTED`
- `CANCELLED`
- `FAILED`

**Fields**:

- `request_id`: UUID.
- `business_account`: Business Account.
- `requested_by_membership`: requesting Business Membership.
- `requested_by_user`: requesting Business user snapshot/reference.
- `request_type`: required type.
- `amount`: exact decimal SGD amount.
- `recipient_personal_account`: nullable for transfer requests.
- `recipient_business_account`: nullable for transfer requests.
- `recipient_label_snapshot`: safe display label for audit.
- `requested_at`: timestamp.
- `actioned_by_authoriser_membership`: nullable membership.
- `actioned_by_user`: nullable Business user.
- `resolved_at`: nullable timestamp.
- `status`: required persisted status.
- `safe_reason`: nullable safe explanation.
- `completed_transaction`: nullable for completed withdrawal.
- `completed_transfer_operation`: nullable for completed transfer.

**Constraints**:

- Submission requires active MEMBER or AUTHORISER membership.
- Approval/rejection requires active AUTHORISER membership.
- Cancellation requires requester ownership or active AUTHORISER membership.
- Only PENDING requests may transition.
- COMPLETED, REJECTED, CANCELLED, and FAILED are final.
- There is no persisted APPROVED status.
- PENDING requests do not reserve funds, change balances, or create completed financial records.
- Multiple PENDING requests may coexist.
- Approval revalidates current balance and retained minimum.

## State Transitions

### Business Invitation

```text
PENDING -> ACCEPTED
PENDING -> CANCELLED
ACCEPTED and CANCELLED are final for MVP.
```

### Business Membership

```text
MEMBER active -> AUTHORISER active
MEMBER active -> inactive removed
AUTHORISER active -> inactive removed, only if another active AUTHORISER remains
AUTHORISER -> MEMBER demotion is rejected
```

### Business Approval Request

```text
PENDING -> COMPLETED   (AUTHORISER approval + financial completion succeeds)
PENDING -> FAILED      (AUTHORISER approval attempted + validation fails)
PENDING -> REJECTED    (AUTHORISER rejects)
PENDING -> CANCELLED   (requester cancels own request or AUTHORISER cancels)
COMPLETED, FAILED, REJECTED, CANCELLED are final.
```

## Validation Responsibility Summary

- **Forms**: required fields, format feedback, amount input parsing messages, confirmation screens.
- **Services**: authoritative permissions, context checks, active memberships, role checks, final-AUTHORISER protection, money validation, retained minimum, transfer resolution, atomicity, and audit creation.
- **Models/database**: uniqueness, required relationships, status/role choices, non-negative balances, and "exactly one account reference" constraints where practical for SQLite.
