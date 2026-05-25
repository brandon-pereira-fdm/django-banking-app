# Data Model: Banking MVP

## Overview

The MVP uses Django models in two apps:

- `users`: authentication identity.
- `banking`: accounts, balances, transfers, approvals, and completed financial
  history.

All money is SGD and stored with exact decimal fields. All identifiers used for
completed financial audit records are UUID values.

## Entity: CustomUser

**Purpose**: Login identity and owner of up to one Personal Account and one
Business Account.

**Fields**:

- `id`: internal primary key.
- `email`: unique, normalised email used for login.
- `username`: user-selected display name.
- `password`: Django-managed password hash.
- Standard Django auth metadata: active flag, staff/superuser flags where
  applicable, date joined, last login.

**Relationships**:

- Owns zero or one Personal `BankAccount`.
- Owns zero or one Business `BankAccount`.

**Constraints and validation**:

- Email is required and unique.
- Password is never stored or displayed in plaintext.
- Authentication uses Django password hashing.

## Entity: BankAccount

**Purpose**: Store both Personal and Business Accounts with shared balance and
ownership behaviour.

**Design decision**: Use one `BankAccount` model with an account-type
discriminator. This keeps transfers, histories, and balances simple while
constraints guard type-specific fields.

**Common fields**:

- `id`: internal primary key.
- `account_id`: UUID public/internal account identifier.
- `owner`: required relationship to `CustomUser`.
- `account_type`: `PERSONAL` or `BUSINESS`.
- `balance`: `DecimalField(max_digits=12, decimal_places=2)`.
- `created_at`: timestamp.

**Personal-only fields**:

- `phone_number`: required and unique when `account_type = PERSONAL`; empty for
  Business Accounts.

**Business-only fields**:

- `business_display_name`: required when `account_type = BUSINESS`.
- `uen`: required and unique when `account_type = BUSINESS`; empty for Personal
  Accounts.
- `authorised_personal_account`: required relationship to the owner's Personal
  Account when `account_type = BUSINESS`.

**Constraints**:

- One Personal Account per user.
- One Business Account per user.
- Personal Account phone numbers are unique among Personal Accounts.
- Business Account UEN values are unique among Business Accounts.
- Balance must not be negative.
- Personal type requires phone number and forbids UEN/business display name.
- Business type requires business display name, UEN, and authorised Personal
  Account; forbids phone number as a transfer recipient identifier.
- Business authorised Personal Account must belong to the same owner.
- Business Account creation below SGD 7,000.00 is rejected.

**Validation responsibilities**:

- Forms: input shape, labels, user-facing errors.
- Services: ownership, business prerequisites, opening deposit, no negative
  balances, retained minimum, recipient identity, authorisation.
- Database/model constraints: uniqueness, non-negative structural balance,
  one-account-per-type ownership, and type-specific field consistency where
  practical.

## Entity: CompletedTransaction

**Purpose**: Immutable audit record for completed balance-changing financial
movements.

**Transaction types**:

- `DEPOSIT`
- `WITHDRAWAL`
- `TRANSFER_DEBIT`
- `TRANSFER_CREDIT`
- `BUSINESS_OPENING_DEPOSIT`

**Fields**:

- `transaction_id`: UUID, unique.
- `account`: related `BankAccount`.
- `transaction_type`: one of the completed transaction types.
- `amount`: `DecimalField(max_digits=12, decimal_places=2)`.
- `currency`: fixed `SGD` representation or implied by invariant.
- `status`: completed-record representation, fixed to completed for this model.
- `created_at` / `completed_at`: completion timestamp.
- `transfer_operation`: optional relationship to `TransferOperation`.
- `approval_request`: optional relationship to `ApprovalRequest` for completed
  Business outgoing operations.

**Rules**:

- Every successful deposit creates one `DEPOSIT`.
- Every successfully completed withdrawal creates one `WITHDRAWAL`.
- Every successfully completed transfer creates one `TRANSFER_DEBIT` and one
  `TRANSFER_CREDIT`.
- Business Account opening funding creates one `BUSINESS_OPENING_DEPOSIT`.
- Records are not editable or deletable through ordinary user-facing flows.
- Failed, PENDING, REJECTED, CANCELLED, and FAILED approval requests do not
  create completed transaction records.

## Entity: TransferOperation

**Purpose**: Represent one completed transfer movement linking sender and
recipient transaction records.

**Fields**:

- `transfer_operation_id`: UUID, unique.
- `sender_account`: related `BankAccount`.
- `recipient_account`: related `BankAccount`.
- `amount`: `DecimalField(max_digits=12, decimal_places=2)`.
- `currency`: fixed `SGD` representation or implied by invariant.
- `status`: `COMPLETED` for completed transfer operations.
- `created_at`: timestamp.
- `completed_at`: timestamp.

**Rules**:

- A completed transfer has exactly one sender debit completed transaction and
  one recipient credit completed transaction.
- Both completed transaction records reference the same transfer operation ID.
- Each transaction record keeps its own UUID transaction ID.
- PENDING Business transfer requests do not create completed transfer operation
  records until approval succeeds and money moves.

## Entity: ApprovalRequest

**Purpose**: Workflow record for outgoing Business Account withdrawals and
transfers requiring approval.

**Request types**:

- `BUSINESS_WITHDRAWAL`
- `BUSINESS_TRANSFER`

**Statuses**:

- `PENDING`
- `COMPLETED`
- `REJECTED`
- `CANCELLED`
- `FAILED`

No persisted `APPROVED` status exists.

**Fields**:

- `request_id`: UUID, unique.
- `business_account`: requesting Business Account.
- `authorised_personal_account`: required authorised Personal Account.
- `request_type`: withdrawal or transfer.
- `amount`: `DecimalField(max_digits=12, decimal_places=2)`.
- `recipient_account`: required for transfer requests, empty for withdrawal.
- `recipient_type_snapshot`: Personal or Business for audit display.
- `recipient_identifier_snapshot`: masked or safe identifier display data.
- `status`: one of the five allowed statuses.
- `requested_at`: timestamp.
- `resolved_at`: timestamp when terminal.
- `resolution_note`: safe failure/rejection/cancellation explanation when
  applicable.
- `completed_transaction`: optional link for completed withdrawal.
- `transfer_operation`: optional link for completed transfer.

**Rules**:

- Only PENDING requests may transition.
- COMPLETED, REJECTED, CANCELLED, and FAILED are final.
- PENDING requests do not modify balances, reserve funds, or create completed
  transaction records.
- Approval action revalidates amount, current Business Account balance, retained
  minimum, and authorised identity.
- Successful approval and completed money movement changes PENDING to COMPLETED.
- Approval-time validation failure changes PENDING to FAILED with no money
  movement.
- Rejection changes PENDING to REJECTED with no money movement.
- Owner cancellation changes PENDING to CANCELLED with no money movement.

## Identifier Normalisation

### Personal Account Phone Number

- Required only for Personal Accounts.
- Unique among Personal Accounts.
- Trim surrounding whitespace.
- Remove common visual separators such as spaces and hyphens for comparison.
- Store in a consistent Singapore-oriented normalised form.
- No OTP or external telecom verification in MVP.

### Business Account UEN

- Required only for Business Accounts.
- Unique among Business Accounts.
- Trim surrounding whitespace.
- Uppercase before storage and comparison.
- Treat as user-supplied, format-validated, unique application data.
- No external Singapore registry lookup in MVP.

## Money Validation

- Calculations use Python `Decimal`.
- Stored money uses `DecimalField(max_digits=12, decimal_places=2)`.
- Reject zero, negative, non-numeric, malformed, non-SGD, excessive-precision,
  and over-capacity amounts.
- Display all money as `SGD 0.00`.

## State Transitions

```text
PENDING -> COMPLETED
PENDING -> REJECTED
PENDING -> CANCELLED
PENDING -> FAILED
```

No other approval request transitions are allowed.
