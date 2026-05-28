<!--
Sync Impact Report
Version change: 3.0.0 -> 4.0.0
Modified principles:
- I. MVP Technology and Scope -> I. MVP Technology, Scope, and Local MCP Boundary
- X. Transaction, Approval, and Access History Separation -> X. Transaction, Approval, Access, and AI Activity History Separation
- XI. Transaction Auditability and Immutability -> XI. Transaction Auditability, Immutability, and Initiation Channels
- XII. Automated Testing and Quality Gates -> XII. Automated Testing and Quality Gates
- XIII. Security and Secrets Management -> XIII. Security, Secrets, and MCP Token Management
- XIV. Governance and SDD Compliance -> XIV. Governance and SDD Compliance
Added sections:
- Amendment 4.0.0 Controlled MCP AI Banking Assistant Governance
Removed sections:
- None
Templates requiring updates:
- .specify/templates/plan-template.md: pending by explicit user request to
  produce the amended constitution only.
- .specify/templates/spec-template.md: pending by explicit user request to
  produce the amended constitution only.
- .specify/templates/tasks-template.md: pending by explicit user request to
  produce the amended constitution only.
- .specify/templates/checklist-template.md: pending by explicit user request
  to produce the amended constitution only.
- .specify/templates/constitution-template.md: reviewed; no project-specific
  amendment applied because this command is constitution-only.
Runtime guidance requiring updates:
- README.md: pending if local MCP setup commands are later specified.
- specs/001-banking-mvp/plan.md: pending v4 planning update.
- specs/001-banking-mvp/spec.md: pending v4 specification update.
Follow-up TODOs:
- Update specification, checklist, plan, data model, contracts, tasks,
  traceability, and implementation artifacts for local stdio MCP, scoped
  short-lived tokens, prepared actions, AI Activity Audit, MCP Assistant channel
  labels, and explicit MCP exclusions before implementation begins.
- Select the concrete local-MVP token lifetime, token handling approach,
  prepared-action expiry policy, audit retention policy, and MCP invocation
  throttling strategy in the later specification and technical plan.
-->
# BankApp Constitution

## Core Principles

### I. MVP Technology, Scope, and Local MCP Boundary
The MVP MUST use Python 3.11 or later, Django, SQLite3, Django templates,
custom CSS, Django built-in authentication, Django forms, Django transactions,
Django migrations, Django tests, and Waitress for simple local macOS execution.
All monetary values and transactions MUST be restricted to Singapore Dollars
(SGD) only.

The MVP MAY include an optional local Model Context Protocol (MCP) AI Banking
Assistant extension. The initial MCP implementation MUST be local-only, use a
`stdio` transport, remain client-neutral, and be testable with an
MCP-compatible inspection or testing client. The MCP server MUST be part of the
existing Django banking project or an adjacent project module that imports and
uses the existing Django models and services.

The MCP extension MAY add only the minimum local MCP server support required
for a stdio learning MVP and later approved technical plan. The MCP extension
MUST NOT introduce public Streamable HTTP deployment, remote cloud hosting,
OAuth or external identity providers, external AI-hosting dependencies, real
banking integrations, autonomous financial decision-making, or MCP-based
credential administration.

The MVP MUST NOT introduce alternative databases, frontend frameworks, external
CSS frameworks, payment gateways, external bank integrations, cloud
infrastructure, microservices, message queues, WebSockets, third-party
authentication systems, OTP verification, email-delivery infrastructure, or
external UEN registry verification without constitutional amendment.

The MVP scope MUST remain limited to registration, authentication, Personal
Account access, Business Account access, Authoriser-provisioned employee access
credentials, role management, temporary-password change and reset flows,
deactivation and reactivation, deposits, withdrawals, transfers, outgoing
Business approval workflow, Transaction History, Approval History, Access Audit
History, optional AI Assistant Access, MCP prepared-action review, AI Activity
Audit, automated tests, traceability, and local deployment.

The MCP extension is a local learning-MVP feature. It MUST NOT be represented
as safe for real public banking use.

Rationale: A narrow local-first stack keeps the SDD MVP auditable, testable,
and focused on proving banking and access-governance rules before architecture
expansion. MCP is allowed only as a controlled local channel layered over the
existing web application and services.

### II. Financial Correctness and Money Validation
All balances and monetary operations MUST use precise decimal arithmetic. The
application MUST never use floating-point arithmetic for money.

Deposits, withdrawals, opening deposits, and transfers MUST reject zero,
negative, malformed, non-numeric, non-SGD, over-capacity, or invalid-precision
values. Monetary values MUST support no more than two decimal places. Any
operation that would result in a negative account balance MUST be prevented.
Rejected or failed financial operations MUST NOT modify balances and MUST NOT
be recorded as completed financial transactions.

MCP preview and prepared-action flows MUST use the same Decimal validation,
recipient resolution, balance checks, retained-minimum checks, transaction
boundaries, and existing banking services as web-initiated operations. MCP
tools MUST NOT implement separate banking rules and MUST NOT write directly to
balances outside approved services.

Rationale: Banking correctness depends on exact SGD arithmetic, strict amount
validation, unchanged state after failed operations, and one authoritative
service layer for web and MCP channels.

### III. Account and Login Model
The application supports exactly two bank-account products: Personal Account
and Business Account.

A Personal Account is an individual bank account with its own Personal login
credentials. A Business Account is a company-owned bank account with one or
more individual employee access logins. An employee access login is not itself
a Personal Account and is not itself a separate Business Account.

A Personal Account login MUST access Personal Account functionality only. A
Business employee access login MUST access Business Account functionality only.
A Business employee access login MUST NOT access Personal Account functionality.
A Personal Account login MUST NOT access Business Account functionality.

A Business employee access login belongs to exactly one Business Account. The
same Business employee login MUST NOT access multiple Business Accounts. If an
individual works with more than one company Business Account in this MVP,
separate employee access credentials MUST be created for each Business Account
using different unique email addresses.

A real individual who separately needs a Personal Account and employee access
to a Business Account MUST use separate login credentials and different unique
email addresses. Email addresses MUST remain unique login identifiers across
the whole application.

Shared Business Account credentials are prohibited. Each employee MUST have
their own assigned login identity. Passwords MUST be stored using Django
authentication and password hashing facilities and MUST never be stored in
plaintext.

An MCP token MUST be scoped to exactly one authenticated identity and account
context: either one Personal Login and its Personal Account, or one active
Business Employee Access Login and its assigned Business Account. MCP MUST NOT
alter account product types, login contexts, or cross-account boundaries.

Rationale: Personal banking, company ownership, employee access, and MCP
session context are separate accountability contexts. One login or token must
not blur those boundaries.

### IV. Personal Account Model
Personal Account registration MUST require a user-selected username, unique
email login, securely stored password, and one unique phone number used for
receiving transfers.

A Personal Account MUST NOT require an opening deposit and MUST begin with
balance SGD 0.00 unless funds are later deposited or received. A Personal
Account has no minimum-balance requirement.

A Personal Account MAY deposit, withdraw, and make outgoing transfers only when
the amount is valid and greater than zero. A Personal Account withdrawal or
outgoing transfer MAY leave the account at SGD 0.00, but MUST NOT cause the
balance to become negative. A Personal Account receives incoming transfers
using its unique phone number.

Successful Personal Account deposits, withdrawals, and outgoing or incoming
transfers MUST be auditable through immutable completed financial transaction
records.

Through MCP, a Personal Login MAY read safe account information, preview
deposits and outgoing transfers, and create prepared deposits or prepared
outgoing transfers for its own Personal Account only. MCP MUST NOT complete
money movement without Midnight Ledger web-app confirmation.

Rationale: Personal accounts are individual SGD accounts with no retained
minimum, but they still require exact validation, unique recipient identity,
auditable financial movement, and explicit human confirmation for MCP writes.

### V. Business Account Registration and Employee Access
A Business Account is a separate company-owned account. A Business Account MUST
NOT be owned or authorised by a Personal Account.

A new Business Account MUST be created by its initial AUTHORISER. Business
Account registration MUST require the initial Authoriser's display name or
username, the initial Authoriser's unique login email, the initial Authoriser's
password, business display name, one unique company UEN used for receiving
transfers, and an opening deposit of at least SGD 7,000.00.

Successful Business Account creation MUST atomically create the Business
Account, the initial AUTHORISER employee-access login scoped only to that
Business Account, the completed Business opening-deposit financial transaction,
an Access Audit event for account creation, and an Access Audit event for
initial AUTHORISER creation.

The initial AUTHORISER login is not a separate Business Account and MUST NOT
access any other Business Account. A Business Account MUST maintain at least
one active AUTHORISER employee access login at all times.

Business Accounts receive incoming transfers using unique UEN values. Deposits
and incoming transfers into a Business Account do not require approval and MAY
increase its balance. Every completed outgoing Business withdrawal or transfer
MUST leave at least SGD 7,000.00 in the Business Account.

Through MCP, an active Business employee MAY interact only with their assigned
Business Account and only within their existing role and access status.
`PASSWORD_CHANGE_REQUIRED` and `DEACTIVATED` Business Employee Access Logins
MUST NOT generate or use MCP access tokens and MUST NOT prepare or confirm MCP
deposits, requests, transfers, or cancellations.

Rationale: Business banking represents company funds governed by individual
employee credentials scoped to the company account, not by Personal Account
ownership, reusable multi-company login identities, or AI-mediated elevation.

### VI. Business Employee Access Credentials
Invitations are not part of the MVP. Existing bank customers or account holders
MUST NOT be added to a Business Account through invitation acceptance.

Only an active AUTHORISER MAY create a new employee access login for their
Business Account. Creating employee access MUST require employee display name,
unique login email, assigned role of MEMBER or AUTHORISER, temporary password,
and temporary password confirmation.

The employee access login MUST be scoped to exactly one Business Account. The
employee access login MUST be inactive for normal financial operation until the
employee signs in and changes the temporary password.

Temporary passwords MUST be securely hashed and MUST never be stored in
plaintext. Temporary passwords MAY be shown or communicated only at initial
assignment as necessary for local MVP use and MUST NOT be retrievable afterward.

The application MUST require the employee to change the temporary password at
first sign-in before accessing Business Account balances, histories, deposits,
request actions, approvals, or management actions. After the employee changes
the temporary password, the Authoriser MUST NOT know, recover, or view the
employee's new password.

MCP MUST NOT expose tools for adding employee access, resetting temporary
passwords, changing passwords, promoting employees, deactivating employees,
reactivating employees, displaying Team Access credentials, or administering
credential data.

Rationale: Company employees receive assigned, accountable access credentials
for one Business Account instead of joining as independent bank customers,
sharing company credentials, or delegating credential governance to an AI tool.

### VII. Business Access State, Password Resets, and Audit History
A Business employee access login MUST have an access state sufficient to
represent pending first-login password change, active, and deactivated.

Only an active AUTHORISER MAY issue a new temporary password for another
employee access login in the same Business Account. Issuing a new temporary
password MUST require the employee to change password again at the next sign-in
before accessing banking functionality. Password reset MUST NOT display,
recover, or reveal the user's existing password.

Only an active AUTHORISER MAY deactivate or reactivate employee access. A
deactivated employee MUST immediately lose access to the Business Account and
MUST NOT initiate, submit, approve, reject, cancel, or action transactions.
Reactivation MAY require issuing a new temporary password according to the
technical plan.

Employee access records MUST NOT be deleted through ordinary user workflows
because their actions must remain auditable.

Access Audit History MUST record Business access and security-governance
events, including Business Account creation, initial AUTHORISER creation,
employee access created, temporary password issued, first-login password
changed or access activated, MEMBER promoted to AUTHORISER, employee access
deactivated, employee access reactivated, temporary password reset issued, and
rejected attempts to deactivate the final AUTHORISER where retained for audit.

Access Audit History MUST never reveal password values, password hashes, or
secret credentials. AI Activity Audit MUST be used for MCP token and
prepared-action activity rather than mixing AI session events into Access Audit
History, except where later traceability deliberately links related records.

Rationale: Employee access lifecycle events change who can act on company
funds, so they require explicit state, server-side enforcement, and audit
records that do not expose credentials.

### VIII. Business Roles, Permissions, and Approval
The MVP MUST define exactly two Business employee access roles: MEMBER and
AUTHORISER.

A MEMBER with active access MAY view the Business Account balance, view
completed Transaction History, view Approval History, view Access Audit
History, make valid deposits into the Business Account without approval, submit
outgoing withdrawal requests, submit outgoing transfer requests, and cancel
their own PENDING outgoing requests.

A MEMBER MUST NOT approve or reject requests, cancel another employee's
request, create employee access, reset another user's password, deactivate or
reactivate users, promote users, remove users, alter users, or assign roles.

An AUTHORISER with active access has all MEMBER capabilities. An AUTHORISER MAY
also approve any PENDING outgoing Business withdrawal or transfer, reject any
PENDING outgoing Business withdrawal or transfer, cancel any PENDING outgoing
request including their own, create MEMBER or AUTHORISER employee access
logins, reset an employee's password using a new temporary password, promote a
MEMBER to AUTHORISER, deactivate or reactivate an employee access login, and
deactivate another AUTHORISER only when at least one other active AUTHORISER
remains.

An AUTHORISER MUST NOT demote an AUTHORISER to MEMBER in the MVP. An AUTHORISER
MUST NOT deactivate the final remaining active AUTHORISER. An AUTHORISER MUST
NOT access, recover, or reveal another employee's chosen password after
first-login password change.

Any MEMBER or AUTHORISER with active access to a Business Account MAY submit an
outgoing Business withdrawal or transfer request. Submission MUST create a
PENDING request only. A PENDING request MUST NOT move money, reserve funds,
reduce displayed balance, or create completed financial transaction records.

Any one active AUTHORISER approval is sufficient to approve and complete a
valid outgoing Business request. An AUTHORISER MAY approve a request they
submitted themselves. An AUTHORISER MAY reject any PENDING request. A MEMBER
MAY cancel only their own PENDING request. An AUTHORISER MAY cancel any PENDING
request, including their own, through the web application only.

Through MCP, a Business MEMBER token MUST retain MEMBER restrictions. A
Business AUTHORISER token MAY expose approved AUTHORISER read visibility for
pending requests requiring attention and safe approval-preview information, but
MUST NOT permit MCP approval, rejection, Team Access administration, credential
actions, or cancellation of another employee's request.

The only persisted outgoing-request statuses are PENDING, COMPLETED, REJECTED,
CANCELLED, and FAILED. There is no separately persisted APPROVED status.
Approval is an action applied to a PENDING request.

When approval succeeds and all financial validations pass, the request changes
directly from PENDING to COMPLETED and money movement completes atomically. If
approval is attempted but current rules fail, including the SGD 7,000.00
retained-minimum rule, the request changes from PENDING to FAILED and no money
moves. Only PENDING requests MAY be approved, rejected, or cancelled.
COMPLETED, REJECTED, CANCELLED, and FAILED requests are final.

Multiple PENDING outgoing requests MAY exist simultaneously. Each PENDING
request MUST be independently revalidated at approval time.

Rationale: Business outgoing funds require active employee status, role-based
approval, current-state financial revalidation, no fund reservation while
pending, and a clear lifecycle without an APPROVED stored state. MCP must not
weaken that human governance.

### IX. Transfers and Linked Transaction Records
Personal Accounts receive transfers using unique phone numbers. Business
Accounts receive transfers using unique UEN values. A sender MUST select
whether the destination is a Personal Account or Business Account. The entered
identifier MUST match the destination account type: phone number for Personal
Account destination and UEN for Business Account destination.

Unknown identifiers and identifier/account-type mismatches MUST be rejected.
Transfers from a Personal Account are performed by the Personal login identity
owning that account. Transfers from a Business Account are requested by an
active MEMBER or AUTHORISER employee access login for that Business Account and
require AUTHORISER approval before completion.

A transfer from an account back to the same account MUST be rejected. Old rules
rejecting transfers because one user owned both Personal and Business contexts
MUST NOT be reintroduced.

Every successfully completed transfer MUST create one unique transfer operation
ID, one immutable sender debit financial transaction record, and one immutable
recipient credit financial transaction record. The sender debit record and
recipient credit record MUST each have their own UUID transaction ID and MUST
reference the same transfer operation ID.

Sender debiting, recipient crediting, transfer operation creation, and
transaction-record creation MUST be atomic: either all changes succeed or none
occur.

MCP transfer preview and prepared transfer flows MUST validate destination
account type, phone-number or UEN recipient resolution, amount validity,
current available balance, retained-minimum rules where applicable, and
self-transfer prohibition. MCP preparation MUST NOT create a completed transfer
operation or completed financial transaction.

Rationale: Recipient identity differs by account type, while completed transfer
records must remain linked, auditable, atomic, and protected from AI-only
completion.

### X. Transaction, Approval, Access, and AI Activity History Separation
The application MUST provide four logically distinct audit-facing views.

Transaction History MUST display completed financial movements only, including
deposits, completed withdrawals, completed transfer debits, completed transfer
credits, and Business Account opening deposits.

Approval History MUST display Business Account outgoing withdrawal and transfer
requests and their workflow statuses: PENDING, COMPLETED, REJECTED, CANCELLED,
and FAILED.

Access Audit History MUST display Business access and security-governance
activity, including Business Account creation, initial AUTHORISER creation,
employee access creation, temporary-password issuance, first-login password
change or access activation, MEMBER promotion, employee deactivation, employee
reactivation, temporary-password reset issuance, and rejected final-AUTHORISER
deactivation attempts where retained for audit.

AI Activity Audit MUST display safe MCP-session, tool, and prepared-action
activity. It MUST be separate from Transaction History, Approval History, and
Access Audit History.

Non-completed workflow records, access records, AI session records, and
prepared MCP actions MUST NOT be represented as completed financial movements.
Access Audit History and AI Activity Audit MUST NOT display password values,
password hashes, temporary password values after initial assignment, raw MCP
tokens, token hashes, secret keys, or unnecessary unmasked personal
identifiers.

Completed MCP-originated financial actions MUST also show their channel as
`MCP Assistant` in Transaction History. MCP-originated Business request
submissions or cancellations MUST show their channel in Approval History. AI
Activity Audit MUST never be confused with completed financial movement.

Rationale: Financial audit, outgoing-request workflow, access governance, and
AI-mediated activity answer different accountability questions and must remain
separate.

### XI. Transaction Auditability, Immutability, and Initiation Channels
Every successful deposit and completed withdrawal MUST have an immutable
financial transaction record with a UUID transaction ID. Every successfully
completed transfer MUST produce two immutable linked financial transaction
records joined by one transfer operation ID. Completed financial transaction
records MUST NOT be editable through application logic.

Completed financial transaction records MUST include at minimum a UUID
transaction ID, transaction type, amount in SGD, associated account, completion
timestamp, transaction status, transfer operation ID where applicable, and a
safe initiation channel where required by the feature.

Rejected, CANCELLED, FAILED, or still-PENDING outgoing requests MUST NOT move
funds or create completed financial transaction records.

Completed MCP-originated deposits and Personal transfers MUST identify the
initiation channel as `MCP Assistant`. Completed confirmation of an
MCP-prepared Business request submission or eligible cancellation MUST identify
the origination channel as `MCP Assistant` in Approval History.

Rationale: Completed financial history must be complete, immutable, and clearly
separated from pending, failed, workflow, access, and AI preparation records.

### XII. Automated Testing and Quality Gates
Automated tests are mandatory for core banking, employee access, security, MCP,
and audit behaviour. A feature with failing mandatory tests MUST NOT be treated
as complete.

Mandatory tests MUST cover Personal registration and Personal-only access;
Business Account registration and initial AUTHORISER employee access creation;
absence of active invitation behaviour; AUTHORISER creation of MEMBER access
with temporary password; AUTHORISER creation of AUTHORISER access with
temporary password; MEMBER inability to create employee access; new employee
denial from Business functionality until changing the temporary password;
temporary password change activating normal access; password values not exposed
or retrievable; active MEMBER permissions; active AUTHORISER permissions;
MEMBER promotion; MEMBER deactivation; AUTHORISER deactivation only when
another active AUTHORISER remains; rejection of final active AUTHORISER
deactivation; deactivated employee immediate access loss; password reset
issuing a new temporary password and requiring password change again;
reactivation behaviour; one Business Account per employee login; and Access
Audit events for account creation, access creation, password reset, password
activation or change, promotion, deactivation, and reactivation.

Mandatory tests MUST also cover Personal Account creation at SGD 0.00 with
unique phone number; Personal deposits, withdrawals, full-balance withdrawal,
outgoing transfers, and negative-balance rejection; Business Account creation
with unique UEN and opening deposit of at least SGD 7,000.00; duplicate UEN
rejection; MEMBER and AUTHORISER deposits without approval; MEMBER and
AUTHORISER outgoing request submission; MEMBER inability to approve or reject;
AUTHORISER approval of any PENDING request; one AUTHORISER approval being
sufficient; AUTHORISER self-approval; MEMBER cancellation of own PENDING
request only; AUTHORISER cancellation of any PENDING request through the web
application; multiple PENDING requests and approval-time revalidation; Business
retained-minimum failure changing request to FAILED without money movement;
Personal phone recipient lookup; Business UEN recipient lookup; unknown
recipient rejection; identifier type mismatch rejection; UUID transaction IDs;
shared transfer operation IDs; atomic rollback on failed financial operations;
Transaction History containing completed financial events only; Approval
History containing outgoing Business requests only; and Access Audit History
containing access-governance events only.

Mandatory MCP tests MUST cover scoped token generation, one-time raw token
display where applicable, non-recoverable token storage, expiry, revocation,
revoked-token rejection, user isolation for token metadata, permission
non-elevation, Personal and Business read scope, AUTHORISER-only MCP pending
review visibility, MEMBER denial from AUTHORISER visibility, preview tools with
no money movement or completed records, sanitised outputs, prepared Personal
and Business deposits, prepared Personal transfers, prepared Business
withdrawal and transfer requests, prepared own-request Business cancellation,
web-app confirmation revalidation, rejection of expired or revoked prepared
actions, no MCP approvals or rejections, MCP Assistant channel labels, AI
Activity Audit safety, and absence of token, password, hash, and secret
exposure.

Rationale: The MVP cannot claim banking, access-governance, MCP, or audit
correctness unless employee access state, role permissions, money movement,
approval workflow, prepared-action lifecycle, token scope, audit separation,
and rollback behaviours are tested.

### XIII. Security, Secrets, and MCP Token Management
Secrets and sensitive configuration MUST NOT be committed to GitHub. Django
secret keys, plaintext passwords, temporary passwords, password hashes, raw MCP
tokens, token hashes, private credentials, environment files containing
secrets, MCP server configuration containing secrets, and local SQLite database
files MUST NOT be committed.

Secret configuration MUST be stored in environment variables or ignored local
files. An appropriate `.gitignore` MUST exist before creating local secrets,
SQLite database files, collected local static files, Python virtual
environments, MCP access tokens, or MCP server configuration containing
secrets.

Authentication MUST use securely hashed passwords. Personal Account logins and
Business employee access logins MUST remain separate. Business Accounts MUST
use individual employee access logins and MUST NOT rely on shared credentials.

Temporary passwords MUST be hashed and MUST NOT be retrievable after initial
assignment. Mandatory first-login password change MUST be enforced
server-side. Deactivated employees MUST NOT access Business functionality.

Only active AUTHORISERS MAY create credentials, reset temporary passwords,
promote users, deactivate users, or reactivate users. The final active
AUTHORISER MUST NOT be deactivated. Permission enforcement MUST NOT rely on UI
hiding alone.

An AI client MUST NOT authenticate by receiving a user's login password and
MUST never receive Personal Login passwords, Business Employee Access
passwords, temporary employee passwords, password hashes, Django secret keys,
Team Access credential data, raw stored token representations, or any other
credential-management material.

MCP tool inputs MUST be validated server-side. MCP tool outputs MUST be
sanitised and minimised. Every MCP tool invocation MUST enforce
authentication, token scope, user context, account access, role, access status,
and action eligibility. MCP tool errors MUST NOT expose internal secrets,
credential data, database details, or unauthorised account existence.

MCP writes MUST require Midnight Ledger web-app confirmation and MUST NOT
depend solely on AI-client confirmation. MCP write confirmations MUST use the
same Django financial and permission services as existing web actions. Tool
invocations MUST be logged or auditable according to the approved AI Activity
Audit design. The server MUST implement sensible local-MVP rate limiting or
invocation throttling where specified in the technical plan.

Rationale: Local MVP deployment still requires credential hygiene, identity
separation, role-based access protection, server-side enforcement, and careful
containment of an AI-mediated interface that can read financial data and
prepare limited actions.

### XIV. Governance and SDD Compliance
This constitution is the highest-authority project document for non-negotiable
banking, identity, employee-access-governance, MCP, audit, and engineering
rules. Every later specification and technical plan MUST include a Constitution
Check.

Every business rule MUST remain traceable from constitution to specification,
acceptance criteria, technical plan, implementation task, code component, and
automated test.

Specifications and plans MUST use identifiers such as `FR-###` for functional
requirements, `BR-###` for business rules, `SEC-###` for security requirements,
`NFR-###` for non-functional requirements, and `TEST-###` for mandatory tests.
Test names or associated traceability documentation MUST reference the banking
rule or requirement being verified.

A constitutional amendment is required for any change to the MVP technology
stack, SGD-only currency restriction, Personal Account login model, Business
employee access login model, account types, Personal Account no-minimum-balance
rule, Business Account opening-deposit or retained-minimum rule, Business
employee roles, temporary-password rules, employee access state rules,
authorisation lifecycle, transfer recipient identifiers, transfer recording,
transaction/approval/access/AI-activity history separation, security
obligations, MCP transport or deployment boundary, MCP token model, MCP write
confirmation rule, testing obligations, traceability obligations, or MVP scope.

Semantic versioning MUST be applied as follows: MAJOR for removing or
fundamentally redefining a core principle or banking, identity,
employee-access, authorisation, MCP, confirmation, token, or audit invariant;
MINOR for adding a mandatory principle or materially expanding scope; PATCH for
clarifications that do not change required behaviour.

Rationale: SDD artifacts must remain subordinate to the constitution, and
changes to banking, MCP, or access-governance invariants must be intentional,
reviewed, and versioned.

## Amendment 3.0.0 Authoriser-Provisioned Employee Access Governance

This amendment replaces the version 2.0.0 invitation-and-membership onboarding
model. Invitations, invitation acceptance, existing Business-user membership
acceptance, and one Business login joining multiple Business Accounts are no
longer valid MVP behaviours.

A Business Account now has employee access logins provisioned by an active
AUTHORISER of that Business Account. Each employee access login is scoped to
exactly one Business Account. Employees do not create separate Business
Accounts or join as existing bank-account users to gain access to a company
Business Account.

This amendment introduces temporary-password provisioning, mandatory
first-login password change, temporary-password reset, active/deactivated
access state, deactivation and reactivation governance, one Business Account
per employee login, and Access Audit events for access and password-governance
activity.

All later artifacts MUST remove or replace active statements, models, services,
forms, routes, templates, tests, or tasks implying Business invitations,
invitation acceptance, a Business user accepting membership in multiple
Business Accounts, a Business Account selector for employee logins, shared
Business credentials, or Personal Account authorisation of Business Accounts.

## Amendment 4.0.0 Controlled MCP AI Banking Assistant Governance

This amendment adds an optional AI-mediated banking interaction channel through
a local MCP server. The existing version 3.0.0 banking product remains
authoritative for Personal Accounts, Business Accounts, Business Employee
Access, Team Access, password handling, approval workflows, histories, UI/UX,
security, and local deployment. MCP MUST operate as an extension of Midnight
Ledger and MUST NOT become an independent banking system.

### Amendment Purpose and Technology Direction
The MCP integration exists to let an authenticated human user interact
conversationally with controlled banking functions: viewing their account
summary, viewing recent completed transactions, previewing transfers or
Business requests, preparing deposits, preparing Personal Account transfers,
preparing Business withdrawal or transfer requests, preparing cancellation of
the user's own eligible PENDING Business request after confirmation, and
allowing an AUTHORISER to view Pending requests requiring attention.

The initial MCP server MUST use local `stdio` transport, remain client-neutral,
and be independently testable with an MCP-compatible inspection or testing
client. The MCP server MUST import and use existing Django models, service
layer functions, permission checks, validation rules, and transaction
boundaries. It MUST NOT implement separate banking rules or write directly to
balances outside approved services.

This amendment MUST NOT introduce public Streamable HTTP deployment, remote
cloud hosting, OAuth or external identity providers, external AI-hosting
dependencies, real banking integrations, autonomous financial decision-making,
MCP-based credential administration, or MCP-based Business approval decisions.

### Human Identity and MCP Session Authentication
A user MUST authenticate through the existing Midnight Ledger web application.
After normal authentication, an eligible user MAY generate a short-lived,
revocable MCP access token from a web-app area such as `AI Assistant Access`.
The token represents the authenticated human user's authorised application
context and MUST NOT elevate permissions.

An AI client MUST NOT authenticate by receiving a user's login password. An AI
client MUST never receive Personal Login passwords, Business Employee Access
passwords, temporary employee passwords, password hashes, Django secret keys,
or Team Access credential data.

An MCP token MUST be scoped to exactly one authenticated identity: one Personal
Login and its Personal Account, or one active Business Employee Access Login
and its assigned Business Account. A Business MEMBER token MUST retain MEMBER
restrictions. A Business AUTHORISER token MAY expose approved AUTHORISER read
visibility but MUST NOT permit MCP approval, rejection, Team Access
administration, or credential actions.

`PASSWORD_CHANGE_REQUIRED` and `DEACTIVATED` Business Employee Access Logins
MUST NOT generate or use MCP access tokens. Tokens MUST be revocable by the
user from Midnight Ledger. Only a non-reversible token hash or equivalent safe
representation MAY be retained in application storage. Token issuance,
revocation, attempted use after revocation, and relevant authentication
failures MUST be auditable.

The later specification and technical plan MUST define a concrete token
lifetime. The lifetime MUST be explicitly short-lived and configurable for the
local MVP.

### MCP Access Scope by Existing User Type
A Personal Login with a valid MCP token MAY use approved MCP functionality only
for their own Personal Account. A Personal MCP context MAY read its own safe
account summary, read its own recent completed transactions, preview a deposit,
prepare a deposit requiring web-app confirmation, preview an outgoing transfer,
prepare an outgoing Personal transfer requiring web-app confirmation, and view
prepared MCP actions associated with its own account.

A Personal MCP context MUST NOT access Business Account data, Team Access data,
Business approval information, or execute money movement without web-app
confirmation.

An ACTIVE Business MEMBER with a valid MCP token MAY use approved MCP
functionality only for their assigned Business Account. A MEMBER MCP context
MAY read a safe Business Account summary, view completed Business transactions
permitted by existing rules, view Business outgoing requests available under
existing history permissions, preview a deposit, prepare a deposit requiring
web-app confirmation, preview an outgoing withdrawal request, prepare an
outgoing withdrawal request requiring web-app confirmation, preview an outgoing
transfer request, prepare an outgoing transfer request requiring web-app
confirmation, and prepare cancellation of their own eligible PENDING Business
request requiring web-app confirmation.

A MEMBER MCP context MUST NOT approve or reject requests, cancel another
employee's request, access Team Access actions, manage credentials or employee
access, or bypass the standard Business outgoing approval workflow.

An ACTIVE Business AUTHORISER with a valid MCP token MAY perform the same MCP
write preparation actions as a MEMBER and MAY additionally view Pending
Business outgoing requests requiring Authoriser review and safe approval-preview
information such as projected remaining balance and retained-minimum
compliance.

An AUTHORISER MCP context MUST NOT approve a Business withdrawal or transfer
request, reject a Business withdrawal or transfer request, cancel another
employee's request, add employee access, reset passwords, promote employees,
deactivate employees, reactivate employees, or perform any Team Access
administration. Business approvals, rejections, and security-governance actions
remain web-application-only actions.

### Approved MCP Tool Categories
MCP MAY expose read tools for authenticated scoped users, including
`get_my_account_summary`, `list_my_recent_transactions`,
`list_my_business_requests`, `get_business_request_details`,
`list_business_requests_requiring_review` for AUTHORISER read visibility only,
and `get_mcp_prepared_actions`.

Read tools MUST enforce user, account, and role scope; return only safe
information; mask or minimise sensitive identifiers where appropriate; and
never expose passwords, password hashes, temporary credentials, secret keys,
token values, unauthorised account details, or Team Access credential data.

MCP MAY expose non-mutating validation and preview tools, including
`preview_deposit`, `preview_transfer`,
`preview_business_withdrawal_request`, `preview_business_transfer_request`, and
`preview_cancel_my_business_request`.

Preview tools MUST perform no balance movement, create no completed financial
records, create no Business approval request, create no cancellation, clearly
state whether the operation would require web confirmation, return safe
recipient or account confirmation information only, validate applicable amount,
recipient, account-access, and retained-minimum rules based on current
information, and state that completion may still be revalidated later.

MCP MAY expose prepared-action tools, including `prepare_deposit`,
`prepare_personal_transfer`, `prepare_business_withdrawal_request`,
`prepare_business_transfer_request`, and `prepare_cancel_my_business_request`.

Prepared-action tools MUST create no completed financial transaction at
preparation time, move no funds at preparation time, create no completed
Transfer Operation at preparation time, create no Business outgoing request
until web-app confirmation of a prepared Business request submission, create no
cancellation until web-app confirmation of a prepared cancellation, create a
time-limited prepared-action record associated with the authenticated human
identity and MCP channel, require explicit user confirmation inside Midnight
Ledger before any approved write executes, expire or become unusable after
confirmation, cancellation, revocation, or timeout as later specified, and
revalidate all business rules at confirmation time.

### Web-App Confirmation Requirement for MCP Writes
No MCP-originated balance-changing or workflow-changing write action MAY
complete solely because an AI client called a tool. Every approved MCP write
action MUST first be created as a prepared action. The authenticated human user
MUST confirm the prepared action inside the Midnight Ledger web application.
Confirmation in the AI client alone is insufficient for the MVP.

This confirmation rule applies to deposits into Personal Accounts, deposits
into Business Accounts, Personal Account transfers, Business withdrawal request
submissions, Business transfer request submissions, and eligible cancellation
of the user's own PENDING Business request.

At web-app confirmation time, the user identity and token-prepared action
association MUST be checked; the user's current permissions MUST be checked;
any Business employee access MUST still be ACTIVE; the action MUST still be
pending confirmation and unexpired; all money validation, recipient resolution,
balance validation, retained-minimum logic, and cancellation eligibility MUST
be revalidated through existing banking services; and only then MAY the
existing v3 operation execute.

### MCP Deposits, Personal Transfers, Business Requests, and Cancellation
MCP MAY support prepared deposits for Personal users and ACTIVE Business
employees. A Personal MCP-prepared deposit MUST target only the user's own
Personal Account. A Business MCP-prepared deposit MUST target only the
employee's assigned Business Account. Deposits require Midnight Ledger
confirmation before changing balances. Confirmed deposits MUST follow existing
v3 rules: Business deposits do not require Authoriser approval; completed
financial transaction records are created only after web confirmation; Decimal
validation and transaction atomicity are reused.

A Personal user MAY preview and prepare a transfer through MCP, but MCP MUST
NOT complete the Personal transfer directly. Web confirmation MUST revalidate
user ownership, token and action validity, destination account type,
phone-number or UEN recipient resolution, amount validity, current available
balance, and self-transfer prohibition. If confirmation succeeds, the existing
v3 Personal transfer service MUST execute atomically. Completed MCP-originated
Personal transfer records MUST visibly identify the initiation channel as
`MCP Assistant`.

An ACTIVE MEMBER or AUTHORISER MAY preview and prepare a Business withdrawal
request or Business transfer request through MCP. Prepared actions MUST NOT
create the formal Business outgoing request and MUST NOT move money. After
web-app confirmation, the existing v3 service creates the standard PENDING
Business outgoing request. No money moves merely because a request is created.
All subsequent approval behaviour remains unchanged: only an active AUTHORISER
MAY approve through the web application, any one AUTHORISER approval is
sufficient, Authoriser self-approval remains permitted only in the web app,
and retained-minimum and approval-time revalidation remain mandatory. Completed
confirmation of MCP-prepared request submission MUST visibly record
`MCP Assistant` as the submission channel in Approval History.

An ACTIVE MEMBER MAY use MCP to prepare cancellation only for their own PENDING
Business request. An ACTIVE AUTHORISER MAY use MCP to prepare cancellation only
for their own PENDING Business request in the initial MCP scope. Although
AUTHORISERS MAY cancel any Pending request in the web application under v3,
MCP MUST NOT extend cancellation to another employee's request. Prepared
cancellation requires confirmation inside Midnight Ledger. At confirmation
time, standard v3 cancellation rules and current request status MUST be
revalidated. Confirmation changes the request to CANCELLED only if it remains
eligible. Cancellation moves no money. Approval History MUST show the
`MCP Assistant` channel where the cancellation originated.

### Explicit MCP Exclusions
MCP MUST NOT expose tools to approve Business withdrawal requests, approve
Business transfer requests, reject Business requests, cancel another employee's
Business request, add employee access, reset temporary passwords, change
passwords, promote employees, deactivate employees, reactivate employees,
display Team Access credentials or security administration data, generate,
revoke, or inspect another user's MCP tokens, alter account product types or
login contexts, perform any action on behalf of unauthenticated users, or
bypass web-app confirmation for writes.

These actions remain available only through the existing secured web
application where already supported.

### MCP Token and Session Governance
Midnight Ledger MUST provide an `AI Assistant Access` feature for eligible
authenticated Personal users and ACTIVE Business employees. The web application
MUST allow the user to create an MCP access token, view their own active MCP
token sessions safely without displaying raw token values after initial
creation, revoke their own token, and see safe metadata such as created
timestamp, expiry timestamp, revoked status, last-used timestamp where
implemented, and scoped account context.

The raw MCP token value MAY be displayed only once at creation time where
necessary for local setup. Application storage MUST retain only a safe hash or
equivalent non-recoverable token representation. Expired or revoked tokens
MUST NOT be usable. Token generation MUST be unavailable to
`PASSWORD_CHANGE_REQUIRED` or `DEACTIVATED` Business employees. Revoking a
token MUST invalidate future MCP requests and any unconfirmed prepared actions
associated with the revoked token, unless the later technical plan documents a
stricter user-identity-level invalidation rule. Token activity MUST be
auditable.

The later specification and technical plan MUST select a concrete local-MVP
expiry period and secure token-handling approach.

### Prepared MCP Action Lifecycle
The application MUST introduce an auditable prepared-action concept separate
from Transaction History and Business Approval History. Required
prepared-action statuses are `PENDING_CONFIRMATION`, `CONFIRMED`, `CANCELLED`,
`EXPIRED`, and `FAILED`.

A prepared action records intended action only. It is not itself a completed
money movement. A prepared action MUST be associated with the authenticated
human identity, scoped Personal or Business account, MCP token or session where
appropriate, MCP tool name, action type, safe input summary, channel
`MCP_ASSISTANT`, created timestamp, expiry timestamp, confirmed timestamp where
applicable, linked resulting transaction/request/cancellation where applicable,
and safe failure reason where applicable.

Only the user whose MCP context created the prepared action MAY confirm it. A
prepared action MAY be confirmed at most once. A prepared action MUST be
revalidated at confirmation time. Expired, cancelled, revoked-session-
associated, failed, or already-confirmed actions MUST NOT execute. Failed
confirmation MUST NOT create unintended money movement.

### AI Activity Audit
The application MUST provide an AI Activity Audit view distinct from
Transaction History, Approval History, and Access Audit History. AI Activity
Audit MUST record safe MCP-related activity including MCP token issued, MCP
token revoked, rejected use of expired or revoked token where retained, MCP
read or preview activity where audit retention is approved, prepared action
created, prepared action confirmed, prepared action cancelled or expired,
prepared action failed, MCP tool name, human actor, scoped account, timestamp,
safe outcome, and related transaction or Business request ID where applicable.

AI Activity Audit MUST NOT reveal raw MCP tokens, token hashes, passwords,
password hashes, temporary passwords, unnecessary unmasked personal
identifiers, secret keys, or credential data. Completed MCP-originated
financial actions MUST also show their channel as `MCP Assistant` in
Transaction History. MCP-originated Business request submissions or
cancellations MUST show their channel in Approval History. AI Activity Audit
MUST never be confused with completed financial movement.

### Existing v3 Rules Remain Authoritative
Every applicable version 3.0.0 rule remains authoritative, including Personal
Account phone-number receiving identifier, Business Account UEN receiving
identifier, SGD-only amounts, Decimal validation, Personal no-minimum-balance
rule, Business opening and retained-minimum rules, Business Employee Access
statuses, Team Access and Authoriser permissions, final active AUTHORISER
protection, Business outgoing approval lifecycle, Transaction, Approval, and
Access Audit separation, secure password and temporary-password handling, and
Midnight Ledger UI/UX requirements.

MCP MUST NOT modify or weaken these rules.

### MCP-Specific Security Obligations
MCP tool inputs MUST be validated server-side. MCP tool outputs MUST be
sanitised and minimised. Every tool invocation MUST enforce authentication,
token scope, user context, account access, role, access status, and action
eligibility. No sensitive operation MAY depend solely on AI-client
confirmation.

MCP writes require Midnight Ledger web-app confirmation. MCP write
confirmations MUST use the same Django financial and permission services as
existing web actions. Tool invocations MUST be logged or auditable according
to the approved AI Activity Audit design. The server MUST implement sensible
local-MVP rate limiting or invocation throttling where specified in the
technical plan.

Tool errors MUST NOT expose internal secrets, credential data, database
details, or unauthorised account existence. MCP server configuration and access
tokens MUST NOT be committed to Git. MCP MUST NOT be treated as safe for real
banking use.

### UI/UX Additions
Midnight Ledger MUST add an AI Assistant Access page for eligible authenticated
Personal users and ACTIVE Business employees. The page MUST explain AI
Assistant access, warn that AI actions remain limited by existing permissions,
provide token creation, display the raw token only at initial creation with
safe local setup guidance, list active token/session metadata safely, provide
token revocation, show expiry and revocation status, and explain that sensitive
write actions require confirmation inside Midnight Ledger.

Midnight Ledger MUST add a Prepared Actions Review page where the authenticated
user can view actions prepared through MCP, inspect safe action details, see
status and expiry, confirm an eligible prepared action, cancel an unconfirmed
prepared action, and understand the financial or workflow consequence before
confirming.

Personal transfer confirmation MUST show recipient confirmation, amount,
current balance, projected resulting balance, and channel `MCP Assistant`.
Deposit confirmation MUST show destination account, amount, and channel
`MCP Assistant`. Business request submission confirmation MUST show Business
Account, request type, amount, destination where applicable, a reminder that
confirmation creates a PENDING request only and no funds move until approved,
and channel `MCP Assistant`.

Midnight Ledger MUST add a separate, readable AI Activity Audit page displaying
safe MCP-session and prepared-action activity. Personal and Business navigation
MUST include appropriate permitted navigation items such as `AI Assistant` or
`AI Activity`. These pages MUST NOT be exposed to unauthenticated users,
`PASSWORD_CHANGE_REQUIRED` employees, or `DEACTIVATED` employees.

### Mandatory MCP Test and Traceability Obligations
MCP token security and scope tests MUST verify that eligible Personal users,
ACTIVE Business MEMBER users, and ACTIVE Business AUTHORISER users can generate
scoped MCP tokens; `PASSWORD_CHANGE_REQUIRED` employees cannot generate or use
tokens; `DEACTIVATED` employees cannot generate or use tokens; tokens are
stored non-recoverably; raw tokens are displayed only once where applicable;
expired tokens are rejected; revoked tokens are rejected; users cannot access
another user's MCP token metadata; and token permissions do not exceed the
human user's permissions.

MCP read and preview tests MUST verify that Personal account summaries are
limited to the user's own account; Business account summaries are limited to
the assigned Business Account; recent-transaction access respects current
permissions; AUTHORISERS may view Pending requests requiring action through
MCP; MEMBER users do not gain unauthorised AUTHORISER-only visibility; transfer
preview validates phone/UEN destination rules; previews do not move funds or
create completed financial records; and preview output is sanitised.

Prepared deposit tests MUST verify that Personal users and ACTIVE Business
employees can prepare deposits; preparation moves no money; web confirmation
completes deposits through the existing service; Business deposit confirmation
does not create an approval request; confirmed transactions identify the
`MCP Assistant` channel; and invalid, expired, or revoked prepared deposits
fail safely.

Prepared Personal transfer tests MUST verify that a Personal user can prepare a
transfer; preparation moves no money; web confirmation revalidates balance and
recipient; confirmed transfer creates atomic linked records; Transaction
History shows the MCP channel; and failed, revoked, or expired confirmation
causes no money movement.

Prepared Business request tests MUST verify that ACTIVE MEMBER or AUTHORISER
users can prepare withdrawal and transfer requests; preparation creates no
standard Business request and moves no money; web confirmation creates a normal
PENDING Business request; Approval History shows the MCP channel; Business
approval still cannot occur through MCP; and all v3 approval and retained-
minimum rules remain intact.

MCP cancellation tests MUST verify that MEMBER users may prepare cancellation
only for their own Pending Business request; AUTHORISER MCP cancellation is
limited to their own Pending request; preparation does not cancel immediately;
web confirmation cancels only if the request remains eligible; attempts to
cancel another employee's request through MCP are rejected; and Approval
History displays the MCP channel.

AI Activity Audit tests MUST verify that token issuance and revocation events
are recorded safely; prepared-action creation, confirmation, cancellation,
expiry, and failure are auditable; linked resulting transactions or requests
are represented safely; the audit view exposes no token or password secrets;
and AI activity does not appear as completed financial movement unless a
confirmed financial action actually completes.

### Governance and Versioning
All subsequent specification, checklist, plan, tasks, analysis, implementation,
UI, security review, test coverage, and traceability work MUST incorporate
local stdio MCP server design, short-lived revocable scoped tokens,
prepared-action confirmation through Midnight Ledger, read/preview/limited
prepared-write tools, prepared deposits, prepared Personal transfers, prepared
Business withdrawal and transfer requests, own-request Business cancellation
through MCP, Authoriser read-only view of pending requests requiring action,
AI Activity Audit, `MCP Assistant` initiation-channel labels, and explicit
exclusion of approvals and Team Access actions from MCP.

This amendment is a MAJOR constitutional amendment because it introduces an
authenticated AI tool interface capable of reading financial information and
preparing limited state-changing banking actions.

## Specification-Driven Development Quality Gates

Every feature specification MUST include a Constitution Check and MUST identify
all applicable `BR-###`, `FR-###`, `SEC-###`, `NFR-###`, and `TEST-###`
identifiers. Each business rule MUST have acceptance criteria before planning
begins.

Every technical plan MUST prove alignment with the MVP stack, SGD-only money
handling, Personal Account rules, Business Account employee access rules,
temporary-password and access-state rules, role rules, Access Audit rules,
Business retained-minimum rules, deposit and withdrawal rules, transfer
atomicity, Business outgoing approval lifecycle, transaction immutability,
history separation, secrets management, MCP token and prepared-action rules
where applicable, mandatory tests, traceability, and local deployment.

Every task list MUST include tests before implementation tasks for applicable
banking, employee-access, permission, audit, password-governance, MCP,
prepared-action, token-security, and security rules. Tasks MUST preserve
requirement and business-rule identifiers and name the code component and test
path that will satisfy each rule.

Completion requires passing mandatory automated tests and updated traceability
from constitution rule to specification, acceptance criteria, plan, task, code
component, and test.

## Governance

This constitution supersedes conflicting repository conventions, templates,
plans, specifications, tasks, and implementation choices. When conflict exists,
the constitution wins until amended.

Amendments MUST be proposed as explicit documentation changes that state the
motivation, affected rules, migration impact, version impact, and required
template updates. An amendment is approved only after the constitution and
dependent Spec Kit templates are updated together, unless the amendment request
explicitly limits the command to constitution-only output and records template
updates as pending follow-up work.

Compliance review is mandatory during specification and planning. A feature may
not proceed from specification to planning, from planning to tasks, or from
tasks to complete implementation while any applicable constitutional gate is
failing.

Versioning follows semantic versioning:
- MAJOR: removing or fundamentally redefining a core principle or banking,
  identity, employee-access, authorisation, MCP, confirmation, token, or audit
  invariant.
- MINOR: adding a mandatory principle or materially expanding scope.
- PATCH: clarifications that do not change required behaviour.

**Version**: 4.0.0 | **Ratified**: 2026-05-25 | **Last Amended**: 2026-05-28
