# Research: Banking MVP Constitution v3.0.0

## Decision: Custom User With Login Context

**Decision**: Use the existing/custom Django user model as the authenticated identity with globally unique email, display name, Django-managed password hash, and immutable MVP login context: `PERSONAL` or `BUSINESS_EMPLOYEE`.

**Rationale**: Login context is a security boundary. Keeping it on the auth identity makes Personal/Business route denial direct and testable.

**Alternatives considered**:

- Django default `User` plus profile: easier initially but splits the security boundary away from authentication.
- Separate auth models: Django supports one active user model; multiple auth models would add unnecessary complexity.

## Decision: Business Employee Access as Separate Domain Record

**Decision**: Represent Business employee scope, role, and access state with `BusinessEmployeeAccess`, linked one-to-one to a `BUSINESS_EMPLOYEE` user and many-to-one to a Business Account.

**Rationale**: A Business Employee Access Login is not a bank account. Separating login identity from employee access prevents UEN/balance/role confusion and enforces exactly one Business Account per employee login.

**Alternatives considered**:

- Reuse v2 `BusinessMembership`: conflicts with multi-account membership removal.
- Put role/status on `CustomUser`: loses direct Business Account relationship and weakens auditability.

## Decision: One Business Account Per Employee Login

**Decision**: Use a unique constraint on the employee user reference in `BusinessEmployeeAccess`, so one Business employee login can have only one access record.

**Rationale**: Constitution v3.0.0 prohibits one employee login from accessing multiple Business Accounts and removes the Business Account selector.

**Alternatives considered**:

- Multiple access rows per user: v2 model; rejected.
- Shared company login: prohibited and not auditable.

## Decision: Temporary Password Workflow

**Decision**: AUTHORISER provisioning and reset use Django password setting to hash the temporary password, then set `BusinessEmployeeAccess.access_status` to `PASSWORD_CHANGE_REQUIRED`.

**Rationale**: Django handles password hashing. The access record is the source of truth for whether the employee may use Business functionality.

**Alternatives considered**:

- Store plaintext temporary passwords for display later: prohibited.
- Store password-change state on both user and access record: creates conflicting sources of truth.

## Decision: Mandatory Password Change Gate

**Decision**: On sign-in and protected Business routes, employees in `PASSWORD_CHANGE_REQUIRED` may only access the mandatory password-change flow and sign-out.

**Rationale**: This enforces first-login activation server-side and keeps temporary credentials from being enough to operate company funds.

**Alternatives considered**:

- UI-only warning: insecure and bypassable.
- Allow read-only dashboard before change: contradicts v3 requirements.

## Decision: Deactivation/Reactivation Instead of Deletion

**Decision**: Deactivation changes access status to `DEACTIVATED` and records audit metadata. Reactivation requires a new temporary password and returns status to `PASSWORD_CHANGE_REQUIRED`.

**Rationale**: Employee actions must remain attributable. Deleting access would weaken audit history and relationship integrity.

**Alternatives considered**:

- Hard delete employee access: rejected for auditability.
- Reactivate directly to `ACTIVE`: rejected because v3 requires a new temporary password and private password change.

## Decision: Final Active AUTHORISER Protection in Service Layer

**Decision**: Enforce "at least one active AUTHORISER remains" in employee deactivation services, inside a transaction and immediately before state change.

**Rationale**: SQLite cannot reliably express this cross-row invariant with a simple constraint. Service enforcement is explicit and testable.

**Alternatives considered**:

- Database trigger: more complex and less beginner-friendly.
- Exactly one AUTHORISER: unconstitutional after v3 and v2.

## Decision: Remove Invitation Flow

**Decision**: Treat invitation models, forms, services, pages, tests, navigation, and invitation audit events as superseded and replace them with Team Access provisioning.

**Rationale**: Constitution v3.0.0 states invitations are not part of the MVP. Employees are provisioned directly and do not accept invitations.

**Alternatives considered**:

- Keep invitation code hidden: risky, could remain reachable or confuse tasks.
- Rename invitation to provisioning: misleading because semantics differ.

## Decision: Explicit Account References for Financial Records

**Decision**: Use explicit nullable PersonalAccount and BusinessAccount references in completed transactions and transfer operations, with model/service validation requiring exactly one account per side.

**Rationale**: The MVP has only two account types. Explicit references are beginner-friendly and avoid generic relation complexity.

**Alternatives considered**:

- GenericForeignKey: harder to constrain and test.
- Single shared account table: risks reintroducing old account-type ambiguity.

## Decision: Decimal Money Handling

**Decision**: Use Python `Decimal`, `DecimalField(max_digits=12, decimal_places=2)`, and one shared money parser/formatter.

**Rationale**: Decimal correctness and consistent validation are central to the constitution.

**Alternatives considered**:

- Float: rejected for financial correctness.
- Integer cents: valid, but less aligned with Django form/model readability for this beginner MVP.

## Decision: SQLite Local MVP Boundaries

**Decision**: Use Django `transaction.atomic()` for multi-row operations and document SQLite as local-only, not production banking concurrency infrastructure.

**Rationale**: SQLite is constitutionally approved and sufficient for local learning. Revalidation at completion time handles MVP multiple-PENDING behavior.

**Alternatives considered**:

- PostgreSQL or row-level locks: outside approved MVP stack.
- No transactions: unacceptable for financial and access-governance atomicity.

## Decision: Server-Rendered Midnight Ledger Redesign

**Decision**: Use Django templates, reusable includes, and custom CSS to implement a substantially redesigned Midnight Ledger interface.

**Rationale**: The stack prohibits frontend frameworks and external CSS frameworks, but custom CSS and server-rendered pages can meet the premium UI requirements.

**Alternatives considered**:

- React/Vue/HTMX: outside scope.
- Bootstrap/Tailwind: outside scope.
- Functional-only CRUD UI: rejected by v3 UX requirements.

## Decision: Superseded Migration/Data Strategy

**Decision**: Because this is a local learning MVP with no approved preservation requirement, prefer resetting local SQLite data and replacing superseded development migrations with fresh v3 migrations during implementation.

**Rationale**: The v3 model removes invitations and multi-memberships and changes employee access semantics enough that local preservation is more complex than useful.

**Alternatives considered**:

- Forward migration: only needed if committed migration history must be preserved by later repository policy.
- Preserve local data: no requirement exists and would retain obsolete semantics.
