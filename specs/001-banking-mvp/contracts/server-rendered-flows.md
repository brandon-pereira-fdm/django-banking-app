# Contracts: Server-Rendered Page Flows

These contracts describe user-facing Django page and form flows. They are not REST API contracts and do not define implementation code.

## Shared Contract Rules

- All state-changing submissions use POST and CSRF protection.
- Authenticated pages require login.
- Personal pages require `PERSONAL` access context.
- Business pages require `BUSINESS` access context plus active membership for the selected Business Account.
- AUTHORISER-only actions must be enforced server-side.
- Money forms display and accept SGD amounts only.
- Confirmation pages are required before financial completion or consequential membership changes.
- Errors must be safe, specific, and non-sensitive.

## Public and Authentication Flows

### Account-Type Selection

**Route family**: public onboarding.

**Purpose**: Present two registration paths.

**Content contract**:

- Personal Account: individual use, receives transfers by phone number, no opening deposit, starts at SGD 0.00.
- Business Account: company use, receives transfers by UEN, requires SGD 7,000.00 opening funds, supports invited team access and AUTHORISER approvals.

**Next states**:

- Personal registration.
- Business Account registration.
- Sign-in.

### Personal Registration

**Inputs**:

- username;
- email;
- password;
- password confirmation;
- phone number.

**Success**:

- Create `PERSONAL` login identity.
- Create Personal Account with SGD 0.00 balance.
- Redirect to Personal dashboard or success page.

**Failures**:

- duplicate email;
- duplicate phone number;
- invalid password confirmation;
- invalid required fields.

### Business Account Registration

**Inputs**:

- creator username;
- email;
- password;
- password confirmation;
- business display name;
- UEN;
- opening deposit.

**Success**:

- Create `BUSINESS` login identity.
- Create Business Account.
- Create initial AUTHORISER membership.
- Create Business opening-deposit completed transaction.
- Create Access Audit Events for Business Account creation and initial AUTHORISER assignment.
- Redirect to Business dashboard.

**Failures**:

- duplicate email;
- missing display name;
- missing or duplicate UEN;
- invalid amount;
- opening deposit below SGD 7,000.00;
- partial creation failure, with no partial account or membership result.

### Sign-In and Sign-Out

**Inputs**:

- email;
- password.

**Success**:

- `PERSONAL` users land on Personal dashboard.
- `BUSINESS` users land on Business dashboard or Business Account selector.

**Failures**:

- invalid credentials without exposing whether email or password was wrong.

## Invitation Flows

### Invitation Issue

**Actor**: active AUTHORISER for selected Business Account.

**Inputs**:

- invitee email;
- intended role: `MEMBER` or `AUTHORISER`.

**Success**:

- Create PENDING invitation.
- Record invitation-issued Access Audit Event.
- Show invitation status and safe invitee email.

**Failures**:

- actor is not AUTHORISER;
- invalid email;
- intended role missing or invalid;
- duplicate PENDING invitation for same Business Account and email.

### Invitation Acceptance by Existing Business User

**Actor**: authenticated `BUSINESS` user whose email matches invitation.

**Inputs**:

- invitation identifier;
- acceptance confirmation.

**Success**:

- Create active Business Membership with invitation role.
- Mark invitation ACCEPTED.
- Record invitation acceptance and role assignment audit events.
- Redirect to selected Business Account.

**Failures**:

- invitation not PENDING;
- email does not match;
- actor is `PERSONAL`;
- actor already has active membership for the Business Account.

### Invitation-Specific Business Registration

**Actor**: unauthenticated invitee or invitee without existing login.

**Inputs**:

- invitation identifier;
- username;
- invited email, fixed or prefilled;
- password;
- password confirmation.

**Success**:

- Create `BUSINESS` login identity.
- Accept invitation atomically.
- Create active membership and audit events.

**Failures**:

- invitation invalid or not PENDING;
- email does not match invitation;
- email already belongs to a Personal identity;
- duplicate active membership.

## Personal Banking Flows

### Personal Dashboard and Account Detail

**Actor**: `PERSONAL` user.

**Displays**:

- username;
- Personal balance as `SGD 0.00`;
- receiving phone number;
- quick links to Deposit, Withdraw, Transfer, Transactions;
- recent completed financial transactions.

**Forbidden**:

- Business navigation, approvals, members, invitations, Access Audit.

### Personal Deposit

**Inputs**:

- amount.

**Review**:

- destination Personal Account;
- amount;
- resulting balance preview where practical.

**Success**:

- Balance increases.
- Completed `DEPOSIT` transaction with UUID is shown.

**Failures**:

- invalid amount;
- unauthorised context.

### Personal Withdrawal

**Inputs**:

- amount.

**Review**:

- source account;
- amount;
- projected balance.

**Success**:

- Balance decreases and may become SGD 0.00.
- Completed `WITHDRAWAL` transaction UUID is shown.

**Failures**:

- invalid amount;
- insufficient funds;
- unauthorised context.

### Personal Transfer

**Inputs**:

- destination account type: Personal or Business;
- phone number for Personal destination or UEN for Business destination;
- amount.

**Recipient confirmation**:

- safe recipient display name or business display name;
- account type;
- masked or safe identifier;
- amount;
- completion is immediate for valid Personal outgoing transfer.

**Success**:

- Sender debit and recipient credit complete atomically.
- Show transfer operation ID and sender debit transaction UUID.

**Failures**:

- unknown phone or UEN;
- identifier/account-type mismatch;
- self-transfer;
- invalid amount;
- insufficient funds.

## Business Account Context Flow

### Business Account Selector

**Actor**: `BUSINESS` user.

**Displays**:

- active Business memberships;
- business display name;
- UEN;
- current role.

**Success**:

- Select a Business Account context for subsequent Business pages.

**Failure**:

- no active memberships: show invitation/onboarding-aware empty state.

## Business Financial Flows

### Business Dashboard

**Actor**: active MEMBER or AUTHORISER.

**Displays**:

- business display name;
- UEN;
- current balance;
- retained-minimum reminder;
- current user's role;
- pending outgoing-request count;
- quick actions allowed for role;
- recent completed transactions;
- recent approval activity.

### Business Deposit

**Actor**: active MEMBER or AUTHORISER.

**Inputs**:

- amount.

**Success**:

- Balance increases immediately.
- Completed `DEPOSIT` transaction UUID is shown.

**Failures**:

- invalid amount;
- no active membership.

### Business Withdrawal Request

**Actor**: active MEMBER or AUTHORISER.

**Inputs**:

- amount.

**Review**:

- selected Business Account;
- amount;
- explanation that request becomes PENDING and no balance changes until AUTHORISER approval.

**Success**:

- Create PENDING Business Approval Request.
- Show request ID and PENDING status.

**Failures**:

- invalid amount;
- no active membership.

### Business Transfer Request

**Actor**: active MEMBER or AUTHORISER.

**Inputs**:

- destination account type;
- phone number or UEN matching destination type;
- amount.

**Recipient confirmation**:

- safe recipient name;
- recipient account type;
- safe identifier;
- amount;
- approval required.

**Success**:

- Create PENDING Business Approval Request.
- No balance change and no completed transfer records.

**Failures**:

- invalid amount;
- unknown destination;
- identifier mismatch;
- self-transfer;
- no active membership.

## Approval and Cancellation Flows

### Approval List

**Actor**: active MEMBER or AUTHORISER.

**Displays**:

- requests for selected Business Account;
- filter by status;
- requester and requester role;
- request type;
- amount;
- destination where applicable;
- status;
- dates.

**Controls**:

- AUTHORISER sees approve/reject/cancel controls for PENDING requests.
- MEMBER sees cancel control only for their own PENDING requests.

### Approval Detail

**Displays**:

- requester;
- requester role;
- operation type;
- recipient confirmation for transfers;
- amount;
- current balance;
- projected post-completion balance;
- retained-minimum compliance;
- status history/outcome reason.

### Approve Request

**Actor**: active AUTHORISER.

**Success**:

- If current validation passes, transition PENDING to COMPLETED and complete financial movement atomically.

**Failure**:

- If current financial validation fails, transition PENDING to FAILED with no balance movement and no completed financial records.
- If actor is not AUTHORISER or request is terminal, reject action without state change except safe error display.

### Reject Request

**Actor**: active AUTHORISER.

**Success**:

- Transition PENDING to REJECTED.
- No balance movement.

### Cancel Request

**Actor**:

- requester for own PENDING request; or
- active AUTHORISER for any PENDING request.

**Success**:

- Transition PENDING to CANCELLED.
- No balance movement.

## Membership Administration Flows

### Member List

**Actor**: active MEMBER or AUTHORISER.

**Displays**:

- active members;
- roles;
- invitation status summary;
- role-specific management controls.

**Controls**:

- AUTHORISER can invite, promote MEMBER, and remove allowed memberships.
- MEMBER sees read-only membership information or no management controls.

### Promote MEMBER

**Actor**: active AUTHORISER.

**Success**:

- MEMBER becomes AUTHORISER.
- Access Audit Event records promotion.

**Failures**:

- actor not AUTHORISER;
- target not active MEMBER.

### Remove MEMBER

**Actor**: active AUTHORISER.

**Success**:

- Membership becomes inactive immediately.
- Access Audit Event records removal.

### Remove AUTHORISER

**Actor**: active AUTHORISER.

**Success**:

- AUTHORISER membership becomes inactive only if another active AUTHORISER remains.
- Access Audit Event records removal.

**Failures**:

- final AUTHORISER removal attempt is rejected;
- retained audit event records rejected attempt where appropriate.

### Demotion Attempt

**Result**:

- AUTHORISER-to-MEMBER demotion is unsupported and rejected.

## History Flows

### Transaction History

**Personal access**: Personal owner only.

**Business access**: active Business member only for selected Business Account.

**Contains**:

- completed deposits;
- completed withdrawals;
- transfer debits;
- transfer credits;
- Business opening deposits.

**Excludes**:

- PENDING/REJECTED/CANCELLED/FAILED approval records;
- access audit records.

### Approval History

**Access**: active Business member only.

**Contains**:

- Business outgoing requests in PENDING, COMPLETED, REJECTED, CANCELLED, FAILED.

**Excludes**:

- access audit events;
- unrelated financial deposits/incoming transfers unless tied to request outcome display.

### Access Audit History

**Access**: active Business member only.

**Contains**:

- Business account creation;
- initial AUTHORISER assignment;
- invitations issued;
- invitations accepted;
- roles assigned;
- promotions;
- removals;
- retained invalid governance attempts such as final-AUTHORISER removal rejection.

**Excludes**:

- completed financial movements;
- outgoing approval requests except where safe cross-reference is useful.
