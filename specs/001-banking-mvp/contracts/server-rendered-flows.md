# Server-Rendered Flow Contracts: Banking MVP

## Contract Style

This MVP exposes server-rendered Django pages and form actions, not a REST API.
Contracts describe page responsibilities, required inputs, server-side
validation, outcomes, and traceability. Core flows must work without mandatory
JavaScript.

## Public Authentication

### Registration

**Page**: `/register/`

**Inputs**:

- Email.
- Username.
- Password.
- Password confirmation.

**Validation**:

- Email required and unique.
- Password handled by Django password validation and hashing.
- Receiving identifiers are not collected here; they are collected during
  account setup.

**Outcomes**:

- Success creates authenticated user identity or enables sign-in.
- Duplicate email returns a clear inline error.

**Traceability**: `FR-001`, `FR-002`, `SEC-003`, `TEST-008`, `TEST-009`,
`TEST-046`.

### Sign-In and Sign-Out

**Pages**: `/login/`, `/logout/`

**Inputs**:

- Email.
- Password.

**Validation**:

- Incorrect credentials rejected without exposing which credential was wrong.

**Traceability**: `FR-003`, `FR-004`, `SEC-001`, `TEST-041`, `TEST-046`.

## Authenticated Shell

### Dashboard

**Page**: `/dashboard/`

**Content contract**:

- Welcome header using username.
- Personal Account card or setup empty state.
- Business Account card or setup empty state.
- Balances formatted as `SGD 0.00`.
- Personal receiving phone number where available.
- Business receiving UEN where available.
- Quick actions for Deposit, Withdraw, Transfer.
- Recent completed transactions.
- PENDING approval indicator.

**Traceability**: `UX-003` to `UX-010`, `TEST-045`.

## Account Setup and Detail

### Personal Account Setup

**Page**: `/accounts/personal/setup/`

**Inputs**:

- Receiving phone number.

**Validation**:

- User must be authenticated.
- User must not already have a Personal Account.
- Phone number required and unique among Personal Accounts.

**Outcomes**:

- Success creates Personal Account with balance SGD 0.00.
- No opening-deposit transaction is created.

**Traceability**: `FR-008` to `FR-010`, `BR-008` to `BR-011`, `TEST-001` to
`TEST-003`.

### Business Account Setup

**Page**: `/accounts/business/setup/`

**Inputs**:

- Business display name.
- Company UEN.
- Opening deposit amount in SGD.

**Validation**:

- User must already own a Personal Account.
- User must not already own a Business Account.
- Business display name required.
- UEN required, normalised, and unique.
- Opening deposit must be at least SGD 7,000.00.

**Outcomes**:

- Success creates Business Account, links owner's Personal Account as authorised
  approver, credits opening deposit, and creates a completed
  `BUSINESS_OPENING_DEPOSIT` transaction atomically.
- Failure creates no Business Account and no completed transaction.

**Traceability**: `FR-016` to `FR-026`, `BR-012` to `BR-017`, `TEST-004` to
`TEST-007`, `TEST-047`.

## Money Operation Flows

### Deposit

**Page**: `/deposit/`

**Inputs**:

- Destination account.
- Amount in SGD.

**Validation**:

- Authenticated owner.
- Valid positive SGD amount.
- Business deposits require no approval.

**Outcomes**:

- Success updates balance and creates completed `DEPOSIT` transaction.
- Result page shows UUID transaction ID.

**Traceability**: `FR-011`, `FR-027`, `BR-001` to `BR-007`, `TEST-010` to
`TEST-012`.

### Withdrawal

**Page**: `/withdraw/`

**Inputs**:

- Source account.
- Amount in SGD.

**Validation**:

- Personal withdrawal: valid positive amount and no negative result.
- Business withdrawal: valid positive amount and owner permission for request
  creation.

**Outcomes**:

- Personal success completes immediately with completed `WITHDRAWAL`.
- Business submission creates PENDING approval request with no balance change.

**Traceability**: `FR-012`, `FR-013`, `FR-029`, `BR-018` to `BR-027`,
`TEST-013` to `TEST-019`.

### Transfer

**Pages**: `/transfer/`, `/transfer/confirm/`

**Inputs**:

- Source account.
- Recipient account type: Personal Account or Business Account.
- Phone number for Personal recipient, or UEN for Business recipient.
- Amount in SGD.

**Validation**:

- Recipient type must match identifier type.
- Personal recipient resolves by phone number.
- Business recipient resolves by UEN.
- Unknown recipient rejected.
- Self-transfer rejected.
- Same-user Personal-to-Business or Business-to-Personal transfer rejected.
- Amount valid and sufficient for sender rules.

**Confirmation contract**:

- Show recipient username or business display name.
- Show recipient account type.
- Show masked or appropriate identifier.
- Show amount in SGD.
- Show whether approval is required.
- Show retained-minimum notice for Business outgoing transfers.

**Outcomes**:

- Personal sender completes immediately if valid.
- Business sender creates PENDING approval request and no money moves.

**Traceability**: `FR-043` to `FR-055`, `BR-028` to `BR-037`, `TEST-020` to
`TEST-038`, `TEST-048`.

## Approval Flow

### Approval List

**Page**: `/approvals/`

**Inputs**:

- Optional status filter.

**Content contract**:

- PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED status chips.
- Request type.
- Amount.
- Requested date/time.
- Recipient safe confirmation for transfers.
- Current status.

### Approval Detail

**Page**: `/approvals/<request_id>/`

**Actions**:

- Approve PENDING request when actor owns authorised Personal Account.
- Reject PENDING request when actor owns authorised Personal Account.
- Cancel PENDING request when actor owns requesting Business Account.

**Review content**:

- Business Account balance.
- Requested outgoing amount.
- Projected balance.
- Whether projected balance satisfies SGD 7,000.00 retained minimum.

**Outcomes**:

- Successful approval plus completion: request becomes COMPLETED.
- Approval-time validation failure: request becomes FAILED.
- Rejection: request becomes REJECTED.
- Cancellation: request becomes CANCELLED.
- Terminal statuses cannot be actioned again.

**Traceability**: `FR-029` to `FR-042`, `BR-018` to `BR-027`, `TEST-032` to
`TEST-040`, `TEST-049`.

## History Flows

### Transactions

**Page**: `/transactions/`

**Inputs**:

- Optional account filter.
- Optional transaction-type filter.

**Content contract**:

- Completed financial records only.
- Transaction type.
- Amount in SGD.
- Date/time.
- Status.
- UUID transaction ID.
- Transfer operation ID where applicable.
- Clear debit/credit distinction without relying only on colour.

**Traceability**: `FR-056` to `FR-063`, `BR-034` to `BR-039`, `TEST-036` to
`TEST-044`, `TEST-050`.
