# Feature Specification: Banking MVP

**Feature Branch**: `001-banking-mvp`

**Created**: 2026-05-25

**Status**: Draft - revised for constitution v3.0.0

**Input**: User description: "Build the MVP for a Personal and Business banking application that allows users to securely manage SGD accounts, deposit and withdraw funds, transfer money using phone numbers and UENs, provision Business employee access credentials, approve outgoing Business transactions, and view auditable Transaction, Approval, and Access Audit histories."

## Clarifications

### Session 2026-05-25

- Q: What is the MVP relationship between a user, Personal Account, Business Account, and Business Account activation? -> A: Superseded by constitution v2.0.0 and v3.0.0; Personal and Business access remain separate, and a Personal Account never authorises a Business Account.
- Q: How do Business Account outgoing approval, revalidation, and lifecycle work? -> A: Submission creates only a PENDING request with no fund reservation; approval revalidates amount, current balance, retained minimum, and authorising role; PENDING may become COMPLETED, REJECTED, CANCELLED, or FAILED, and final states cannot be acted on again.
- Q: How are Transaction History and Approval History separated? -> A: Transaction History shows completed financial records only; Approval History shows Business Account outgoing requests, with completed Business outgoing operations appearing in both histories.
- Q: How are transfer recipients identified after constitution v1.1.0? -> A: Personal Account destinations use phone number, Business Account destinations use UEN, and sender must choose recipient account type before entering the matching identifier.
- Q: What transfer and monetary edge rules are final? -> A: Safe recipient confirmation is required; self-transfers are rejected; SGD amounts use at most two decimal places and reject zero, negative, text, malformed, non-numeric, and excessive-precision values.

### Session 2026-05-26

- Q: How does constitution v3.0.0 change Business access onboarding? -> A: Invitations and multi-Business memberships are superseded. An active AUTHORISER provisions individual Business Employee Access Logins scoped to exactly one Business Account, with temporary-password change, access status, deactivation, reactivation, and access audit requirements.

## Final Product Terminology

- **Personal Account**: An individual bank account holding an individual's funds.
- **Business Account**: A company-owned bank account holding company funds, identified for incoming transfers by its UEN.
- **Personal Login**: A login identity that accesses exactly one Personal Account and Personal functionality only.
- **Business Employee Access Login**: An individual employee login credential provisioned for access to exactly one Business Account. It is not a Personal Account, is not a separate Business Account, has no balance, has no receiving phone number or UEN, and exists only to let one employee operate one company Business Account according to assigned role and access state.
- **Business Employee**: A person using a Business Employee Access Login.
- **MEMBER**: An active employee-access role permitting Business Account viewing, deposits, and outgoing transaction requests, but not approvals or access administration.
- **AUTHORISER**: An active employee-access role permitting MEMBER actions plus outgoing transaction approval and employee-access administration.
- **Access State**: The employee access lifecycle state: `PASSWORD_CHANGE_REQUIRED`, `ACTIVE`, or `DEACTIVATED`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register for the Correct Account Product (Priority: P1)

A new person chooses Personal Account registration or Business Account registration. Personal registration creates a Personal Login and one Personal Account. Business Account registration creates a company Business Account and the initial AUTHORISER Business Employee Access Login for that Business Account.

**Why this priority**: Product and login boundaries are foundational. No financial, approval, or employee-access workflow can be trusted if Personal and Business Account access overlap.

**Independent Test**: Personal registration creates Personal-only access and one Personal Account. Business registration creates a Business Account and initial AUTHORISER employee access scoped to that account only. Duplicate emails are rejected globally.

**Acceptance Scenarios**:

1. **Given** no registered login has email `p@example.test` and no Personal Account has phone `91234567`, **When** a person registers for Personal Account access with display name, email, password, password confirmation, and phone number, **Then** one Personal Login and one Personal Account are created with balance SGD 0.00.
2. **Given** an email is already used by any Personal Login or Business Employee Access Login, **When** registration attempts to use that email, **Then** registration is rejected and no duplicate login is created.
3. **Given** a Personal Login is authenticated, **When** it attempts to access Business Account dashboard, approvals, Team Access, Access Audit, or Business financial actions, **Then** access is denied.
4. **Given** a Business Employee Access Login is authenticated, **When** it attempts to access Personal Account pages or Personal money operations, **Then** access is denied.
5. **Given** an individual needs both a Personal Account and employee access to a Business Account, **When** both access types are needed, **Then** separate credentials with different unique email addresses are required.

---

### User Story 2 - Use a Personal Account (Priority: P1)

A Personal Account holder manages one Personal Account with a unique receiving phone number, no opening deposit, no minimum balance, valid deposits, valid withdrawals, outgoing transfers, and completed Transaction History.

**Why this priority**: Personal Account behavior proves the individual banking flow, phone recipient identity, no-minimum-balance rule, and negative-balance protection.

**Independent Test**: A Personal Account starts at SGD 0.00, rejects duplicate phone numbers, accepts valid money operations, allows full-balance withdrawal or transfer to SGD 0.00, and rejects operations that would make the balance negative.

**Acceptance Scenarios**:

1. **Given** a Personal Account has just been registered, **When** the Personal Dashboard is viewed, **Then** it shows balance SGD 0.00 and the unique receiving phone number.
2. **Given** another Personal Account already uses phone `91234567`, **When** Personal registration attempts to use phone `91234567`, **Then** registration is rejected and no duplicate phone identifier is created.
3. **Given** a Personal Account with balance SGD 0.00, **When** SGD 100.00 is deposited, **Then** the balance becomes SGD 100.00 and one completed deposit transaction with UUID transaction ID is recorded.
4. **Given** a Personal Account with balance SGD 100.00, **When** SGD 100.00 is withdrawn, **Then** the balance becomes SGD 0.00 and one completed withdrawal transaction is recorded.
5. **Given** a Personal Account with balance SGD 30.00, **When** SGD 30.01 is requested for withdrawal, **Then** the withdrawal is rejected, balance remains SGD 30.00, and no completed withdrawal transaction is recorded.
6. **Given** a Personal Account with balance SGD 75.00 and a known Personal recipient phone number, **When** SGD 25.00 is transferred, **Then** sender and recipient balances update atomically and linked transfer records are created.
7. **Given** a Personal Account with balance SGD 75.00 and a known Business recipient UEN, **When** SGD 75.00 is transferred, **Then** the Personal balance becomes SGD 0.00 and the Business Account receives the incoming transfer without approval.
8. **Given** a Personal Account with balance SGD 75.00, **When** SGD 75.01 is requested for transfer, **Then** the transfer is rejected and no balance or completed transaction record changes.

---

### User Story 3 - Create a Business Account as Initial AUTHORISER (Priority: P1)

An initial AUTHORISER opens a company Business Account with a unique UEN and an opening deposit of at least SGD 7,000.00. The registration creates the Business Account, the initial AUTHORISER Business Employee Access Login, an opening-deposit transaction, and initial Access Audit events.

**Why this priority**: Business Account creation establishes company funds, UEN receipt identity, retained minimum, and the first accountable employee credential.

**Independent Test**: Business Account registration succeeds only with unique Authoriser email, display name, business display name, unique UEN, valid opening deposit, completed opening transaction, and initial AUTHORISER Access Audit records.

**Acceptance Scenarios**:

1. **Given** no Business Account uses UEN `202612345A`, **When** Business Account registration uses opening deposit exactly SGD 7,000.00, **Then** the Business Account is created, the balance is SGD 7,000.00, and the creator is an active AUTHORISER employee for that Business Account only.
2. **Given** no Business Account uses UEN `202612346B`, **When** Business Account registration uses opening deposit greater than SGD 7,000.00, **Then** the Business Account is created with the deposited balance.
3. **Given** the initial Authoriser login email is already used, **When** registration is submitted, **Then** registration is rejected.
4. **Given** Business Account registration omits business display name, **When** it is submitted, **Then** registration is rejected.
5. **Given** Business Account registration omits UEN or uses a duplicate UEN, **When** it is submitted, **Then** registration is rejected.
6. **Given** Business Account registration uses opening deposit SGD 6,999.99, **When** it is submitted, **Then** registration is rejected and no Business Account, employee login, opening transaction, or Access Audit event is created.
7. **Given** opening deposit input is zero, negative, malformed, non-numeric, or has excessive decimal precision, **When** registration is submitted, **Then** registration is rejected.
8. **Given** a Business Account is created, **When** histories are viewed, **Then** Transaction History includes one completed Business opening-deposit transaction and Access Audit History includes Business Account creation plus initial AUTHORISER creation.

---

### User Story 4 - Provision and Govern Employee Access (Priority: P1)

An active AUTHORISER provisions individual Business Employee Access Logins for one Business Account, assigns MEMBER or AUTHORISER role, controls temporary-password and access-state workflows, promotes MEMBERS, deactivates or reactivates eligible employees, and preserves Access Audit History.

**Why this priority**: Company-owned account access requires individual credentials, scoped employee accountability, and auditable security administration rather than invitations or shared credentials.

**Independent Test**: AUTHORISER-only access administration succeeds or fails according to role, access-state, and last-AUTHORISER rules; employees cannot use normal Business functions until password change; all access-governance actions are auditable without exposing passwords.

**Acceptance Scenarios**:

1. **Given** an active AUTHORISER enters employee display name, unique email, role MEMBER, temporary password, and confirmation, **When** employee access is created, **Then** one MEMBER Business Employee Access Login scoped to the current Business Account is created in `PASSWORD_CHANGE_REQUIRED` state and Access Audit History records access creation plus temporary password issuance.
2. **Given** an active AUTHORISER enters employee display name, unique email, role AUTHORISER, temporary password, and confirmation, **When** employee access is created, **Then** one AUTHORISER Business Employee Access Login scoped to the current Business Account is created in `PASSWORD_CHANGE_REQUIRED` state.
3. **Given** a MEMBER attempts to create employee access, **When** the action is submitted, **Then** it is denied.
4. **Given** an employee email is already used by any login, **When** an AUTHORISER attempts to create employee access with that email, **Then** the action is rejected.
5. **Given** a newly created employee signs in using the temporary password, **When** authentication succeeds, **Then** the employee can access only the mandatory password-change flow and sign-out.
6. **Given** an employee in `PASSWORD_CHANGE_REQUIRED` state attempts to open Business Dashboard, histories, deposits, approvals, or Team Access before changing password, **When** access is attempted, **Then** the employee is redirected to or denied except for password change.
7. **Given** an employee changes the temporary password to a private password, **When** the change succeeds, **Then** the employee access state becomes `ACTIVE` and Access Audit History records activation or first-login password change.
8. **Given** employee access has been provisioned or reset, **When** ordinary pages, employee lists, or Access Audit History are viewed, **Then** plaintext temporary passwords, chosen passwords, and password hashes are not displayed or retrievable.
9. **Given** an AUTHORISER promotes an active MEMBER to AUTHORISER, **When** the action succeeds, **Then** the employee can perform AUTHORISER actions and Access Audit History records the promotion.
10. **Given** an AUTHORISER attempts to demote an AUTHORISER to MEMBER, **When** the action is submitted, **Then** it is rejected because demotion is outside MVP scope.
11. **Given** an active AUTHORISER deactivates a MEMBER, **When** the action succeeds, **Then** the MEMBER immediately loses Business Account access and Access Audit History records deactivation.
12. **Given** at least two active AUTHORISERS exist, **When** one AUTHORISER deactivates another AUTHORISER, **Then** deactivation succeeds only if at least one active AUTHORISER remains afterward.
13. **Given** only one active AUTHORISER remains, **When** deactivation of that AUTHORISER is attempted, **Then** deactivation is rejected and Access Audit History records the rejected final-AUTHORISER attempt where retained.
14. **Given** a deactivated employee is reactivated by an AUTHORISER, **When** a new temporary password and confirmation are provided, **Then** access state becomes `PASSWORD_CHANGE_REQUIRED`, the employee must change password again before normal access, and Access Audit History records reactivation plus temporary password issuance.
15. **Given** a deactivated employee attempts to sign in or access Business Account data, **When** access is attempted, **Then** normal Business functionality and all histories are denied.

---

### User Story 5 - Transfer Money Safely (Priority: P1)

A Personal Login or active Business Employee selects recipient account type, enters the matching identifier, reviews safe recipient confirmation, and receives a completed, PENDING, or rejected outcome according to source account rules.

**Why this priority**: Account-type-specific recipient identification prevents misdirected money and preserves Personal phone versus Business UEN distinction.

**Independent Test**: Recipient lookup uses phone for Personal destinations and UEN for Business destinations, rejects mismatches and unknown identifiers, and creates linked transfer records only after completion.

**Acceptance Scenarios**:

1. **Given** a Personal sender selects Personal Account destination and enters a known phone number, **When** they confirm a valid transfer, **Then** the transfer completes immediately.
2. **Given** a Personal sender selects Business Account destination and enters a known UEN, **When** they confirm a valid transfer, **Then** the transfer completes immediately as incoming Business funds.
3. **Given** an active MEMBER or AUTHORISER selects Personal Account destination and enters a known phone number, **When** they submit a valid Business outgoing transfer, **Then** a PENDING Business outgoing request is created and no funds move.
4. **Given** an active MEMBER or AUTHORISER selects Business Account destination and enters a known UEN, **When** they submit a valid Business outgoing transfer, **Then** a PENDING Business outgoing request is created and no funds move.
5. **Given** the sender selects Personal Account destination and enters an unknown phone number, **When** transfer is attempted, **Then** it is rejected.
6. **Given** the sender selects Business Account destination and enters an unknown UEN, **When** transfer is attempted, **Then** it is rejected.
7. **Given** the sender selects Personal Account destination but enters a UEN, **When** transfer is attempted, **Then** it is rejected as an identifier/account-type mismatch.
8. **Given** the sender selects Business Account destination but enters a phone number, **When** transfer is attempted, **Then** it is rejected as an identifier/account-type mismatch.
9. **Given** a sender attempts to transfer from an account back to the same account, **When** transfer is attempted, **Then** it is rejected.
10. **Given** a completed transfer exists, **When** Transaction History is viewed, **Then** sender debit and recipient credit records each have their own UUID transaction ID and share one transfer operation ID.

---

### User Story 6 - Submit and Resolve Business Outgoing Requests (Priority: P1)

An active MEMBER or AUTHORISER submits outgoing Business withdrawal or transfer requests. AUTHORISERS approve, reject, or cancel requests according to role rules. MEMBERS may cancel only their own PENDING requests.

**Why this priority**: Role-based approval protects outgoing company funds while supporting multiple PENDING requests without reserving funds.

**Independent Test**: PENDING requests do not reserve funds, AUTHORISER approval threshold is one, approval revalidates retained minimum, and terminal states cannot be changed again.

**Acceptance Scenarios**:

1. **Given** an active MEMBER submits a Business withdrawal request, **When** the amount is valid, **Then** a PENDING request is created and no balance changes.
2. **Given** an active MEMBER submits a Business outgoing transfer request, **When** the amount and recipient are valid, **Then** a PENDING request is created and no completed transfer records are created.
3. **Given** an active AUTHORISER submits a Business outgoing request, **When** the amount is valid, **Then** a PENDING request is created.
4. **Given** an AUTHORISER submitted their own PENDING request, **When** they approve it and all current financial rules pass, **Then** the request becomes COMPLETED and money moves atomically.
5. **Given** a different active AUTHORISER approves a PENDING request, **When** all current financial rules pass, **Then** one AUTHORISER approval is sufficient for completion.
6. **Given** a MEMBER attempts to approve or reject a PENDING request, **When** the action is submitted, **Then** the action is denied.
7. **Given** a MEMBER submitted a PENDING request, **When** that same MEMBER cancels it, **Then** it becomes CANCELLED and no funds move.
8. **Given** a MEMBER attempts to cancel another employee's PENDING request, **When** the action is submitted, **Then** the action is denied.
9. **Given** an AUTHORISER cancels any PENDING request, **When** the action is submitted, **Then** it becomes CANCELLED and no funds move.
10. **Given** an AUTHORISER rejects any PENDING request, **When** the action is submitted, **Then** it becomes REJECTED and no funds move.
11. **Given** a Business Account has multiple PENDING requests, **When** each is reviewed, **Then** none reserve funds and each is independently revalidated at approval time.
12. **Given** a Business Account has balance SGD 8,500.00 and two PENDING withdrawals for SGD 1,000.00 and SGD 500.01, **When** the first completes, **Then** the second fails at approval because completion would leave SGD 6,999.99.
13. **Given** a PENDING outgoing request would leave exactly SGD 7,000.00, **When** an AUTHORISER approves it, **Then** the request becomes COMPLETED.
14. **Given** a request is COMPLETED, REJECTED, CANCELLED, or FAILED, **When** any user attempts to change it again, **Then** the action is rejected.

---

### User Story 7 - Navigate the Midnight Ledger Interface (Priority: P2)

Users get a substantially upgraded premium "Midnight Ledger" server-rendered banking experience with separate Personal and Business navigation, clear role-based controls, strong hierarchy, polished operational data displays, safe confirmations, and accessible responsive behavior.

**Why this priority**: The MVP must feel like a credible banking product and corporate treasury access-control surface, not a basic administrative CRUD screen.

**Independent Test**: Personal users see only Personal navigation. Business Employees see Business navigation for their assigned Business Account only, with no Business Account selector, role-aware controls, Team Access, and separate history areas.

**Acceptance Scenarios**:

1. **Given** an unauthenticated visitor opens registration, **When** the page loads, **Then** it presents polished choices for "Open a Personal Account" and "Open a Business Account".
2. **Given** the user chooses Personal Account registration, **When** the form appears, **Then** it explains phone-number transfer receipt, no opening deposit, and SGD 0.00 starting balance.
3. **Given** the user chooses Business Account registration, **When** the form appears, **Then** it explains UEN transfer receipt, SGD 7,000.00 opening funds, employee access, and approval controls.
4. **Given** a Personal Login is signed in, **When** navigation is shown, **Then** it includes Dashboard, Personal Account, Deposit, Withdraw, Transfer, Transactions, and Sign Out only.
5. **Given** an active Business Employee is signed in, **When** navigation is shown, **Then** it includes Business Dashboard, Deposit, Request Withdrawal, Request Transfer, Approvals, Team Access, Access Audit, Transactions, and Sign Out, with no Invitations item and no Business Account selector.
6. **Given** an employee in `PASSWORD_CHANGE_REQUIRED` state is signed in, **When** navigation is shown, **Then** normal Business Account navigation is withheld and only mandatory password change and sign-out are available.
7. **Given** an active Business Employee views the Business Dashboard, **When** the page loads, **Then** it shows business name, UEN, employee role, access state where relevant, balance, retained-minimum reminder, usable available-outgoing-funds indicator where consistent with rules, pending count, recent completed transactions, recent approval activity, and Authoriser-only Team Access summary where applicable.
8. **Given** an AUTHORISER opens Team Access, **When** employee records are displayed, **Then** the page shows business name, UEN, current role, active employee count, AUTHORISER count, password-change-required count, deactivated count, employee role and status, and permitted actions.
9. **Given** a MEMBER opens Team Access, **When** employee records are displayed, **Then** access-administration controls are hidden or read-only and server-side permission checks still enforce restrictions.
10. **Given** Add Employee Access is used to create AUTHORISER access, **When** the confirmation step appears, **Then** it clearly states the security consequence of creating another AUTHORISER.
11. **Given** an approval detail is viewed, **When** the screen loads, **Then** it shows requester identity, requester role, operation type, recipient confirmation, amount, current balance, projected post-approval balance, retained-minimum compliance, permitted actions, and status history.
12. **Given** the browser width is narrow, **When** primary pages are used, **Then** content remains readable without ordinary-use horizontal scrolling.
13. **Given** standard desktop width is used, **When** Business Dashboard, Team Access, Approvals, and histories are viewed, **Then** there are no large unusable empty layout gaps in core content areas.

---

### User Story 8 - View Transaction, Approval, and Access Audit Histories (Priority: P2)

Users view completed financial movements in Transaction History, Business outgoing workflow records in Approval History, and Business access/security-governance activity in Access Audit History.

**Why this priority**: Trust depends on distinguishing completed money movement from approval workflow and access governance.

**Independent Test**: The three histories contain only their own record types and enforce Personal ownership or active Business Employee access permissions.

**Acceptance Scenarios**:

1. **Given** a Personal Account has completed deposits, withdrawals, and transfers, **When** the Personal Login views Transaction History, **Then** completed financial movements are shown with amount, status, timestamp, account, and UUID transaction ID.
2. **Given** a Business Account has opening deposit, deposits, completed withdrawals, completed transfers, and incoming credits, **When** an active Business Employee views Transaction History, **Then** only completed financial movements are shown.
3. **Given** Business outgoing requests exist in PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED status, **When** Approval History is viewed, **Then** requester employee, requester role, type, amount, destination where applicable, actioning AUTHORISER where applicable, status, dates, and safe outcome reason are shown.
4. **Given** Business Account creation, initial AUTHORISER creation, employee access creation, temporary-password issuance, password activation, promotion, deactivation, reactivation, and password reset events exist, **When** Access Audit History is viewed, **Then** access and security-governance events are shown separately from financial transactions.
5. **Given** PENDING, REJECTED, CANCELLED, or FAILED outgoing requests exist, **When** Transaction History is viewed, **Then** those workflow records are not displayed as completed money movement.
6. **Given** access audit events exist, **When** Transaction History is viewed, **Then** employee access, password, promotion, deactivation, and reactivation events are not displayed as financial transactions.
7. **Given** Access Audit History is viewed, **When** password-related events are displayed, **Then** password values and password hashes are not displayed.
8. **Given** a deactivated employee attempts to view Business Transaction History, Approval History, or Access Audit History, **When** access is attempted, **Then** access is denied immediately.

## Edge Cases

- Duplicate email across Personal Logins and Business Employee Access Logins.
- Personal registration with duplicate phone number.
- Personal Login attempts Business Account functionality.
- Business Employee Access Login attempts Personal Account functionality.
- Business Account registration with missing business display name.
- Business Account registration with missing or duplicate UEN.
- Business Account registration with opening deposit below SGD 7,000.00.
- Business Account registration with invalid, zero, negative, malformed, non-numeric, non-SGD, over-capacity, or excessive-precision opening deposit.
- MEMBER attempts to add employee access, reset passwords, promote, deactivate, reactivate, approve, reject, or cancel another employee's request.
- AUTHORISER attempts to create employee access with duplicate email.
- AUTHORISER attempts to create employee access with mismatched temporary password confirmation.
- New employee attempts normal Business Account access before mandatory password change.
- Employee in `PASSWORD_CHANGE_REQUIRED` state attempts balances, histories, deposits, approvals, requests, or Team Access.
- AUTHORISER attempts to retrieve or view another employee's existing or chosen password.
- AUTHORISER attempts administrative temporary-password reset for themselves.
- MEMBER attempts to reset any employee password.
- AUTHORISER attempts to deactivate the final active AUTHORISER.
- AUTHORISER attempts to demote an AUTHORISER to MEMBER.
- Deactivated employee attempts sign-in, normal Business Account actions, histories, or approvals.
- Reactivated employee attempts normal access before changing new temporary password.
- Attempt to attach one Business Employee Access Login to another Business Account.
- Attempt to show a multi-Business Account selector to an employee login.
- Zero, negative, malformed, non-numeric, non-SGD, over-capacity, or invalid-precision monetary inputs.
- Amounts with more than two decimal places.
- Personal Account withdrawal or transfer exceeding available balance.
- Business Account outgoing request attempted by a login that is not an active employee of that Business Account.
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

- **FR-001**: The system MUST support exactly two bank-account products: Personal Account and Business Account.
- **FR-002**: The system MUST require every login identity to have a globally unique email address and securely stored password.
- **FR-003**: The system MUST reject duplicate email registration across Personal Logins and Business Employee Access Logins.
- **FR-004**: The system MUST allow registered users to sign in and sign out.
- **FR-005**: The system MUST reject sign-in attempts with incorrect credentials without exposing which credential was incorrect.
- **FR-006**: The system MUST ensure Personal Logins access Personal Account functionality only.
- **FR-007**: The system MUST ensure Business Employee Access Logins access Business Account functionality only.
- **FR-008**: The system MUST reject Personal Login access to Business Dashboard, Team Access, Access Audit, approvals, and Business financial actions.
- **FR-009**: The system MUST reject Business Employee Access Login access to Personal Account pages and Personal money operations.
- **FR-010**: The system MUST require an individual needing both Personal Account and Business employee access to use separate credentials with different unique email addresses.
- **FR-011**: The system MUST create exactly one Personal Account during Personal Account registration.
- **FR-012**: The system MUST require Personal registration to include display name or username, unique login email, password, password confirmation, and unique receiving phone number.
- **FR-013**: The system MUST require a Personal Account to have one unique phone number used for receiving transfers.
- **FR-014**: The system MUST reject duplicate Personal Account phone numbers.
- **FR-015**: The system MUST create a Personal Account with balance SGD 0.00 and no opening deposit.
- **FR-016**: The system MUST allow Personal Account deposits of valid positive SGD amounts.
- **FR-017**: The system MUST allow Personal Account withdrawals of valid positive SGD amounts when the balance will not become negative.
- **FR-018**: The system MUST reject Personal Account withdrawals that would make the balance negative.
- **FR-019**: The system MUST allow Personal Account transfers of valid positive SGD amounts when the sender balance will not become negative.
- **FR-020**: The system MUST reject Personal Account transfers that would make the sender balance negative.
- **FR-021**: The system MUST require Business Account registration to include initial Authoriser display name, unique Authoriser login email, password, password confirmation, business display name, unique UEN, and opening deposit of at least SGD 7,000.00.
- **FR-022**: The system MUST create one Business Account during successful Business Account registration.
- **FR-023**: The system MUST create one Business Employee Access Login for the creator during successful Business Account registration.
- **FR-024**: The system MUST assign the creator the AUTHORISER role scoped only to the new Business Account.
- **FR-025**: The system MUST set the initial AUTHORISER access state to ACTIVE because the creator chooses their own secure password during registration.
- **FR-026**: The system MUST create one completed `BUSINESS_OPENING_DEPOSIT` financial transaction during successful Business Account registration.
- **FR-027**: The system MUST create Access Audit events for Business Account creation and initial AUTHORISER creation.
- **FR-028**: The system MUST reject Business Account registration when business display name is missing.
- **FR-029**: The system MUST reject Business Account registration when UEN is missing or already registered.
- **FR-030**: The system MUST reject Business Account registration when opening deposit is below SGD 7,000.00.
- **FR-031**: The system MUST reject Business Account registration when opening deposit is invalid, zero, negative, malformed, non-numeric, over-capacity, or has excessive decimal precision.
- **FR-032**: The system MUST ensure a Business Employee Access Login belongs to exactly one Business Account.
- **FR-033**: The system MUST NOT allow one Business Employee Access Login to access multiple Business Accounts.
- **FR-034**: The system MUST NOT provide a Business Account selector for employee logins in the MVP.
- **FR-035**: The system MUST support exactly two employee roles: MEMBER and AUTHORISER.
- **FR-036**: The system MUST support employee access states sufficient to represent `PASSWORD_CHANGE_REQUIRED`, `ACTIVE`, and `DEACTIVATED`.
- **FR-037**: The system MUST allow only active AUTHORISERS to create employee access for their own Business Account.
- **FR-038**: Employee access creation MUST require employee display name, unique login email, role, temporary password, and temporary password confirmation.
- **FR-039**: The system MUST set newly provisioned employee access to `PASSWORD_CHANGE_REQUIRED`.
- **FR-040**: The system MUST securely hash temporary passwords and MUST NOT retain or reveal plaintext temporary passwords after creation.
- **FR-041**: The system MUST require an employee in `PASSWORD_CHANGE_REQUIRED` state to change password before accessing Business Account balances, histories, deposits, requests, approvals, or Team Access.
- **FR-042**: The system MUST set employee access to ACTIVE after successful mandatory password change.
- **FR-043**: The system MUST reject MEMBER attempts to create employee access.
- **FR-044**: The system MUST allow an active AUTHORISER to reset another employee's password by issuing a new temporary password and confirmation.
- **FR-045**: The system MUST NOT allow an AUTHORISER to issue their own administrative temporary-password reset in the MVP.
- **FR-046**: The system MUST set employee access to `PASSWORD_CHANGE_REQUIRED` after an administrative temporary-password reset.
- **FR-047**: The system MUST ensure the previous password no longer grants access after an administrative temporary-password reset.
- **FR-048**: The system MUST allow active MEMBERS and AUTHORISERS to view their assigned Business Account dashboard, balance, Transaction History, Approval History, and Access Audit History.
- **FR-049**: The system MUST allow active MEMBERS and AUTHORISERS to deposit valid positive SGD amounts into their assigned Business Account without approval.
- **FR-050**: The system MUST allow active MEMBERS and AUTHORISERS to submit outgoing Business withdrawal requests.
- **FR-051**: The system MUST allow active MEMBERS and AUTHORISERS to submit outgoing Business transfer requests.
- **FR-052**: The system MUST allow an active MEMBER to cancel only their own PENDING outgoing requests.
- **FR-053**: The system MUST reject MEMBER attempts to approve, reject, cancel another employee's request, reset passwords, promote, deactivate, reactivate, or perform access administration.
- **FR-054**: The system MUST allow an active AUTHORISER to approve, reject, or cancel any PENDING outgoing Business request.
- **FR-055**: The system MUST allow an AUTHORISER to approve their own PENDING outgoing request.
- **FR-056**: The system MUST allow one AUTHORISER approval to be sufficient for a valid outgoing Business request to complete.
- **FR-057**: The system MUST allow an active AUTHORISER to promote an active MEMBER to AUTHORISER.
- **FR-058**: The system MUST reject demotion of an AUTHORISER to MEMBER in the MVP.
- **FR-059**: The system MUST allow an active AUTHORISER to deactivate an active MEMBER.
- **FR-060**: The system MUST allow an active AUTHORISER to deactivate another AUTHORISER only when at least one other active AUTHORISER remains afterward.
- **FR-061**: The system MUST reject deactivation of the final active AUTHORISER.
- **FR-062**: The system MUST immediately deny Business Account access to DEACTIVATED employee logins.
- **FR-063**: The system MUST retain employee access records after deactivation for auditability.
- **FR-064**: The system MUST allow an active AUTHORISER to reactivate a deactivated employee by issuing a new temporary password.
- **FR-065**: Reactivated employee access MUST return to `PASSWORD_CHANGE_REQUIRED`, not directly to ACTIVE.
- **FR-066**: The system MUST NOT support invitations, invitation acceptance, invitation cancellation, or invitation-based Business access in the active MVP behavior.
- **FR-067**: The system MUST resolve Personal Account transfer destinations by unique phone number.
- **FR-068**: The system MUST resolve Business Account transfer destinations by unique UEN.
- **FR-069**: The system MUST require sender selection of destination account type before entering recipient identifier.
- **FR-070**: The system MUST reject unknown Personal phone numbers and unknown Business UENs.
- **FR-071**: The system MUST reject recipient identifier/account-type mismatches.
- **FR-072**: The system MUST reject transfer from an account to itself.
- **FR-073**: The system MUST complete valid Personal outgoing transfers immediately.
- **FR-074**: The system MUST allow incoming Business transfers by UEN without approval.
- **FR-075**: The system MUST require outgoing Business transfers to enter PENDING approval before completion.
- **FR-076**: The system MUST require outgoing Business withdrawals to enter PENDING approval before completion.
- **FR-077**: The system MUST ensure PENDING Business outgoing requests do not reserve funds, change balances, or appear as completed financial transactions.
- **FR-078**: The system MUST display actual Business Account balances without reducing them for PENDING requests.
- **FR-079**: The system MUST allow multiple PENDING outgoing Business requests simultaneously.
- **FR-080**: The system MUST revalidate requested amount, current Business balance, retained minimum, recipient where applicable, access state, and AUTHORISER role when approval is attempted.
- **FR-081**: The system MUST complete a Business outgoing request only when approval-time validation passes and the Business Account retains at least SGD 7,000.00.
- **FR-082**: The system MUST mark a PENDING Business outgoing request as FAILED when approval-time validation fails.
- **FR-083**: The system MUST support outgoing request statuses PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED.
- **FR-084**: The system MUST NOT persist a separate APPROVED status in the MVP.
- **FR-085**: The system MUST allow only PENDING outgoing requests to be approved, rejected, or cancelled.
- **FR-086**: The system MUST treat COMPLETED, REJECTED, CANCELLED, and FAILED outgoing requests as final.
- **FR-087**: Every successful deposit and completed withdrawal MUST create one immutable completed financial transaction record with a UUID transaction ID.
- **FR-088**: Every successfully completed transfer MUST create one shared transfer operation ID.
- **FR-089**: Every successfully completed transfer MUST create one immutable sender debit record and one immutable recipient credit record.
- **FR-090**: Each completed transfer debit and credit record MUST have its own UUID transaction ID.
- **FR-091**: Linked transfer debit and credit records MUST reference the same transfer operation ID.
- **FR-092**: Transaction History MUST contain completed financial movements only.
- **FR-093**: Approval History MUST contain Business outgoing withdrawal and transfer requests with requester employee, requester role, type, amount, destination where applicable, actioning AUTHORISER where applicable, status, dates, and safe outcome reason where applicable.
- **FR-094**: Access Audit History MUST contain Business Account creation, initial AUTHORISER creation, employee access creation, temporary-password issuance, first-login password change or activation, password reset, MEMBER promotion, employee deactivation, employee reactivation, and rejected final-AUTHORISER deactivation attempts where recorded.
- **FR-095**: The system MUST keep Transaction History, Approval History, and Access Audit History logically distinct.
- **FR-096**: The system MUST deny history access when the user does not own the Personal Account, is not an active employee of the Business Account, is in `PASSWORD_CHANGE_REQUIRED` state, or is DEACTIVATED.
- **FR-097**: The system MUST identify all employee-access, password, approval, and financial actions by authenticated individual login, not shared credentials.

### Business Rules

- **BR-001**: All monetary values and balances are SGD only.
- **BR-002**: Monetary operations MUST use precise decimal arithmetic and MUST NOT use floating-point arithmetic.
- **BR-003**: Money inputs MUST reject zero, negative, malformed, non-numeric, non-SGD, over-capacity, and excessive-precision values.
- **BR-004**: Monetary values MUST support no more than two decimal places.
- **BR-005**: Failed, rejected, PENDING, CANCELLED, or FAILED operations MUST NOT create completed financial transaction records.
- **BR-006**: Failed, rejected, PENDING, CANCELLED, or FAILED operations MUST NOT change balances.
- **BR-007**: Personal Logins and Business Employee Access Logins are mutually exclusive access contexts.
- **BR-008**: A Personal Login accesses Personal Account functionality only.
- **BR-009**: A Business Employee Access Login accesses Business Account functionality only.
- **BR-010**: A Business Employee Access Login belongs to exactly one Business Account.
- **BR-011**: Shared Business Account credentials are prohibited.
- **BR-012**: A Personal Account has no opening deposit requirement and no retained minimum.
- **BR-013**: A Personal Account begins at SGD 0.00.
- **BR-014**: A Personal Account MUST NOT become negative.
- **BR-015**: A Personal Account receives transfers by unique phone number.
- **BR-016**: A Business Account is company-owned and is not owned or authorised by a Personal Account.
- **BR-017**: A Business Account receives transfers by unique UEN.
- **BR-018**: A Business Account requires opening deposit of at least SGD 7,000.00.
- **BR-019**: A Business Account creator becomes initial AUTHORISER employee access for that Business Account only.
- **BR-020**: A Business Account MUST always have at least one active AUTHORISER.
- **BR-021**: Employee roles are MEMBER and AUTHORISER only.
- **BR-022**: Employee access states are `PASSWORD_CHANGE_REQUIRED`, `ACTIVE`, and `DEACTIVATED`.
- **BR-023**: Invitations are not part of the active MVP access model.
- **BR-024**: AUTHORISER-only employee access administration MUST be enforced server-side.
- **BR-025**: Temporary passwords are one-time onboarding or reset credentials and MUST be replaced before normal Business Account access.
- **BR-026**: Deactivated employee access immediately revokes Business Account functionality.
- **BR-027**: Demoting AUTHORISER to MEMBER is outside MVP scope and MUST be rejected.
- **BR-028**: Completed outgoing Business withdrawals and transfers MUST leave at least SGD 7,000.00.
- **BR-029**: Business deposits and incoming Business transfers do not require approval.
- **BR-030**: Business outgoing withdrawals and transfers require AUTHORISER approval before completion.
- **BR-031**: One AUTHORISER approval is sufficient.
- **BR-032**: AUTHORISERS MAY approve their own requests.
- **BR-033**: PENDING outgoing requests do not reserve funds or reduce displayed balances.
- **BR-034**: Multiple PENDING outgoing requests are allowed.
- **BR-035**: Each PENDING request is independently revalidated at approval time.
- **BR-036**: There is no separately persisted APPROVED status.
- **BR-037**: Only PENDING requests may transition.
- **BR-038**: COMPLETED, REJECTED, CANCELLED, and FAILED are final statuses.
- **BR-039**: Transfer destination account type and identifier MUST match.
- **BR-040**: Transfers from an account to itself are rejected.
- **BR-041**: Old same-login Personal/Business ownership transfer restrictions MUST NOT be reintroduced.
- **BR-042**: Every completed transfer creates two linked financial transaction records with one shared transfer operation ID.
- **BR-043**: Balance changes and completed financial transaction creation MUST be atomic.
- **BR-044**: Completed financial transaction records MUST NOT be editable or deletable through ordinary user actions.
- **BR-045**: Access audit records are distinct from financial transaction records.
- **BR-046**: Password values, password hashes, and secret credentials MUST NOT appear in Access Audit History.

### Security Requirements

- **SEC-001**: Users MUST authenticate before accessing accounts, histories, money operations, Team Access, password-change, password-reset, deactivation, reactivation, promotion, or approval actions.
- **SEC-002**: Personal Logins MUST be denied Business functionality and Business Employee Access Logins MUST be denied Personal functionality.
- **SEC-003**: Business Employee Access Logins MUST access only their assigned Business Account.
- **SEC-004**: Business Employees in `PASSWORD_CHANGE_REQUIRED` state MUST access only mandatory password-change and sign-out until activated.
- **SEC-005**: DEACTIVATED employee logins MUST NOT access Business functionality or Business data.
- **SEC-006**: Only active AUTHORISERS may create employee access, reset temporary passwords, promote employees, deactivate employees, reactivate employees, approve requests, or reject requests.
- **SEC-007**: The final active AUTHORISER MUST NOT be deactivated.
- **SEC-008**: Passwords, temporary passwords after initial handover, password hashes, and secrets MUST never appear in account pages, histories, employee lists, recipient confirmations, access audit entries, or error outputs.
- **SEC-009**: Safe recipient confirmation MUST NOT expose sensitive email or credential details.
- **SEC-010**: Employee access, access state, role assignment, promotion, deactivation, reactivation, password reset, approval, rejection, cancellation, financial validation, and access control MUST be enforced server-side.
- **SEC-011**: No secrets, Django secret keys, plaintext passwords, temporary passwords, tokens, environment files containing secrets, local database files, or password hashes may be committed to GitHub.
- **SEC-012**: Shared employee credentials are prohibited by the intended workflow.
- **SEC-013**: All important access-management actions MUST be attributable to the authenticated AUTHORISER in Access Audit History.

### UI/UX Requirements

- **UX-001**: The interface MUST deliver a substantially upgraded premium "Midnight Ledger" visual direction: polished, high contrast, corporate banking appropriate, desktop-first, and usable at narrow browser widths.
- **UX-002**: Page layouts MUST use purposeful full-content-area composition with strong hierarchy: title, account context, summary metrics, primary action, and data content.
- **UX-003**: The UI MUST use premium card layouts, polished tables or structured cards, consistent spacing rhythm, readable typography, and clear primary, secondary, and destructive action styling.
- **UX-004**: Public registration MUST present polished choices for Open a Personal Account or Open a Business Account.
- **UX-005**: Personal registration MUST explain individual use, phone-number transfer receipt, no opening deposit, and SGD 0.00 starting balance.
- **UX-006**: Business registration MUST explain company use, UEN transfer receipt, SGD 7,000.00 opening funds, employee access, and approval controls.
- **UX-007**: Personal Login navigation MUST include Dashboard, Personal Account, Deposit, Withdraw, Transfer, Transactions, and Sign Out.
- **UX-008**: Personal users MUST NOT see Business administration, Team Access, Access Audit, or Business approval navigation.
- **UX-009**: Business Employee navigation MUST include Business Dashboard, Deposit, Request Withdrawal, Request Transfer, Approvals, Team Access, Access Audit, Transactions, and Sign Out.
- **UX-010**: Business Employee navigation MUST NOT include Invitations or a Business Account selector.
- **UX-011**: Business Dashboard MUST show business display name, UEN, employee role, employee access state where relevant, current balance, SGD 7,000.00 retained-minimum reminder, available-outgoing-funds indicator where consistent with rules, pending approval count, recent completed transactions, recent approval activity, and Authoriser-only Team Access summary where applicable.
- **UX-012**: Team Access MUST show business display name, UEN, current user's role, active employee count, AUTHORISER count, password-change-required count, deactivated count, and an AUTHORISER-only Add Employee Access action.
- **UX-013**: Team Access MUST display employee display name, login email, role, access status, created date or last security-action timestamp where useful, and permitted AUTHORISER actions: Promote to Authoriser, Reset Temporary Password, Deactivate, and Reactivate.
- **UX-014**: Team Access MUST explain that employee access is individual and auditable, and MUST show clear protection messages when final active AUTHORISER deactivation is blocked.
- **UX-015**: Add Employee Access MUST provide employee display name, login email, role selector, temporary password, confirmation, first-login password-change notice, AUTHORISER-role confirmation step, and success outcome without redisplaying the password after the initial handover moment.
- **UX-016**: First Login Password Change MUST be a branded security checkpoint with new password and confirmation fields, no navigation into Business Account functions until completed, and success redirect to Business Dashboard.
- **UX-017**: Reset Temporary Password MUST be AUTHORISER-only, confirm employee identity, collect temporary password and confirmation, warn that normal activity is blocked until password change, and never display password in employee list or audit log.
- **UX-018**: Deactivation and reactivation flows MUST show confirmation, immediate access-loss warning, heightened AUTHORISER warning, final-AUTHORISER block explanation, and reactivation with new temporary password.
- **UX-019**: Approval screens MUST show balance, retained-minimum summary, projected post-approval balance, requester identity and role, recipient type and safe identifier, financial consequence explanation, and differentiated approve, reject, and cancel actions.
- **UX-020**: Transaction, Approval, and Access Audit history views MUST be clearly labelled as separate views and MUST NOT visually confuse access events or workflow records with completed money movement.
- **UX-021**: Transfer flow MUST require recipient account type, matching identifier, SGD amount, safe recipient confirmation, review, submission, and completed/PENDING/rejected outcome.
- **UX-022**: Forms MUST use visible labels, field-specific validation messages, and clear primary actions.
- **UX-023**: Financial, password-reset, promotion, deactivation, reactivation, and AUTHORISER-level access creation actions MUST show clear review or confirmation.
- **UX-024**: Statuses MUST be communicated with text and not colour alone.
- **UX-025**: The UI MUST provide polished empty, success, error, PENDING, COMPLETED, REJECTED, CANCELLED, FAILED, Password Change Required, Active, and Deactivated states.
- **UX-026**: Monetary values MUST display the SGD marker and exactly two decimal places.
- **UX-027**: Interactive controls MUST support keyboard navigation and visible focus states.
- **UX-028**: Primary pages MUST have strong text/background contrast and avoid ordinary-use horizontal scrolling.
- **UX-029**: Core Business pages MUST avoid large unusable empty layout gaps at standard desktop widths.

### Non-Functional Requirements

- **NFR-001**: The feature MUST remain within the constitutionally approved MVP scope and not introduce unapproved product behavior.
- **NFR-002**: The specification MUST remain technology-agnostic and defer implementation architecture to planning.
- **NFR-003**: Error messages MUST clearly explain what prevented an invalid action without exposing sensitive information.
- **NFR-004**: Financial operation completion MUST be atomic: either all balance and completed-record changes succeed or none occur.
- **NFR-005**: Each business rule MUST remain traceable from constitution to acceptance criteria, plan, tasks, code component, and automated test.
- **NFR-006**: Primary target is a modern desktop browser on macOS, with usable narrower-width behavior.
- **NFR-007**: Business employee access, password, approval, and financial actions MUST be attributable to authenticated individual login identities.
- **NFR-008**: Access changes MUST take effect immediately for authorization decisions.
- **NFR-009**: Employee access records MUST be retained rather than deleted through ordinary MVP user workflows.

### Mandatory Test Requirements

- **TEST-001**: Verify Personal registration creates Personal-only access and one Personal Account.
- **TEST-002**: Verify Business Account registration creates Business Account, initial AUTHORISER employee access, opening-deposit transaction, and initial Access Audit events.
- **TEST-003**: Verify duplicate email rejection across Personal Logins and Business Employee Access Logins.
- **TEST-004**: Verify Personal Login cannot access Business functionality.
- **TEST-005**: Verify Business Employee Access Login cannot access Personal functionality.
- **TEST-006**: Verify separate credentials are required for a person needing both contexts.
- **TEST-007**: Verify Personal Account starts at SGD 0.00 and requires unique phone number.
- **TEST-008**: Verify duplicate Personal phone rejection.
- **TEST-009**: Verify Business Account registration requires display name, unique UEN, and opening deposit of SGD 7,000.00 or more.
- **TEST-010**: Verify Business Account registration rejects missing/duplicate UEN and opening deposit below SGD 7,000.00.
- **TEST-011**: Verify secure password hashing and no password exposure.
- **TEST-012**: Verify no active invitation feature remains in MVP behavior.
- **TEST-013**: Verify AUTHORISER creates MEMBER access with temporary password.
- **TEST-014**: Verify AUTHORISER creates AUTHORISER access with temporary password.
- **TEST-015**: Verify MEMBER cannot create employee access.
- **TEST-016**: Verify duplicate employee email rejection.
- **TEST-017**: Verify new employee begins in `PASSWORD_CHANGE_REQUIRED` state.
- **TEST-018**: Verify employee is forced to change temporary password before normal Business access.
- **TEST-019**: Verify temporary password change activates normal access.
- **TEST-020**: Verify password values are not exposed or retrievable.
- **TEST-021**: Verify AUTHORISER resets MEMBER password and returns access to `PASSWORD_CHANGE_REQUIRED`.
- **TEST-022**: Verify AUTHORISER resets another AUTHORISER password and returns access to `PASSWORD_CHANGE_REQUIRED`.
- **TEST-023**: Verify MEMBER cannot reset passwords.
- **TEST-024**: Verify previous password no longer works after administrative temporary-password reset.
- **TEST-025**: Verify MEMBER permissions.
- **TEST-026**: Verify AUTHORISER permissions.
- **TEST-027**: Verify AUTHORISER may promote MEMBER to AUTHORISER.
- **TEST-028**: Verify AUTHORISER-to-MEMBER demotion is rejected.
- **TEST-029**: Verify AUTHORISER may deactivate MEMBER.
- **TEST-030**: Verify AUTHORISER may deactivate another AUTHORISER only when another active AUTHORISER remains.
- **TEST-031**: Verify final active AUTHORISER deactivation is rejected.
- **TEST-032**: Verify deactivated employee immediately loses Business access.
- **TEST-033**: Verify reactivation requires a new temporary password and returns access to `PASSWORD_CHANGE_REQUIRED`.
- **TEST-034**: Verify Business Employee Access Login belongs to exactly one Business Account.
- **TEST-035**: Verify no multi-Business Account selector appears for employee logins.
- **TEST-036**: Verify successful positive deposits for Personal and Business Accounts.
- **TEST-037**: Verify active MEMBER and AUTHORISER may deposit into Business Account without approval.
- **TEST-038**: Verify rejection of zero, negative, malformed, non-numeric, non-SGD, over-capacity, and excessive-precision money inputs.
- **TEST-039**: Verify successful Personal withdrawal and full-balance withdrawal to SGD 0.00.
- **TEST-040**: Verify Personal withdrawal that would make balance negative is rejected.
- **TEST-041**: Verify successful Personal outgoing transfer and full-balance transfer to SGD 0.00.
- **TEST-042**: Verify Personal outgoing transfer that would make balance negative is rejected.
- **TEST-043**: Verify Personal recipient lookup by phone number.
- **TEST-044**: Verify Business recipient lookup by UEN.
- **TEST-045**: Verify unknown phone, unknown UEN, identifier mismatch, and self-transfer rejection.
- **TEST-046**: Verify completed transfer creates one operation ID and two linked UUID transaction records.
- **TEST-047**: Verify MEMBER may submit withdrawal and transfer requests.
- **TEST-048**: Verify AUTHORISER may submit withdrawal and transfer requests.
- **TEST-049**: Verify PENDING requests do not move funds, reserve funds, or create completed financial records.
- **TEST-050**: Verify MEMBER cannot approve, reject, reset passwords, promote, deactivate, reactivate, or cancel another employee's request.
- **TEST-051**: Verify AUTHORISER may approve any PENDING request and one approval is sufficient.
- **TEST-052**: Verify AUTHORISER may approve their own PENDING request.
- **TEST-053**: Verify AUTHORISER may reject any PENDING request.
- **TEST-054**: Verify MEMBER may cancel own PENDING request only.
- **TEST-055**: Verify AUTHORISER may cancel any PENDING request.
- **TEST-056**: Verify no persisted APPROVED status exists.
- **TEST-057**: Verify terminal statuses cannot be actioned again.
- **TEST-058**: Verify multiple PENDING requests may coexist and are independently revalidated.
- **TEST-059**: Verify successful Business outgoing completion may leave exactly SGD 7,000.00.
- **TEST-060**: Verify Business outgoing approval fails at SGD 6,999.99 with FAILED status, no money movement, and no completed financial records.
- **TEST-061**: Verify Access Audit History records account creation, initial AUTHORISER creation, employee access creation, temporary-password issuance, password activation, password reset, promotion, deactivation, reactivation, and rejected final-AUTHORISER deactivation where recorded.
- **TEST-062**: Verify Access Audit History never exposes password values or password hashes.
- **TEST-063**: Verify Transaction History contains completed financial movements only.
- **TEST-064**: Verify Approval History contains Business outgoing request workflow records only.
- **TEST-065**: Verify Access Audit History is separate from Transaction History and Approval History.
- **TEST-066**: Verify unauthorised account, history, employee access, approval, and financial operation access is denied.
- **TEST-067**: Verify deactivated employee is denied all histories.
- **TEST-068**: Verify Midnight Ledger registration choice, Personal navigation, Business navigation, Team Access, role-aware controls, labelled forms, confirmations, accessibility, no Business Account selector, no Invitations navigation, and narrow-width usability.
- **TEST-069**: Verify core Business pages avoid large unusable empty layout gaps at standard desktop widths.

### Key Entities *(include if feature involves data)*

- **Personal Login**: A registered identity with Personal Account access only, unique email, display name or username, and securely hashed password.
- **Business Employee Access Login**: A registered employee credential with unique email, display name, securely hashed password, role, access state, and scope to exactly one Business Account.
- **Personal Account**: An SGD account created during Personal registration with no opening deposit, no minimum balance, and one unique phone number for receiving transfers.
- **Business Account**: A company-owned SGD account created during Business Account registration with business display name, unique UEN, opening deposit of at least SGD 7,000.00, and at least one active AUTHORISER employee access login.
- **Employee Access Record**: The auditable relationship between one Business Employee Access Login and exactly one Business Account, including MEMBER or AUTHORISER role, access state, creation timestamp, deactivation/reactivation timestamps where applicable, and security-action metadata.
- **Access Audit Event**: An audit record for Business Account access-security and employee-administration activity.
- **Money Operation**: A requested deposit, withdrawal, or transfer with an SGD amount, validation outcome, and account/role-specific completion rules.
- **Business Outgoing Request**: A workflow record for an outgoing Business withdrawal or transfer with status PENDING, COMPLETED, REJECTED, CANCELLED, or FAILED.
- **Completed Financial Transaction Record**: An immutable audit record for a completed deposit, withdrawal, transfer debit, transfer credit, or Business opening deposit.
- **Transfer Operation**: The shared identity of a completed transfer that links one sender debit record and one recipient credit record.
- **Transaction History**: The view of completed financial movement records only.
- **Approval History**: The view of Business outgoing workflow requests and outcomes.
- **Access Audit History**: The view of Business access-security and employee-administration events.
- **Invitation**: Superseded v2.0.0 concept. Invitations are not active MVP behavior under constitution v3.0.0 and must be removed or refactored later.

### Banking Rule Coverage *(mandatory for banking features)*

- **Technology Scope**: The feature remains a specification of the constitutionally approved MVP only; planning must stay within the approved local stack and must not add alternative databases, frontend frameworks, external CSS frameworks, payment gateways, external bank integrations, cloud infrastructure, microservices, message queues, third-party authentication, OTP verification, email delivery, or external UEN verification.
- **MVP Scope**: The feature is limited to Personal and Business registration, authentication, Personal Accounts, Business Accounts, provisioned Business Employee Access Logins, role management, password-change and reset workflows, deactivation/reactivation, deposits, withdrawals, transfers, Transaction History, Approval History, Access Audit History, premium UI/UX, tests, traceability, and local deployment readiness.
- **Personal Account Rules**: FR-011 through FR-020 and BR-012 through BR-015 define Personal Account creation, phone recipient identity, no opening deposit, no retained minimum, and no negative balance.
- **Business Account and Employee Access Rules**: FR-021 through FR-066 and BR-016 through BR-027 define Business Account creation, UEN identity, initial AUTHORISER, one-account employee scope, roles, temporary password, access states, password reset, promotion, deactivation, reactivation, and no invitation model.
- **Financial Rules**: FR-016 through FR-020, FR-049 through FR-056, FR-073 through FR-091, and BR-001 through BR-006, BR-028 through BR-043 define money validation, deposits, withdrawals, transfers, retained minimum, approval, atomicity, UUID records, and no completed records on failed paths.
- **Recipient Identity**: FR-067 through FR-072 and BR-039 through BR-041 define Personal phone lookup, Business UEN lookup, mismatched identifier rejection, unknown identifier rejection, self-transfer rejection, and no same-login ownership transfer rule.
- **Business Approval**: FR-075 through FR-086 and BR-030 through BR-038 define PENDING requests, AUTHORISER approval, one-approval threshold, self-approval, cancellation, rejection, FAILED, multiple PENDING requests, and no APPROVED status.
- **Histories and Auditability**: FR-092 through FR-097 and BR-044 through BR-046 define Transaction History, Approval History, Access Audit History, authenticated attribution, password secrecy, and no shared credentials.
- **Security**: SEC-001 through SEC-013 define authentication, context separation, assigned-account access, password-change-required gating, deactivated access loss, authoriser-only actions, final-AUTHORISER protection, password safety, safe recipient confirmation, server-side enforcement, and secret management.
- **UI/UX and Accessibility**: UX-001 through UX-029 and NFR-006 through NFR-009 define Midnight Ledger registration choice, context-specific navigation, no Invitations navigation, no Business Account selector, Team Access, approval screens, histories, states, accessibility, and responsive behavior.
- **Mandatory Tests**: TEST-001 through TEST-069 provide the required traceable test inventory.

### Traceability Matrix *(mandatory)*

| Rule ID | Requirement ID | Acceptance Criteria | Plan Reference | Task ID | Code Component | Test ID / Path |
|---------|----------------|---------------------|----------------|---------|----------------|----------------|
| BR-007 to BR-011 | FR-001 to FR-010, FR-032 to FR-034 | User Story 1 and employee-scope scenarios | Pending v3.0.0 plan regeneration | Pending | Pending | TEST-001 to TEST-006, TEST-034 to TEST-035 |
| BR-012 to BR-015 | FR-011 to FR-020 | User Story 2 Personal Account scenarios | Pending v3.0.0 plan regeneration | Pending | Pending | TEST-007 to TEST-008, TEST-036, TEST-039 to TEST-042 |
| BR-016 to BR-027 | FR-021 to FR-066 | User Story 3 and 4 Business creation, employee access, password, promotion, deactivation, reactivation scenarios | Pending v3.0.0 plan regeneration | Pending | Pending | TEST-009 to TEST-035, TEST-061 to TEST-062 |
| BR-001 to BR-006, BR-028 to BR-038 | FR-049 to FR-056, FR-075 to FR-086 | Business deposit, request, approval, retained-minimum, no-reservation, and failed approval scenarios | Pending v3.0.0 plan regeneration | Pending | Pending | TEST-036 to TEST-038, TEST-047 to TEST-060 |
| BR-039 to BR-043 | FR-067 to FR-091 | Transfer recipient, self-transfer, linked records, UUID, and atomicity scenarios | Pending v3.0.0 plan regeneration | Pending | Pending | TEST-043 to TEST-046 |
| BR-044 to BR-046 | FR-092 to FR-097 | Transaction, Approval, Access Audit, password secrecy, and authenticated attribution scenarios | Pending v3.0.0 plan regeneration | Pending | Pending | TEST-061 to TEST-067 |
| SEC-001 to SEC-013 | FR-006 to FR-010, FR-036 to FR-066, FR-096 to FR-097 | Access denial, password gating, deactivation, final-AUTHORISER, and safe-output scenarios | Pending v3.0.0 plan regeneration | Pending | Pending | TEST-004 to TEST-006, TEST-015, TEST-018 to TEST-024, TEST-031 to TEST-033, TEST-050, TEST-066 to TEST-067 |
| UX-001 to UX-029 | User Stories 7 and 8 | Registration choice, Personal nav, Business nav, no selector, Team Access, role-aware controls, approval, histories, and responsive scenarios | Pending v3.0.0 plan regeneration | Pending | Pending | TEST-068 to TEST-069 |
| NFR-001 to NFR-009 | All BR, FR, SEC, UX, and TEST identifiers | Scope, atomicity, traceability, attribution, immediate access effect, and retained audit records | Pending v3.0.0 plan regeneration | Pending | Pending | TEST-001 to TEST-069 |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successful Personal registrations create Personal-only access, one Personal Account, unique phone recipient identifier, and starting balance SGD 0.00.
- **SC-002**: 100% of successful Business Account registrations create one Business Account, unique UEN, opening deposit transaction, active initial AUTHORISER employee access scoped to that account only, and initial Access Audit events.
- **SC-003**: 100% of duplicate email, duplicate Personal phone, duplicate Business UEN, missing UEN, invalid opening deposit, and insufficient Business opening deposit attempts are rejected with no partial account or employee-access creation.
- **SC-004**: 100% of Personal Login attempts to access Business functionality are denied.
- **SC-005**: 100% of Business Employee Access Login attempts to access Personal functionality are denied.
- **SC-006**: 100% of Business Employee Access Logins are scoped to exactly one Business Account.
- **SC-007**: 0 active MVP user journeys require invitation issuance, invitation acceptance, or Business Account switching by one employee login.
- **SC-008**: 100% of newly provisioned employee logins require password change before normal Business Account access.
- **SC-009**: 100% of administrative temporary-password resets return employee access to `PASSWORD_CHANGE_REQUIRED`.
- **SC-010**: 100% of password-related audit entries and ordinary views omit password values and password hashes.
- **SC-011**: 100% of Business Accounts have at least one active AUTHORISER after every employee-access administration action.
- **SC-012**: 100% of deactivated Business Employees lose Business Account functionality and history access immediately.
- **SC-013**: 100% of MEMBER attempts to perform AUTHORISER-only actions are denied.
- **SC-014**: 100% of completed Business outgoing withdrawals and transfers leave the Business Account with at least SGD 7,000.00.
- **SC-015**: 100% of PENDING Business outgoing requests leave displayed balances unchanged and reserve no funds.
- **SC-016**: If multiple PENDING Business requests exist, each approval attempt is independently revalidated and may become FAILED if current rules no longer pass.
- **SC-017**: 100% of successful deposits and completed withdrawals are visible in Transaction History with amount in SGD, status, type, timestamp, account, and UUID transaction ID.
- **SC-018**: 100% of successful transfers show one sender debit record and one recipient credit record, each with its own UUID transaction ID and the same transfer operation ID.
- **SC-019**: 100% of failed, rejected, PENDING, CANCELLED, or FAILED operations leave balances unchanged and create no completed financial transaction records.
- **SC-020**: Users can distinguish Transaction History, Approval History, and Access Audit History.
- **SC-021**: 100% of Personal recipient transfers require Personal Account destination plus phone number, and 100% of Business recipient transfers require Business Account destination plus UEN.
- **SC-022**: 100% of mismatched recipient account type and identifier combinations are rejected before money moves.
- **SC-023**: 100% of monetary values displayed in primary account, transfer, approval, and transaction views include the SGD marker and exactly two decimal places.
- **SC-024**: Primary registration, sign-in, password change, dashboard, transfer, approval, Team Access, and history flows are usable with keyboard navigation and visible focus states.
- **SC-025**: Dashboard cards, Team Access records, transfer forms, approval requests, and histories remain readable at narrow browser widths without ordinary-use horizontal scrolling.
- **SC-026**: Business Dashboard, Team Access, Approvals, Transactions, and Access Audit pages avoid large unusable empty layout gaps at standard desktop widths.
- **SC-027**: Every core business rule in this specification has at least one acceptance scenario and at least one `TEST-###` identifier for later automated testing.
- **SC-028**: Any implementation based on constitution v2.0.0 invitations or multi-Business memberships is identified as superseded before v3.0.0 planning and tasks proceed.

## Assumptions

- A login identity has exactly one access context: Personal Login or Business Employee Access Login.
- Personal Account registration creates the Personal Account immediately.
- Business Account registration creates the Business Account and active initial AUTHORISER employee access immediately when all validation passes.
- A Business Employee Access Login belongs to exactly one Business Account and never uses a Business Account selector.
- The MVP supports Authoriser-provisioned employee access credentials and does not support invitations.
- Temporary passwords are created by AUTHORISERS for local MVP handoff but are not retrievable after provisioning or reset.
- The MVP does not support AUTHORISER demotion to MEMBER.
- The MVP does not support permanent deletion of employee access through ordinary user flows.
- The MVP does not support ordinary self-service password reset outside the mandatory first-login password-change and AUTHORISER-issued temporary-password reset flows.
- The MVP does not support shared company credentials.
- Date/time display must be understandable to users and consistent within histories, while exact formatting belongs to later design work.
- Existing implementation and planning artifacts based on v2.0.0 invitations, multi-Business memberships, or Business Account selector logic require later refactoring and regeneration.
- This specification intentionally avoids implementation decisions, including database tables, models, URLs, form classes, templates, middleware, modules, test framework, server configuration, deployment details, UI libraries, CSS frameworks, and JavaScript frameworks.

## Implementation Impact Note

Any current constitution v2.0.0 implementation is superseded where it includes invitation records, invitation pages, invitation acceptance, invitation tests, multi-Business membership support, Business Account selector logic, or wording requiring employees to register or accept invitations.

These areas MUST be replaced later through a revised `/speckit.plan`, regenerated `/speckit.tasks`, and new `/speckit.analyze` review before implementation resumes. This clarification step does not implement code and does not patch Django models, forms, views, templates, CSS, migrations, services, or tests.

## Required Next Validation

This specification has been clarified for constitution v3.0.0. No genuine product ambiguity remains from the provided amendment text. Run `/speckit.checklist` against this v3.0.0 specification before regenerating `/speckit.plan`.
