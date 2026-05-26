# Feature Specification: Banking MVP

**Feature Branch**: `001-banking-mvp`

**Created**: 2026-05-25

**Status**: Draft - revised for constitution v2.0.0

**Input**: User description: "Build the MVP for a personal and business banking application that allows users to securely manage SGD accounts, deposit and withdraw funds, transfer money using phone numbers and UENs, manage Business Account membership and approvals, and view auditable transaction, approval, and access histories."

## Clarifications

### Session 2026-05-25

- Q: What is the MVP relationship between a user, Personal Account, Business Account, and Business Account activation? -> A: Superseded by constitution v2.0.0; Personal and Business login identities are now separate and a Personal Account no longer authorises a Business Account.
- Q: How do Business Account outgoing approval, revalidation, and lifecycle work? -> A: Submission creates only a PENDING request with no fund reservation; approval revalidates amount, current balance, retained minimum, and authorising Business role; PENDING may become COMPLETED, REJECTED, CANCELLED, or FAILED, and final states cannot be acted on again.
- Q: How are Transaction History and Approval History separated? -> A: Transaction History shows completed financial records only; Approval History shows Business Account outgoing requests, with completed Business outgoing operations appearing in both histories.
- Q: How are transfer recipients identified after constitution v1.1.0? -> A: Preserved in constitution v2.0.0; Personal Account destinations use phone number, Business Account destinations use UEN, and sender must choose recipient account type before entering the matching identifier.
- Q: What transfer and monetary edge rules are final? -> A: Safe recipient confirmation is required; self-transfers are rejected; SGD amounts use at most two decimal places and reject zero, negative, text, malformed, non-numeric, and excessive-precision values.

### Session 2026-05-26

- Q: How does constitution v2.0.0 change account identity and Business authorisation? -> A: Personal and Business login identities are separate. Business Accounts are company-owned shared accounts accessed through Business User memberships with MEMBER or AUTHORISER roles. A Personal Account never authorises a Business Account.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register for the Correct Access Context (Priority: P1)

A new user chooses exactly one registration path: Personal Account access or Business Account access. Personal registration creates Personal-only access and one Personal Account. Business registration creates Business-only access, creates one Business Account, and makes the creator the first AUTHORISER for that Business Account.

**Why this priority**: Separate login contexts are the foundation of constitution v2.0.0. No financial or membership workflow can be trusted if a login can cross Personal and Business boundaries.

**Independent Test**: A Personal registration can access only Personal functionality, a Business registration can access only Business functionality, duplicate emails are rejected globally, and Business registration creates the initial AUTHORISER membership.

**Acceptance Scenarios**:

1. **Given** no registered identity has email `p@example.test` and no Personal Account has phone `91234567`, **When** a user registers for Personal Account access with username, email, password, and phone number, **Then** a Personal-only login identity and one Personal Account are created with balance SGD 0.00.
2. **Given** no registered identity has email `b@example.test` and no Business Account has UEN `202612345A`, **When** a user registers for Business Account access with creator username, email, password, business display name, UEN, and opening deposit SGD 7,000.00, **Then** a Business-only login identity, Business Account, creator AUTHORISER membership, and completed opening-deposit transaction are created.
3. **Given** an email is already used by any Personal or Business login identity, **When** another registration attempts to use that email, **Then** registration is rejected and no duplicate login is created.
4. **Given** a Personal login is authenticated, **When** they attempt to access Business Account pages, Business invitation acceptance, Approvals, Members, or Access Audit, **Then** access is denied.
5. **Given** a Business login is authenticated, **When** they attempt to access Personal Account pages or Personal money operations, **Then** access is denied.
6. **Given** a real individual needs both Personal and Business access, **When** they register both contexts, **Then** each context requires separate credentials with different unique email addresses.
7. **Given** Business registration is submitted without UEN, with a duplicate UEN, or with opening deposit below SGD 7,000.00, **When** registration is processed, **Then** it is rejected and no Business Account, membership, or completed opening transaction is created.

---

### User Story 2 - Use a Personal Account (Priority: P1)

A Personal user manages exactly one Personal Account with a unique receiving phone number, no opening deposit, no minimum balance, valid deposits, valid withdrawals, outgoing transfers, and completed transaction history.

**Why this priority**: Personal Account behavior proves the individual banking flow, phone recipient identity, no-minimum-balance rule, and negative-balance protection.

**Independent Test**: A Personal Account starts at SGD 0.00, rejects duplicate phone numbers, accepts valid money operations, allows full-balance withdrawal or transfer to SGD 0.00, and rejects operations that would make the balance negative.

**Acceptance Scenarios**:

1. **Given** a Personal user has just registered, **When** they view their Personal Account, **Then** it shows balance SGD 0.00 and its unique receiving phone number.
2. **Given** another Personal Account already uses phone `91234567`, **When** Personal registration attempts to use phone `91234567`, **Then** registration is rejected and no duplicate phone identifier is created.
3. **Given** a Personal Account with balance SGD 0.00, **When** SGD 100.00 is deposited, **Then** the balance becomes SGD 100.00 and one completed deposit transaction with UUID transaction ID is recorded.
4. **Given** a Personal Account with balance SGD 100.00, **When** SGD 100.00 is withdrawn, **Then** the balance becomes SGD 0.00 and one completed withdrawal transaction is recorded.
5. **Given** a Personal Account with balance SGD 30.00, **When** SGD 30.01 is requested for withdrawal, **Then** the withdrawal is rejected, balance remains SGD 30.00, and no completed withdrawal transaction is recorded.
6. **Given** a Personal Account with balance SGD 75.00 and a known Personal recipient phone number, **When** SGD 25.00 is transferred, **Then** sender and recipient balances update atomically and linked transfer records are created.
7. **Given** a Personal Account with balance SGD 75.00 and a known Business recipient UEN, **When** SGD 75.00 is transferred, **Then** the Personal balance becomes SGD 0.00 and the Business Account receives the incoming transfer without approval.

---

### User Story 3 - Register and Use a Business Account as Initial AUTHORISER (Priority: P1)

A Business creator registers a Business-only login identity, opens a Business Account with a unique UEN and opening deposit of at least SGD 7,000.00, and becomes the first AUTHORISER for that Business Account.

**Why this priority**: Business Account creation now depends on company account identity and Business membership, not on a Personal Account prerequisite.

**Independent Test**: Business registration succeeds only with unique email, business display name, unique UEN, valid opening deposit, and initial AUTHORISER membership.

**Acceptance Scenarios**:

1. **Given** no Business Account uses UEN `202612345A`, **When** a Business registration uses opening deposit exactly SGD 7,000.00, **Then** the Business Account is created, the balance is SGD 7,000.00, and the creator is an AUTHORISER.
2. **Given** no Business Account uses UEN `202612346B`, **When** a Business registration uses opening deposit greater than SGD 7,000.00, **Then** the Business Account is created with the deposited balance.
3. **Given** a Business registration omits business display name, **When** it is submitted, **Then** registration is rejected.
4. **Given** a Business registration omits UEN or uses a duplicate UEN, **When** it is submitted, **Then** registration is rejected.
5. **Given** a Business registration uses opening deposit SGD 6,999.99, **When** it is submitted, **Then** registration is rejected and no Business Account or membership is created.
6. **Given** a Business Account is created, **When** history is viewed, **Then** Transaction History includes one completed Business opening-deposit transaction and Access Audit History includes Business creation plus initial AUTHORISER assignment.

---

### User Story 4 - Manage Business Membership and Invitations (Priority: P1)

An AUTHORISER manages access to a Business Account by inviting Business Users, assigning roles, promoting MEMBERS, removing members where allowed, and preserving access audit history. MEMBERS can view membership information but cannot administer membership.

**Why this priority**: Company-owned accounts require individual accountability and role-based access rather than shared credentials.

**Independent Test**: AUTHORISER-only membership actions succeed or fail according to role rules, and every access-management outcome is auditable.

**Acceptance Scenarios**:

1. **Given** an AUTHORISER enters an invitee email and selects MEMBER, **When** the invitation is issued, **Then** a PENDING invitation is created and Access Audit History records the invitation.
2. **Given** an AUTHORISER enters an invitee email and selects AUTHORISER, **When** the invitation is issued, **Then** a PENDING invitation is created with AUTHORISER role.
3. **Given** a MEMBER attempts to invite a user or assign a role, **When** they submit the action, **Then** the action is rejected.
4. **Given** an invited person signs in with an existing Business-only login matching the invited email, **When** they accept the invitation, **Then** active membership is created with the invited role.
5. **Given** an invited person has no login, **When** they register from the invitation, **Then** they must create a Business-only login before accepting access.
6. **Given** an invited person signs in with a Personal-only login, **When** they attempt to accept a Business invitation, **Then** acceptance is rejected.
7. **Given** a Business User accepts invitations to two Business Accounts, **When** they sign in, **Then** they can access both accounts and select between accessible companies.
8. **Given** a Business User is removed from one Business Account but remains a member of another, **When** they sign in, **Then** they lose access only to the removed account.
9. **Given** an AUTHORISER promotes a MEMBER to AUTHORISER, **When** the action succeeds, **Then** the member can perform AUTHORISER actions and Access Audit History records the promotion.
10. **Given** an AUTHORISER removes a MEMBER, **When** the action succeeds, **Then** the removed user immediately loses access to that Business Account.
11. **Given** at least two AUTHORISERS exist, **When** one AUTHORISER removes another AUTHORISER, **Then** the removal succeeds only if at least one AUTHORISER remains afterward.
12. **Given** only one AUTHORISER remains, **When** removal of that AUTHORISER is attempted, **Then** removal is rejected.
13. **Given** an AUTHORISER attempts to demote another AUTHORISER to MEMBER, **When** the action is submitted, **Then** it is rejected because demotion is outside MVP scope.

---

### User Story 5 - Transfer Money Safely (Priority: P1)

A Personal user or Business User selects a source account, selects recipient account type, enters the matching identifier, reviews safe recipient confirmation, and receives a completed, PENDING, or rejected outcome.

**Why this priority**: Account-type-specific recipient identification prevents misdirected money and preserves Personal phone versus Business UEN distinction.

**Independent Test**: Recipient lookup uses phone for Personal destinations and UEN for Business destinations, rejects mismatches and unknown identifiers, and creates linked transfer records only after completion.

**Acceptance Scenarios**:

1. **Given** a Personal sender selects Personal Account destination and enters a known phone number, **When** they confirm a valid transfer, **Then** the transfer completes immediately.
2. **Given** a Personal sender selects Business Account destination and enters a known UEN, **When** they confirm a valid transfer, **Then** the transfer completes immediately as incoming Business funds.
3. **Given** a Business MEMBER or AUTHORISER selects Personal Account destination and enters a known phone number, **When** they submit a valid outgoing transfer, **Then** a PENDING Business outgoing request is created and no funds move.
4. **Given** a Business MEMBER or AUTHORISER selects Business Account destination and enters a known UEN, **When** they submit a valid outgoing transfer, **Then** a PENDING Business outgoing request is created and no funds move.
5. **Given** the sender selects Personal Account destination and enters an unknown phone number, **When** transfer is attempted, **Then** it is rejected.
6. **Given** the sender selects Business Account destination and enters an unknown UEN, **When** transfer is attempted, **Then** it is rejected.
7. **Given** the sender selects Personal Account destination but enters a UEN, **When** transfer is attempted, **Then** it is rejected as an identifier-type mismatch.
8. **Given** the sender selects Business Account destination but enters a phone number, **When** transfer is attempted, **Then** it is rejected as an identifier-type mismatch.
9. **Given** a sender attempts to transfer from an account back to the same account, **When** transfer is attempted, **Then** it is rejected.
10. **Given** a completed transfer exists, **When** Transaction History is viewed, **Then** sender debit and recipient credit records each have their own UUID transaction ID and share one transfer operation ID.

---

### User Story 6 - Submit and Resolve Business Outgoing Requests (Priority: P1)

A MEMBER or AUTHORISER submits outgoing Business withdrawal or transfer requests. AUTHORISERS approve, reject, or cancel requests according to role rules. MEMBERS may cancel only their own PENDING requests.

**Why this priority**: Role-based approval protects outgoing company funds while supporting multiple Business Users and multiple PENDING requests.

**Independent Test**: PENDING requests do not reserve funds, AUTHORISER approval threshold is one, approval revalidates retained minimum, and terminal states cannot be changed again.

**Acceptance Scenarios**:

1. **Given** an active MEMBER submits a Business withdrawal request, **When** the amount is valid, **Then** a PENDING request is created and no balance changes.
2. **Given** an active MEMBER submits a Business outgoing transfer request, **When** the amount and recipient are valid, **Then** a PENDING request is created and no completed transfer records are created.
3. **Given** an AUTHORISER submits a Business outgoing request, **When** the amount is valid, **Then** a PENDING request is created.
4. **Given** an AUTHORISER submitted their own PENDING request, **When** they approve it and all current financial rules pass, **Then** the request becomes COMPLETED and money moves atomically.
5. **Given** a different AUTHORISER approves a PENDING request, **When** all current financial rules pass, **Then** one AUTHORISER approval is sufficient for completion.
6. **Given** a MEMBER attempts to approve or reject a PENDING request, **When** the action is submitted, **Then** the action is denied.
7. **Given** a MEMBER submitted a PENDING request, **When** that same MEMBER cancels it, **Then** it becomes CANCELLED and no funds move.
8. **Given** a MEMBER attempts to cancel another user's PENDING request, **When** the action is submitted, **Then** the action is denied.
9. **Given** an AUTHORISER cancels any PENDING request, **When** the action is submitted, **Then** it becomes CANCELLED and no funds move.
10. **Given** a Business Account has multiple PENDING requests, **When** each is reviewed, **Then** none reserve funds and each is independently revalidated at approval time.
11. **Given** a Business Account has balance SGD 8,500.00 and two PENDING withdrawals for SGD 1,000.00 and SGD 500.01, **When** the first completes, **Then** the second fails at approval because completion would leave SGD 6,999.99.
12. **Given** a PENDING outgoing request would leave exactly SGD 7,000.00, **When** an AUTHORISER approves it, **Then** the request becomes COMPLETED.
13. **Given** a request is COMPLETED, REJECTED, CANCELLED, or FAILED, **When** any user attempts to change it again, **Then** the action is rejected.

---

### User Story 7 - Navigate the Midnight Ledger Interface (Priority: P2)

Users get a premium "Midnight Ledger" server-rendered banking experience with separate navigation for Personal and Business contexts, clear role-based controls, safe confirmations, and polished empty, error, success, PENDING, REJECTED, CANCELLED, FAILED, and COMPLETED states.

**Why this priority**: The MVP must feel like a credible banking product while making account context and permissions obvious.

**Independent Test**: Personal users see only Personal navigation. Business users see Business navigation, company selection where applicable, role-aware controls, and separate history areas.

**Acceptance Scenarios**:

1. **Given** an unauthenticated visitor opens registration, **When** the page loads, **Then** it presents polished choices for "Open a Personal Account" and "Open a Business Account".
2. **Given** the user chooses Personal Account registration, **When** the form appears, **Then** it explains phone-number transfer receipt and no opening deposit.
3. **Given** the user chooses Business Account registration, **When** the form appears, **Then** it explains UEN transfer receipt, SGD 7,000.00 opening funds, team access, and approval controls.
4. **Given** a Personal user is signed in, **When** navigation is shown, **Then** it includes Dashboard, Personal Account, Transfer, Transactions, and Sign Out only.
5. **Given** a Business user is signed in, **When** navigation is shown, **Then** it includes Business Dashboard, company selector when multiple memberships exist, Deposit, Request Withdrawal, Request Transfer, Approvals, Members, Access Audit, Transactions, and Sign Out.
6. **Given** a Business user views the Business Dashboard, **When** an account is selected, **Then** it shows business name, UEN, current balance, retained-minimum reminder, current role, pending count, role-appropriate quick actions, recent transactions, and recent request activity.
7. **Given** an AUTHORISER opens Members, **When** memberships are displayed, **Then** invite, promote, and remove controls appear only where allowed.
8. **Given** a MEMBER opens Members, **When** memberships are displayed, **Then** management controls are hidden or read-only and server-side permission checks still enforce restrictions.
9. **Given** an approval detail is viewed, **When** the screen loads, **Then** it shows requester, requester role, operation type, recipient confirmation, amount, current balance, projected balance, retained-minimum compliance, permitted actions, and status history.
10. **Given** the browser width is narrow, **When** primary pages are used, **Then** content remains readable without horizontal scrolling for normal use.

---

### User Story 8 - View Transaction, Approval, and Access Audit Histories (Priority: P2)

Users view completed financial movements in Transaction History, Business outgoing workflow records in Approval History, and Business access-management activity in Access Audit History.

**Why this priority**: Trust depends on distinguishing completed money movement from approval workflow and membership governance.

**Independent Test**: The three histories contain only their own record types and enforce Personal ownership or active Business membership permissions.

**Acceptance Scenarios**:

1. **Given** a Personal Account has completed deposits, withdrawals, and transfers, **When** the Personal user views Transaction History, **Then** completed financial movements are shown with amount, status, timestamp, account, and UUID transaction ID.
2. **Given** a Business Account has opening deposit, deposits, completed withdrawals, completed transfers, and incoming credits, **When** an active Business member views Transaction History, **Then** only completed financial movements are shown.
3. **Given** Business outgoing requests exist in PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED status, **When** Approval History is viewed, **Then** requester, requester role, type, amount, destination where applicable, reviewer where applicable, status, dates, and safe outcome reason are shown.
4. **Given** Business invitations, acceptances, role assignments, promotions, removals, and initial AUTHORISER assignment exist, **When** Access Audit History is viewed, **Then** access events are shown separately from financial transactions.
5. **Given** PENDING, REJECTED, CANCELLED, or FAILED outgoing requests exist, **When** Transaction History is viewed, **Then** those workflow records are not displayed as completed money movement.
6. **Given** access audit events exist, **When** Transaction History is viewed, **Then** invitations, acceptances, promotions, and removals are not displayed as financial transactions.
7. **Given** a removed Business User attempts to view Business Transaction History, Approval History, or Access Audit History for the removed account, **When** access is attempted, **Then** access is denied immediately.

## Edge Cases

- Duplicate email across Personal and Business login identities.
- Personal registration with duplicate phone number.
- Business registration with missing business display name.
- Business registration with missing or duplicate UEN.
- Business registration with opening deposit below SGD 7,000.00.
- Personal login attempts Business pages or Business invitation acceptance.
- Business login attempts Personal pages or Personal money operations.
- Business User attempts to access a Business Account without active accepted membership.
- Removed Business User attempts any action or history view on the removed Business Account.
- MEMBER attempts to invite, assign role, promote, remove, approve, reject, or cancel another user's request.
- AUTHORISER attempts to remove the final AUTHORISER.
- AUTHORISER attempts to demote an AUTHORISER to MEMBER.
- Invitation is issued but not accepted; no Business Account access is granted.
- Personal-only identity attempts to accept a Business invitation.
- Business User belongs to multiple Business Accounts and is removed from only one.
- Zero, negative, malformed, non-numeric, non-SGD, or invalid-precision monetary inputs.
- Amounts with more than two decimal places.
- Personal Account withdrawal or transfer exceeding available balance.
- Business Account outgoing request attempted by a user without membership.
- Business Account outgoing request approved by MEMBER.
- Business Account outgoing withdrawal or transfer that would leave less than SGD 7,000.00.
- Business Account outgoing request that would leave exactly SGD 6,999.99.
- Business Account outgoing request that would leave exactly SGD 7,000.00.
- Multiple PENDING Business outgoing requests with no fund reservation.
- PENDING Business request failing approval because another request completed first.
- Attempt to act on COMPLETED, REJECTED, CANCELLED, or FAILED outgoing request.
- Unknown Personal phone number or Business UEN.
- Recipient account type and identifier mismatch.
- Transfer from an account to itself.
- Failed, rejected, cancelled, or PENDING operation creating completed financial records or changing balances.
- Access audit events appearing in Transaction History.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST require registration to choose exactly one account-access type: Personal Account access or Business Account access.
- **FR-002**: The system MUST require every login identity to have a user-selected username, globally unique email address, and securely stored password.
- **FR-003**: The system MUST reject duplicate email registration across Personal and Business login identities.
- **FR-004**: The system MUST allow registered users to sign in and sign out.
- **FR-005**: The system MUST reject sign-in attempts with incorrect credentials without exposing which credential was incorrect.
- **FR-006**: The system MUST ensure Personal login identities access Personal Account functionality only.
- **FR-007**: The system MUST ensure Business login identities access Business Account functionality only.
- **FR-008**: The system MUST reject Personal login access to Business Account pages, Business invitation acceptance, Business approvals, Members, and Access Audit.
- **FR-009**: The system MUST reject Business login access to Personal Account pages and Personal money operations.
- **FR-010**: The system MUST require an individual needing both contexts to register separate credentials with different unique email addresses.
- **FR-011**: The system MUST create exactly one Personal Account during Personal Account registration.
- **FR-012**: The system MUST require a Personal Account to have one unique phone number used for receiving transfers.
- **FR-013**: The system MUST reject duplicate Personal Account phone numbers.
- **FR-014**: The system MUST create a Personal Account with balance SGD 0.00 and no opening deposit.
- **FR-015**: The system MUST allow Personal Account deposits of valid positive SGD amounts.
- **FR-016**: The system MUST allow Personal Account withdrawals of valid positive SGD amounts when the balance will not become negative.
- **FR-017**: The system MUST reject Personal Account withdrawals that would make the balance negative.
- **FR-018**: The system MUST allow Personal Account transfers of valid positive SGD amounts when the sender balance will not become negative.
- **FR-019**: The system MUST reject Personal Account transfers that would make the sender balance negative.
- **FR-020**: The system MUST create a Business-only login identity during Business Account registration.
- **FR-021**: The system MUST require Business Account registration to include business display name, unique UEN, and opening deposit of at least SGD 7,000.00.
- **FR-022**: The system MUST reject Business Account registration when business display name is missing.
- **FR-023**: The system MUST reject Business Account registration when UEN is missing or already registered.
- **FR-024**: The system MUST reject Business Account registration when opening deposit is below SGD 7,000.00.
- **FR-025**: The system MUST create the Business Account creator's active membership with AUTHORISER role.
- **FR-026**: The system MUST create one completed Business opening-deposit financial transaction during successful Business Account registration.
- **FR-027**: The system MUST allow a Business User to have active memberships in more than one Business Account.
- **FR-028**: The system MUST support exactly two Business membership roles in the MVP: MEMBER and AUTHORISER.
- **FR-029**: The system MUST allow MEMBER and AUTHORISER users to view Business balance, completed Business Transaction History, Approval History, and Access Audit History for accounts where they have active membership.
- **FR-030**: The system MUST allow MEMBER and AUTHORISER users to deposit valid positive SGD amounts into a Business Account where they have active membership without approval.
- **FR-031**: The system MUST allow MEMBER and AUTHORISER users to submit outgoing Business withdrawal requests.
- **FR-032**: The system MUST allow MEMBER and AUTHORISER users to submit outgoing Business transfer requests.
- **FR-033**: The system MUST allow a MEMBER to cancel only their own PENDING outgoing requests.
- **FR-034**: The system MUST reject MEMBER attempts to approve, reject, invite, assign roles, promote, remove, or cancel another user's request.
- **FR-035**: The system MUST allow an AUTHORISER to approve, reject, or cancel any PENDING outgoing Business request.
- **FR-036**: The system MUST allow an AUTHORISER to approve their own PENDING outgoing request.
- **FR-037**: The system MUST allow one AUTHORISER approval to be sufficient for a valid outgoing Business request to complete.
- **FR-038**: The system MUST allow an AUTHORISER to invite Business Users by email and assign MEMBER or AUTHORISER role through the invitation.
- **FR-039**: The system MUST ensure invitations grant no Business Account access until accepted.
- **FR-040**: The system MUST allow invitees to accept invitations only using or creating a Business-only login identity associated with the invited email.
- **FR-041**: The system MUST reject Personal-only login acceptance of Business invitations.
- **FR-042**: The system MUST allow an AUTHORISER to promote an existing MEMBER to AUTHORISER.
- **FR-043**: The system MUST allow an AUTHORISER to remove an existing MEMBER.
- **FR-044**: The system MUST allow an AUTHORISER to remove another AUTHORISER only when at least one AUTHORISER remains afterward.
- **FR-045**: The system MUST reject removal of the final AUTHORISER.
- **FR-046**: The system MUST reject demotion of an AUTHORISER to MEMBER in the MVP.
- **FR-047**: The system MUST immediately revoke removed users' access to the affected Business Account.
- **FR-048**: The system MUST preserve a Business User's memberships in other Business Accounts when they are removed from one Business Account.
- **FR-049**: The system MUST resolve Personal Account transfer destinations by unique phone number.
- **FR-050**: The system MUST resolve Business Account transfer destinations by unique UEN.
- **FR-051**: The system MUST require sender selection of destination account type before entering recipient identifier.
- **FR-052**: The system MUST reject unknown Personal phone numbers and unknown Business UENs.
- **FR-053**: The system MUST reject recipient identifier/account-type mismatches.
- **FR-054**: The system MUST reject transfer from an account to itself.
- **FR-055**: The system MUST complete valid Personal outgoing transfers immediately.
- **FR-056**: The system MUST allow incoming Business transfers by UEN without approval.
- **FR-057**: The system MUST require outgoing Business transfers to enter PENDING approval before completion.
- **FR-058**: The system MUST require outgoing Business withdrawals to enter PENDING approval before completion.
- **FR-059**: The system MUST ensure PENDING Business outgoing requests do not reserve funds, change balances, or appear as completed financial transactions.
- **FR-060**: The system MUST display actual Business Account balances without reducing them for PENDING requests.
- **FR-061**: The system MUST allow multiple PENDING outgoing Business requests simultaneously.
- **FR-062**: The system MUST revalidate requested amount, current Business balance, retained minimum, and authorising Business role when approval is attempted.
- **FR-063**: The system MUST complete a Business outgoing request only when approval-time validation passes and the Business Account retains at least SGD 7,000.00.
- **FR-064**: The system MUST mark a PENDING Business outgoing request as FAILED when approval-time validation fails.
- **FR-065**: The system MUST support outgoing request statuses PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED.
- **FR-066**: The system MUST NOT persist a separate APPROVED status in the MVP.
- **FR-067**: The system MUST allow only PENDING outgoing requests to be approved, rejected, or cancelled.
- **FR-068**: The system MUST treat COMPLETED, REJECTED, CANCELLED, and FAILED outgoing requests as final.
- **FR-069**: Every successful deposit and completed withdrawal MUST create one immutable completed financial transaction record with a UUID transaction ID.
- **FR-070**: Every successfully completed transfer MUST create one shared transfer operation ID.
- **FR-071**: Every successfully completed transfer MUST create one immutable sender debit record and one immutable recipient credit record.
- **FR-072**: Each completed transfer debit and credit record MUST have its own UUID transaction ID.
- **FR-073**: Linked transfer debit and credit records MUST reference the same transfer operation ID.
- **FR-074**: Transaction History MUST contain completed financial movements only.
- **FR-075**: Approval History MUST contain Business outgoing withdrawal and transfer requests with requester, requester role, type, amount, destination where applicable, reviewer/actioning AUTHORISER where applicable, status, dates, and safe outcome reason where applicable.
- **FR-076**: Access Audit History MUST contain Business creation, initial AUTHORISER assignment, invitations, acceptances, role assignment, promotion, removal, and retained invalid membership-management attempts where appropriate.
- **FR-077**: The system MUST keep Transaction History, Approval History, and Access Audit History logically distinct.
- **FR-078**: The system MUST deny history access when the user does not own the Personal Account or does not have active Business membership.
- **FR-079**: The system MUST record access audit events for invitations, acceptances, role assignment, promotions, removals, and initial AUTHORISER assignment.
- **FR-080**: The system MUST identify all membership and approval actions by authenticated individual login, not shared credentials.

### Business Rules

- **BR-001**: All monetary values and balances are SGD only.
- **BR-002**: Monetary operations MUST use precise decimal arithmetic and MUST NOT use floating-point arithmetic.
- **BR-003**: Money inputs MUST reject zero, negative, malformed, non-numeric, non-SGD, and excessive-precision values.
- **BR-004**: Monetary values MUST support no more than two decimal places.
- **BR-005**: Failed, rejected, PENDING, CANCELLED, or FAILED operations MUST NOT create completed financial transaction records.
- **BR-006**: Failed, rejected, PENDING, CANCELLED, or FAILED operations MUST NOT change balances.
- **BR-007**: Personal and Business login identities are mutually exclusive access contexts.
- **BR-008**: A Personal login identity accesses Personal Account functionality only.
- **BR-009**: A Business login identity accesses Business Account functionality only.
- **BR-010**: A Personal Account has no opening deposit requirement and no retained minimum.
- **BR-011**: A Personal Account begins at SGD 0.00.
- **BR-012**: A Personal Account MUST NOT become negative.
- **BR-013**: A Personal Account receives transfers by unique phone number.
- **BR-014**: A Business Account is a company-owned shared account and is not owned or authorised by a Personal Account.
- **BR-015**: A Business Account receives transfers by unique UEN.
- **BR-016**: A Business Account requires opening deposit of at least SGD 7,000.00.
- **BR-017**: A Business Account creator becomes initial AUTHORISER.
- **BR-018**: A Business Account may have multiple AUTHORISERS and MUST always have at least one AUTHORISER.
- **BR-019**: Business membership roles are MEMBER and AUTHORISER only.
- **BR-020**: AUTHORISER-only membership administration MUST be enforced server-side.
- **BR-021**: Removing a Business User immediately revokes access to that Business Account.
- **BR-022**: Demoting AUTHORISER to MEMBER is outside MVP scope and MUST be rejected.
- **BR-023**: Completed outgoing Business withdrawals and transfers MUST leave at least SGD 7,000.00.
- **BR-024**: Business deposits and incoming Business transfers do not require approval.
- **BR-025**: Business outgoing withdrawals and transfers require AUTHORISER approval before completion.
- **BR-026**: One AUTHORISER approval is sufficient.
- **BR-027**: AUTHORISERS MAY approve their own requests.
- **BR-028**: PENDING outgoing requests do not reserve funds or reduce displayed balances.
- **BR-029**: Multiple PENDING outgoing requests are allowed.
- **BR-030**: Each PENDING request is independently revalidated at approval time.
- **BR-031**: There is no separately persisted APPROVED status.
- **BR-032**: Only PENDING requests may transition.
- **BR-033**: COMPLETED, REJECTED, CANCELLED, and FAILED are final statuses.
- **BR-034**: Transfer destination account type and identifier MUST match.
- **BR-035**: Transfers from an account to itself are rejected.
- **BR-036**: The previous same-user Personal/Business transfer prohibition is removed because one login no longer owns both contexts.
- **BR-037**: Every completed transfer creates two linked financial transaction records with one shared transfer operation ID.
- **BR-038**: Balance changes and completed financial transaction creation MUST be atomic.
- **BR-039**: Completed financial transaction records MUST NOT be editable or deletable through ordinary user actions.
- **BR-040**: Access audit records are distinct from financial transaction records.
- **BR-041**: Shared Business Account credentials are not an approved application workflow.

### Security Requirements

- **SEC-001**: Users MUST authenticate before accessing accounts, histories, money operations, membership actions, invitations, or approval actions.
- **SEC-002**: Personal users MUST be denied Business functionality and Business users MUST be denied Personal functionality.
- **SEC-003**: Business Users MUST access only Business Accounts where they have active accepted membership.
- **SEC-004**: Removed Business Users MUST immediately lose access to the affected Business Account.
- **SEC-005**: Only AUTHORISERS may invite, assign invitation roles, promote, remove, approve, or reject.
- **SEC-006**: The final AUTHORISER MUST NOT be removable.
- **SEC-007**: Passwords MUST never appear in account pages, histories, recipient confirmations, access audit entries, or error outputs.
- **SEC-008**: Safe recipient confirmation MUST NOT expose sensitive email or credential details.
- **SEC-009**: Business membership, invitation, role assignment, promotion, removal, approval, rejection, cancellation, financial validation, and access control MUST be enforced server-side.
- **SEC-010**: No secrets, Django secret keys, plaintext passwords, tokens, environment files containing secrets, or local database files may be committed to GitHub.

### UI/UX Requirements

- **UX-001**: The interface MUST retain the premium "Midnight Ledger" visual direction: clean, confident, modern, high contrast, distinctive, and suitable for desktop-first macOS use with narrow-width usability.
- **UX-002**: Public registration MUST present a polished account-type choice: Open a Personal Account or Open a Business Account.
- **UX-003**: Personal registration MUST explain individual use, phone-number transfer receipt, no opening deposit, and SGD 0.00 starting balance.
- **UX-004**: Business registration MUST explain company use, UEN transfer receipt, SGD 7,000.00 opening funds, team access, membership roles, and approval controls.
- **UX-005**: Personal login navigation MUST include Dashboard, Personal Account, Transfer, Transactions, and Sign Out.
- **UX-006**: Personal users MUST NOT see Business administration, Members, Access Audit, or Business approval navigation.
- **UX-007**: Business login navigation MUST include Business Dashboard, company selector when multiple memberships exist, Deposit, Request Withdrawal, Request Transfer, Approvals, Members, Access Audit, Transactions, and Sign Out.
- **UX-008**: Business Dashboard MUST show selected Business Account name, UEN, current balance, SGD 7,000.00 retained-minimum reminder, current user's role, pending request count, role-appropriate quick actions, recent transactions, and recent outgoing-request activity.
- **UX-009**: Member Management MUST show invite controls, membership list, current roles, promote action, and remove action to AUTHORISERS where allowed.
- **UX-010**: Member Management for MEMBERS MUST hide management controls or present read-only membership information while server-side permissions remain authoritative.
- **UX-011**: Approval screens MUST show requester, requester role, operation type, recipient confirmation for transfers, amount, current balance, projected balance, retained-minimum compliance, permitted role-based actions, and status history.
- **UX-012**: Transaction, Approval, and Access Audit history views MUST be clearly labelled as separate views.
- **UX-013**: Workflow records and access-management events MUST NOT visually resemble completed money movements.
- **UX-014**: Transfer flow MUST require source account, recipient account type, matching identifier, SGD amount, safe recipient confirmation, review, submission, and completed/PENDING/rejected outcome.
- **UX-015**: Forms MUST use visible labels, inline validation messages, and clear primary actions.
- **UX-016**: Final or consequential financial, approval, invitation, promotion, and removal actions MUST show clear review or confirmation.
- **UX-017**: Statuses MUST be communicated with text and not colour alone.
- **UX-018**: The UI MUST provide polished empty, success, error, PENDING, REJECTED, CANCELLED, FAILED, and COMPLETED states.
- **UX-019**: Monetary values MUST display the SGD marker and exactly two decimal places.
- **UX-020**: Interactive controls MUST support keyboard navigation and visible focus states.
- **UX-021**: Dashboard cards, forms, approval requests, member lists, and histories MUST remain readable at narrow browser widths without horizontal scrolling for normal use.

### Non-Functional Requirements

- **NFR-001**: The feature MUST remain within the constitutionally approved MVP scope and not introduce unapproved product behaviour.
- **NFR-002**: The specification MUST remain technology-agnostic and defer implementation architecture to planning.
- **NFR-003**: Error messages MUST clearly explain what prevented an invalid action without exposing sensitive information.
- **NFR-004**: Financial operation completion MUST be atomic: either all balance and completed-record changes succeed or none occur.
- **NFR-005**: Each business rule MUST remain traceable from constitution to acceptance criteria, plan, tasks, code component, and automated test.
- **NFR-006**: Primary target is a modern desktop browser on macOS, with usable narrower-width behavior.
- **NFR-007**: Business membership and approval actions MUST be attributable to authenticated individual login identities.
- **NFR-008**: Access changes MUST take effect immediately for authorization decisions.

### Mandatory Test Requirements

- **TEST-001**: Verify Personal registration creates Personal-only access and one Personal Account.
- **TEST-002**: Verify Business registration creates Business-only access, Business Account, initial AUTHORISER membership, and opening-deposit transaction.
- **TEST-003**: Verify duplicate email rejection across Personal and Business identities.
- **TEST-004**: Verify Personal login cannot access Business pages or accept Business invitations.
- **TEST-005**: Verify Business login cannot access Personal pages.
- **TEST-006**: Verify separate credentials are required for a person needing both contexts.
- **TEST-007**: Verify Personal Account starts at SGD 0.00 and requires unique phone number.
- **TEST-008**: Verify duplicate Personal phone rejection.
- **TEST-009**: Verify Business registration requires display name, unique UEN, and opening deposit of SGD 7,000.00 or more.
- **TEST-010**: Verify Business registration rejects missing/duplicate UEN and opening deposit below SGD 7,000.00.
- **TEST-011**: Verify secure password hashing and no password exposure.
- **TEST-012**: Verify successful positive deposits for Personal and Business Accounts.
- **TEST-013**: Verify MEMBER and AUTHORISER may deposit into Business Account without approval.
- **TEST-014**: Verify rejection of zero, negative, malformed, non-numeric, non-SGD, and excessive-precision money inputs.
- **TEST-015**: Verify successful Personal withdrawal and full-balance withdrawal to SGD 0.00.
- **TEST-016**: Verify Personal withdrawal that would make balance negative is rejected.
- **TEST-017**: Verify successful Personal outgoing transfer and full-balance transfer to SGD 0.00.
- **TEST-018**: Verify Personal outgoing transfer that would make balance negative is rejected.
- **TEST-019**: Verify Personal recipient lookup by phone number.
- **TEST-020**: Verify Business recipient lookup by UEN.
- **TEST-021**: Verify unknown phone, unknown UEN, identifier mismatch, and self-transfer rejection.
- **TEST-022**: Verify completed transfer creates one operation ID and two linked UUID transaction records.
- **TEST-023**: Verify MEMBER may submit withdrawal and transfer requests.
- **TEST-024**: Verify AUTHORISER may submit withdrawal and transfer requests.
- **TEST-025**: Verify PENDING requests do not move funds, reserve funds, or create completed financial records.
- **TEST-026**: Verify MEMBER cannot approve, reject, invite, assign roles, promote, remove, or cancel another user's request.
- **TEST-027**: Verify AUTHORISER may approve any PENDING request and one approval is sufficient.
- **TEST-028**: Verify AUTHORISER may approve their own PENDING request.
- **TEST-029**: Verify AUTHORISER may reject any PENDING request.
- **TEST-030**: Verify MEMBER may cancel own PENDING request only.
- **TEST-031**: Verify AUTHORISER may cancel any PENDING request.
- **TEST-032**: Verify no persisted APPROVED status exists.
- **TEST-033**: Verify terminal statuses cannot be actioned again.
- **TEST-034**: Verify multiple PENDING requests may coexist and are independently revalidated.
- **TEST-035**: Verify successful Business outgoing completion may leave exactly SGD 7,000.00.
- **TEST-036**: Verify Business outgoing approval fails at SGD 6,999.99 with FAILED status, no money movement, and no completed financial records.
- **TEST-037**: Verify AUTHORISER can invite MEMBER and AUTHORISER roles.
- **TEST-038**: Verify invitations grant no access before acceptance.
- **TEST-039**: Verify invited Business-only login can accept invitation.
- **TEST-040**: Verify new Business-only registration from invitation can accept invitation.
- **TEST-041**: Verify Personal-only login cannot accept Business invitation.
- **TEST-042**: Verify Business User can belong to multiple Business Accounts.
- **TEST-043**: Verify removal from one Business Account preserves other memberships.
- **TEST-044**: Verify AUTHORISER may promote MEMBER to AUTHORISER.
- **TEST-045**: Verify AUTHORISER may remove MEMBER.
- **TEST-046**: Verify AUTHORISER may remove another AUTHORISER only when another AUTHORISER remains.
- **TEST-047**: Verify final AUTHORISER removal is rejected.
- **TEST-048**: Verify AUTHORISER-to-MEMBER demotion is rejected.
- **TEST-049**: Verify removed user immediately loses access.
- **TEST-050**: Verify Access Audit History records creation, invitations, acceptances, role assignments, promotions, and removals.
- **TEST-051**: Verify Transaction History contains completed financial movements only.
- **TEST-052**: Verify Approval History contains Business outgoing request workflow records.
- **TEST-053**: Verify Access Audit History is separate from Transaction History and Approval History.
- **TEST-054**: Verify unauthorised account, history, membership, approval, and financial operation access is denied.
- **TEST-055**: Verify Midnight Ledger registration choice, Personal navigation, Business navigation, role-aware controls, labelled forms, confirmations, accessibility, and narrow-width usability.

### Key Entities *(include if feature involves data)*

- **Personal Login Identity**: A registered identity with Personal Account access only, unique email, username, and securely hashed password.
- **Business Login Identity**: A registered identity with Business Account access only, unique email, username, and securely hashed password.
- **Personal Account**: An SGD account created during Personal registration with no opening deposit, no minimum balance, and one unique phone number for receiving transfers.
- **Business Account**: A company-owned shared SGD account created during Business registration with business display name, unique UEN, opening deposit of at least SGD 7,000.00, and at least one AUTHORISER membership.
- **Business User**: A Business login identity that may hold active memberships in one or more Business Accounts.
- **Business Membership**: The relationship granting a Business User access to a Business Account with MEMBER or AUTHORISER role.
- **Invitation**: A pending access offer issued by an AUTHORISER to an email address for a specific Business Account and role.
- **Access Audit Event**: An audit record for Business Account access-management activity.
- **Money Operation**: A requested deposit, withdrawal, or transfer with an SGD amount, validation outcome, and account/role-specific completion rules.
- **Business Outgoing Request**: A workflow record for an outgoing Business withdrawal or transfer with status PENDING, COMPLETED, REJECTED, CANCELLED, or FAILED.
- **Completed Financial Transaction Record**: An immutable audit record for a completed deposit, withdrawal, transfer debit, transfer credit, or Business opening deposit.
- **Transfer Operation**: The shared identity of a completed transfer that links one sender debit record and one recipient credit record.
- **Transaction History**: The view of completed financial movement records only.
- **Approval History**: The view of Business outgoing workflow requests and outcomes.
- **Access Audit History**: The view of Business membership, invitation, role, and removal events.

### Banking Rule Coverage *(mandatory for banking features)*

- **Technology Scope**: The feature remains a specification of the constitutionally approved MVP only; planning must stay within the approved local stack and must not add alternative databases, frontend frameworks, payment gateways, external bank integrations, cloud infrastructure, microservices, message queues, third-party authentication, OTP verification, or external UEN verification.
- **MVP Scope**: The feature is limited to Personal and Business registration, authentication, Personal Accounts, Business Accounts, Business memberships, invitations, role management, deposits, withdrawals, transfers, Transaction History, Approval History, Access Audit History, premium UI/UX, tests, traceability, and local deployment readiness.
- **Separate Identity**: FR-001 through FR-010 and BR-007 through BR-009 define mutually exclusive Personal and Business login contexts.
- **Personal Account Rules**: FR-011 through FR-019 and BR-010 through BR-013 define Personal Account creation, phone recipient identity, no opening deposit, no retained minimum, and no negative balance.
- **Business Account and Membership Rules**: FR-020 through FR-048 and BR-014 through BR-022 define Business Account creation, UEN identity, initial AUTHORISER, multi-account membership, MEMBER and AUTHORISER roles, invitations, promotions, removals, and last-AUTHORISER protection.
- **Financial Rules**: FR-015 through FR-019, FR-030 through FR-037, FR-055 through FR-073, and BR-001 through BR-006, BR-023 through BR-038 define money validation, deposits, withdrawals, transfers, retained minimum, approval, atomicity, UUID records, and no completed records on failed paths.
- **Recipient Identity**: FR-049 through FR-054 and BR-034 through BR-036 define Personal phone lookup, Business UEN lookup, mismatched identifier rejection, unknown identifier rejection, and self-transfer rejection.
- **Business Approval**: FR-057 through FR-068 and BR-025 through BR-033 define PENDING requests, AUTHORISER approval, one-approval threshold, self-approval, cancellation, rejection, FAILED, multiple PENDING requests, and no APPROVED status.
- **Histories and Auditability**: FR-074 through FR-080 and BR-039 through BR-041 define Transaction History, Approval History, Access Audit History, authenticated attribution, and no shared credentials.
- **Security**: SEC-001 through SEC-010 define authentication, context separation, membership access, removed-user access loss, authoriser-only actions, final-AUTHORISER protection, password safety, safe recipient confirmation, server-side enforcement, and secret management.
- **UI/UX and Accessibility**: UX-001 through UX-021 and NFR-006 through NFR-008 define Midnight Ledger registration choice, context-specific navigation, dashboards, member management, approval screens, histories, states, accessibility, and responsive behavior.
- **Mandatory Tests**: TEST-001 through TEST-055 provide the required traceable test inventory.

### Traceability Matrix *(mandatory)*

| Rule ID | Requirement ID | Acceptance Criteria | Plan Reference | Task ID | Code Component | Test ID / Path |
|---------|----------------|---------------------|----------------|---------|----------------|----------------|
| BR-007 to BR-009 | FR-001 to FR-010 | User Story 1 identity separation scenarios | Pending v2.0.0 plan regeneration | Pending | Pending | TEST-001 to TEST-006 |
| BR-010 to BR-013 | FR-011 to FR-019 | User Story 2 Personal Account scenarios | Pending v2.0.0 plan regeneration | Pending | Pending | TEST-007 to TEST-018 |
| BR-014 to BR-022 | FR-020 to FR-048 | User Story 3 and 4 Business Account, membership, invitation, promotion, removal scenarios | Pending v2.0.0 plan regeneration | Pending | Pending | TEST-009 to TEST-010, TEST-037 to TEST-049 |
| BR-001 to BR-006, BR-023 to BR-033 | FR-030 to FR-037, FR-057 to FR-068 | Business deposit, request, approval, retained-minimum, no-reservation, and failed approval scenarios | Pending v2.0.0 plan regeneration | Pending | Pending | TEST-012 to TEST-014, TEST-023 to TEST-036 |
| BR-034 to BR-038 | FR-049 to FR-073 | Transfer recipient, self-transfer, linked records, UUID, and atomicity scenarios | Pending v2.0.0 plan regeneration | Pending | Pending | TEST-019 to TEST-022 |
| BR-039 to BR-041 | FR-074 to FR-080 | Transaction, Approval, Access Audit, and authenticated attribution scenarios | Pending v2.0.0 plan regeneration | Pending | Pending | TEST-050 to TEST-054 |
| SEC-001 to SEC-010 | FR-006 to FR-010, FR-029, FR-034 to FR-048, FR-078 to FR-080 | Access denial, role restriction, removed-user, final-AUTHORISER, and safe-output scenarios | Pending v2.0.0 plan regeneration | Pending | Pending | TEST-004 to TEST-006, TEST-026, TEST-041, TEST-047, TEST-049, TEST-054 |
| UX-001 to UX-021 | User Stories 7 and 8 | Registration choice, Personal nav, Business nav, role-aware controls, approval, histories, and responsive scenarios | Pending v2.0.0 plan regeneration | Pending | Pending | TEST-055 |
| NFR-001 to NFR-008 | All BR, FR, SEC, UX, and TEST identifiers | Scope, atomicity, traceability, attribution, and immediate access-effect scenarios | Pending v2.0.0 plan regeneration | Pending | Pending | TEST-001 to TEST-055 |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successful Personal registrations create Personal-only access, one Personal Account, unique phone recipient identifier, and starting balance SGD 0.00.
- **SC-002**: 100% of successful Business registrations create Business-only access, one Business Account, unique UEN, opening deposit transaction, and creator AUTHORISER membership.
- **SC-003**: 100% of duplicate email, duplicate Personal phone, duplicate Business UEN, missing UEN, and insufficient Business opening deposit attempts are rejected with no partial account or membership creation.
- **SC-004**: 100% of Personal login attempts to access Business functionality are denied.
- **SC-005**: 100% of Business login attempts to access Personal functionality are denied.
- **SC-006**: 100% of active Business Account access is through individual Business User memberships, not shared credentials.
- **SC-007**: 100% of Business Accounts have at least one active AUTHORISER after every membership-management action.
- **SC-008**: 100% of invitation, acceptance, promotion, and removal actions appear in Access Audit History and do not appear in Transaction History.
- **SC-009**: 100% of removed Business Users lose access to the affected Business Account immediately.
- **SC-010**: 100% of MEMBER attempts to perform AUTHORISER-only actions are denied.
- **SC-011**: 100% of completed Business outgoing withdrawals and transfers leave the Business Account with at least SGD 7,000.00.
- **SC-012**: 100% of PENDING Business outgoing requests leave displayed balances unchanged and reserve no funds.
- **SC-013**: If multiple PENDING Business requests exist, each approval attempt is independently revalidated and may become FAILED if current rules no longer pass.
- **SC-014**: 100% of successful deposits and completed withdrawals are visible in Transaction History with amount in SGD, status, type, timestamp, account, and UUID transaction ID.
- **SC-015**: 100% of successful transfers show one sender debit record and one recipient credit record, each with its own UUID transaction ID and the same transfer operation ID.
- **SC-016**: 100% of failed, rejected, PENDING, CANCELLED, or FAILED operations leave balances unchanged and create no completed financial transaction records.
- **SC-017**: Users can distinguish Transaction History, Approval History, and Access Audit History.
- **SC-018**: 100% of Personal recipient transfers require Personal Account destination plus phone number, and 100% of Business recipient transfers require Business Account destination plus UEN.
- **SC-019**: 100% of mismatched recipient account type and identifier combinations are rejected before money moves.
- **SC-020**: 100% of monetary values displayed in primary account, transfer, approval, and transaction views include the SGD marker and exactly two decimal places.
- **SC-021**: Primary registration, sign-in, dashboard, transfer, approval, member-management, and history flows are usable with keyboard navigation and visible focus states.
- **SC-022**: Dashboard cards, member lists, transfer forms, approval requests, and histories remain readable at narrow browser widths without horizontal scrolling for normal use.
- **SC-023**: Every core business rule in this specification has at least one acceptance scenario and at least one `TEST-###` identifier for later automated testing.
- **SC-024**: Any implementation based on the previous Personal-Account-authoriser model is identified as requiring refactoring before v2.0.0 completion.

## Assumptions

- A login identity has exactly one access context: Personal or Business.
- Personal Account registration creates the Personal Account immediately; a separate Personal Account setup step is no longer part of the v2.0.0 product flow.
- Business Account registration creates the Business Account and initial AUTHORISER membership immediately when all validation passes.
- A Business User may be a MEMBER or AUTHORISER on different Business Accounts at the same time.
- The MVP supports inviting by email, but does not require external email delivery integration unless later approved; invitation delivery mechanics belong to planning.
- The MVP does not support AUTHORISER demotion to MEMBER.
- The MVP does not support shared company credentials.
- Date/time display must be understandable to users and consistent within histories, while exact formatting belongs to later design work.
- Existing implementation and planning artifacts based on the superseded one-login-owning-both-accounts model require later refactoring and regeneration.
- This specification intentionally avoids implementation decisions, including database tables, models, URLs, form classes, templates, middleware, modules, test framework, server configuration, deployment details, UI libraries, CSS frameworks, and JavaScript frameworks.

## Required Next Validation

This specification has been clarified for constitution v2.0.0 and MUST be validated through `/speckit.checklist` before regenerating `/speckit.plan`.
