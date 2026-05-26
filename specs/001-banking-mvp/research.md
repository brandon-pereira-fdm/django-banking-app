# Research: Banking MVP Constitution v2.0.0

## Decision: Custom User Model With Exclusive Access Context

**Decision**: Keep/use a custom Django user model with unique email login, username display name, Django password hashing, and required `access_context` choice of `PERSONAL` or `BUSINESS`.

**Rationale**: Constitution v2.0.0 makes access context a core identity invariant. A custom user model from the beginning keeps email login, global email uniqueness, and Personal/Business separation explicit and testable.

**Alternatives considered**:

- Django default `User` plus profile model: simpler initially, but access context would be split away from authentication identity and is easier to bypass accidentally.
- Two separate user models: Django does not support multiple active auth user models cleanly; it would increase complexity.

## Decision: Separate PersonalAccount and BusinessAccount Models

**Decision**: Use concrete `PersonalAccount` and `BusinessAccount` models rather than a single account table with type-specific nullable fields.

**Rationale**: Personal and Business accounts now have different access rules. Personal Accounts are one-to-one with a `PERSONAL` user and receive transfers by phone. Business Accounts are company-owned shared accounts with memberships and receive transfers by UEN. Separate models make constraints and UI flows clearer for a beginner-friendly Django MVP.

**Alternatives considered**:

- One `Account` model with account type discriminator: convenient for balances but creates many nullable fields and risks reintroducing shared ownership assumptions.
- Generic foreign keys everywhere: flexible but harder to validate and less beginner-friendly.

## Decision: Explicit Dual Account References for Money Records

**Decision**: Completed financial transactions and transfer operations use explicit nullable references to `PersonalAccount` and `BusinessAccount`, with validation requiring exactly one account where applicable.

**Rationale**: Transfers can involve either account type. Explicit fields avoid generic relations while allowing services to enforce "exactly one sender" and "exactly one recipient" rules.

**Alternatives considered**:

- GenericForeignKey: less transparent and harder to enforce with database constraints.
- Reintroducing a shared base table: simpler for transactions but weaker for Personal/Business-specific invariants.

## Decision: Business Membership With Soft Removal

**Decision**: Model Business access through `BusinessMembership` with role `MEMBER` or `AUTHORISER`, active status, and `removed_at` timestamp rather than deleting memberships.

**Rationale**: Removed users must immediately lose access, while access governance remains auditable. Filtering active memberships enforces access loss; historical rows support audit and attribution.

**Alternatives considered**:

- Delete memberships on removal: simple but loses governance history.
- Store only audit events and no inactive membership rows: audit remains, but permission history and duplicate-membership handling are harder.

## Decision: Invitation Acceptance Without Email Delivery

**Decision**: Store `BusinessInvitation` records addressed to email with intended role. Acceptance occurs through server-rendered in-app invitation pages or invitation-specific entry links/IDs. Actual outbound email delivery is excluded.

**Rationale**: The specification requires invitation workflow but excludes email infrastructure. Stored invitations let existing Business users accept matching invites and new users register from an invite without adding external services.

**Alternatives considered**:

- SMTP or third-party email provider: explicitly out of MVP scope.
- Automatically granting access on invite: violates access-begins-only-after-acceptance rule.

## Decision: Duplicate Pending Invitation Rule

**Decision**: Prevent multiple `PENDING` invitations for the same Business Account and invited email. Accepted or cancelled invitations remain historical and do not block a future invitation.

**Rationale**: This keeps the MVP deterministic without needing expiry, reminder, or invitation deduplication UX.

**Alternatives considered**:

- Allow unlimited duplicates: confusing for acceptance and audit.
- Expire old invites automatically: adds timing behavior not required by the spec.

## Decision: Invitation Expiry Excluded

**Decision**: Invitation statuses are `PENDING`, `ACCEPTED`, and `CANCELLED`; `EXPIRED` is excluded from the MVP.

**Rationale**: The constitution and spec do not require expiry. Excluding it avoids scheduled cleanup, time-window messaging, and additional edge cases.

**Alternatives considered**:

- Add expiry: useful in production, but expands product behavior beyond the approved MVP.

## Decision: Unlimited AUTHORISERS With Last-AUTHORISER Protection

**Decision**: Allow any number of active AUTHORISER memberships and enforce "at least one active AUTHORISER remains" during removal.

**Rationale**: Constitution v2.0.0 explicitly removes the exactly-one-authoriser model and requires last-AUTHORISER protection. A service-layer check is mandatory because SQLite constraints alone cannot easily express this cross-row invariant.

**Alternatives considered**:

- Exactly one AUTHORISER: unconstitutional after v2.0.0.
- Configurable approval thresholds: out of MVP scope.

## Decision: Access Audit History as Separate Immutable Event Stream

**Decision**: Add `BusinessAccessAuditEvent` for account creation, initial AUTHORISER assignment, invitation issuance/acceptance, role assignment, promotion, removal, and retained invalid governance attempts.

**Rationale**: Access-governance history must be distinct from financial Transaction History and outgoing-request Approval History.

**Alternatives considered**:

- Store access events inside Transaction History: violates history separation.
- Only infer from membership/invitation records: loses explicit actor/outcome chronology.

## Decision: Transfer Recipient Resolution by Selected Account Type

**Decision**: Transfer forms require destination account type first. Personal destinations resolve by phone number; Business destinations resolve by UEN. Mismatches and unknown identifiers are rejected before money moves or a Business request is created.

**Rationale**: This is required by the constitution and avoids ambiguous identifiers between Personal and Business accounts.

**Alternatives considered**:

- Try both phone and UEN automatically: weaker confirmation model and conflicts with explicit recipient type selection.

## Decision: Decimal Money Handling

**Decision**: Use Python `Decimal`, Django `DecimalField(max_digits=12, decimal_places=2)`, and a single money validation helper.

**Rationale**: Decimal avoids floating-point error and a shared helper prevents inconsistent validation across deposits, withdrawals, transfers, opening deposits, and approval revalidation.

**Alternatives considered**:

- Float: unconstitutional for money.
- Store cents as integers: valid, but Django `DecimalField` is more readable for a beginner MVP and matches form validation needs.

## Decision: Service Layer for Financial and Membership Rules

**Decision**: Implement domain services in `banking/services/` for money validation, account creation, invitations, memberships, transfers, and approvals.

**Rationale**: The spec requires server-side enforcement. Keeping rules out of views/forms improves traceability and makes atomicity/test coverage clearer.

**Alternatives considered**:

- Put logic in forms/views: too easy to bypass and hard to test consistently.
- Heavy domain framework or repository layer: unnecessary for MVP.

## Decision: SQLite Atomicity Boundaries

**Decision**: Use Django `transaction.atomic()` around multi-row state changes and re-read balances/memberships before final financial or governance completion.

**Rationale**: SQLite supports local transactional correctness for the MVP. Revalidation at completion time is required for multiple PENDING Business requests and last-AUTHORISER protection.

**Alternatives considered**:

- PostgreSQL or row-level locking: more production-ready but outside approved MVP stack.
- No transaction boundaries: risks partial balances, records, or audit state.

## Decision: Server-Rendered Midnight Ledger UI With Custom CSS

**Decision**: Use Django templates, reusable includes, and custom CSS for the Midnight Ledger interface. No frontend framework or external CSS framework.

**Rationale**: The approved stack is server-rendered Django. The premium UI can be achieved with custom CSS, template inheritance, and server-rendered confirmation flows.

**Alternatives considered**:

- React/Vue/Angular, Bootstrap, Tailwind: explicitly outside MVP scope.
- JavaScript-required form steps: not allowed for core flows.

## Decision: Superseded Implementation Reset Strategy

**Decision**: For local MVP development, regenerate tasks for v2.0.0 and replace superseded migrations/schema assumptions. Reset the local SQLite development database before continuing implementation unless a separate preservation requirement is introduced.

**Rationale**: The v2 amendment changes user/account ownership, Business Account authorisation, memberships, and audit history fundamentally. A local reset is simpler, safer, and consistent with the learning MVP context.

**Alternatives considered**:

- Forward migrations from the superseded schema: possible, but not worth the complexity unless preserving local development data becomes a requirement.
