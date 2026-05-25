# Research: Banking MVP

## Decision: Use a Custom User Model From the Beginning

**Rationale**: The MVP requires email as the unique login identifier and a
user-selected username as display text. Starting with a custom Django user model
avoids later migration risk and keeps authentication aligned with the
constitution.

**Alternatives considered**:

- Django default `User`: rejected because username-first authentication would
  conflict with the preferred email-login direction and complicate later
  changes.
- Third-party authentication: rejected by constitution.

## Decision: Use One `BankAccount` Model With Account Type

**Rationale**: Personal and Business Accounts share owner, balance, account ID,
transactions, and transfer behaviour. A single model with an account-type
discriminator keeps transfers and histories simple while explicit constraints
protect type-specific fields.

**Alternatives considered**:

- Separate `PersonalAccount` and `BusinessAccount` models: clearer type
  separation, but more joining and duplicated money/account logic for the MVP.
- Abstract base model with two concrete tables: more abstraction than needed
  for two account types and one local MVP.

## Decision: Resolve Recipients by Account Type Plus Identifier

**Rationale**: Constitution 1.1.0 requires Personal recipients to use unique
phone numbers and Business recipients to use unique UEN values. Requiring the
sender to select recipient account type before entering the identifier prevents
ambiguous routing when a user owns both account types.

**Alternatives considered**:

- Phone-only lookup: rejected by amendment 1.1.0.
- Single identifier field that guesses account type: rejected because it is less
  explicit and harder to validate safely.

## Decision: Treat UEN as User-Supplied, Normalised, Unique Application Data

**Rationale**: The specification does not require external registry
verification. Normalising UEN values by trimming whitespace and uppercasing
supports consistent uniqueness without adding external integration.

**Alternatives considered**:

- External Singapore registry verification: outside MVP and not constitutionally
  approved.
- No format validation: rejected because basic user-input quality is needed for
  clear errors and duplicate prevention.

## Decision: Normalise Singapore Phone Input Without OTP Verification

**Rationale**: Personal Account phone numbers are receiving identifiers, not a
telecom verification feature. The MVP should trim spacing and apply a simple
consistent Singapore-oriented format while preserving the constitution's
no-extra-integration scope.

**Alternatives considered**:

- OTP verification: outside MVP.
- External phone validation service: outside MVP.

## Decision: Use `Decimal` and `DecimalField(max_digits=12, decimal_places=2)`

**Rationale**: SGD money must be exact and limited to two decimal places. The
chosen capacity supports up to SGD 9,999,999,999.99, which is ample for local
MVP testing without over-designing production banking limits.

**Alternatives considered**:

- Floating point: prohibited.
- Integer cents: viable, but less idiomatic with Django forms and `DecimalField`
  display for this beginner-friendly MVP.
- Larger precision: unnecessary for scope and may imply production scale.

## Decision: Service Layer Owns Financial Rules

**Rationale**: Forms provide helpful feedback, but banking invariants must be
enforced server-side in one place. `banking.services` centralises Decimal
validation, ownership checks, approval checks, atomic balance movement, and
transaction record creation.

**Alternatives considered**:

- View-only enforcement: rejected because rules would be duplicated and easier
  to bypass.
- Model-only enforcement: useful for structural constraints, but insufficient
  for multi-record atomic workflows and user permissions.

## Decision: Approval Has No Persisted `APPROVED` Status

**Rationale**: Constitution 1.1.0 makes approval an action. A successful
approval that completes money movement changes the request to `COMPLETED`; an
approval attempt that fails validation changes it to `FAILED`.

**Alternatives considered**:

- Store `APPROVED`: rejected by constitution.
- Complete money movement at request creation: rejected because outgoing
  Business operations require approval and PENDING requests do not reserve
  funds.

## Decision: Use Django `transaction.atomic()` With SQLite

**Rationale**: The MVP needs all-or-nothing balance and audit updates. Django
atomic blocks provide consistent transaction boundaries for local SQLite usage.
Each approval re-reads and revalidates balances before money moves.

**Alternatives considered**:

- PostgreSQL row locks: stronger for production, but outside constitutional MVP
  stack.
- Application-level reservation ledger: rejected because PENDING requests must
  not reserve funds.

## Decision: Server-Rendered Multi-Step Confirmation Flows

**Rationale**: The MVP must work without mandatory JavaScript. Server-rendered
confirmation pages support safe recipient confirmation, review steps, CSRF, and
clear validation with Django templates and forms.

**Alternatives considered**:

- SPA frontend: prohibited.
- AJAX-required workflows: rejected because core flows must not depend on
  JavaScript.

## Decision: Custom CSS for Midnight Ledger

**Rationale**: The specification requires a premium distinctive UI but the
constitution forbids frontend frameworks for the MVP. Custom CSS with reusable
template components is sufficient for Midnight Ledger styling.

**Alternatives considered**:

- Bootstrap/Tailwind: rejected by user constraints.
- Minimal default Django styling: rejected because it would not meet UI/UX
  requirements.
