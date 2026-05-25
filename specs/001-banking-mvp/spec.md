# Feature Specification: Banking MVP

**Feature Branch**: `001-banking-mvp`

**Created**: 2026-05-25

**Status**: Draft

**Input**: User description: "Build the MVP for a personal and business banking application that allows users to securely manage SGD accounts, deposit and withdraw funds, transfer money using phone numbers and UENs, and view an auditable transaction history."

## Clarifications

### Session 2026-05-25

- Q: What is the MVP relationship between a user, Personal Account, Business Account, and Business Account activation? -> A: A user must have an active own Personal Account before creating a Business Account; that Personal Account is the sole authorised approver; Business Account creation is rejected unless the opening deposit is at least SGD 7,000.00.
- Q: How do Business Account outgoing approval, revalidation, and lifecycle work? -> A: Submission creates only a PENDING request with no fund reservation; approval revalidates amount, current balance, retained minimum, and authorised identity; PENDING may become COMPLETED, REJECTED, CANCELLED, or FAILED, and final states cannot be acted on again.
- Q: How are Transaction History and Approval History separated? -> A: Transaction History shows completed financial records only; Approval History shows Business Account outgoing requests, with completed business outgoing operations appearing in both histories.
- Q: How are transfer recipients identified after constitution v1.1.0? -> A: Transfers to Personal Accounts use the recipient Personal Account phone number; transfers to Business Accounts use the recipient Business Account UEN; the sender must choose recipient account type before entering the matching identifier.
- Q: What transfer and monetary edge rules are final? -> A: Safe recipient confirmation is required; self-transfers and same-user Personal/Business transfers are rejected; SGD amounts use at most two decimal places and reject zero, negative, text, malformed, non-numeric, and excessive-precision values.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register and Access Own Accounts (Priority: P1)

An Account Holder registers with username, unique email address, password, and
then creates account-specific recipient identifiers through Personal Account and
Business Account setup. The signed-in user accesses only their own accounts,
balances, transactions, and assigned approval requests.

**Why this priority**: Registration, authentication, and account isolation are
required before any financial workflow can be trusted.

**Independent Test**: A new user can register, sign in, view their own
information, and is denied access to another user's account or history.

**Acceptance Scenarios**:

1. **Given** no registered user has email `a@example.test`, **When** a user registers with username, email, and password, **Then** the user is registered and the password is not displayed back.
2. **Given** an existing user has email `a@example.test`, **When** another user registers with that email, **Then** registration is rejected and no duplicate user is created.
3. **Given** a registered user enters correct credentials, **When** they sign in, **Then** they reach their authenticated dashboard.
4. **Given** a registered user enters incorrect credentials, **When** they attempt sign-in, **Then** sign-in is rejected without exposing which credential was wrong.
5. **Given** User A is signed in, **When** User A attempts to access User B's account, Transaction History, or Approval History, **Then** access is denied.

---

### User Story 2 - Open and Use a Personal Account (Priority: P1)

An Account Holder opens a Personal Account with one unique phone number used to
receive transfers, no opening deposit, and balance SGD 0.00. The holder deposits
funds, withdraws funds when available, transfers funds to other accounts, and
views completed transactions.

**Why this priority**: Personal Account behavior proves the core money,
validation, phone-recipient, transfer, and audit rules.

**Independent Test**: A Personal Account can be opened with a unique receiving
phone number, complete valid deposits, withdrawals, and outgoing transfers, and
reject invalid or negative-balance outcomes.

**Acceptance Scenarios**:

1. **Given** a signed-in user without a Personal Account and no Personal Account has phone `91234567`, **When** they open a Personal Account with phone `91234567`, **Then** it is active with balance SGD 0.00 and that phone number is its transfer recipient identifier.
2. **Given** another Personal Account already uses phone `91234567`, **When** a user attempts to open or update a Personal Account with `91234567`, **Then** the request is rejected.
3. **Given** a Personal Account with balance SGD 0.00, **When** SGD 100.00 is deposited, **Then** the balance becomes SGD 100.00 and one completed deposit transaction is recorded.
4. **Given** a Personal Account with balance SGD 100.00, **When** SGD 40.00 is withdrawn, **Then** the balance becomes SGD 60.00 and one completed withdrawal transaction is recorded.
5. **Given** a Personal Account with balance SGD 30.00, **When** SGD 40.00 is requested for withdrawal, **Then** the withdrawal is rejected, balance remains SGD 30.00, and no completed withdrawal transaction is recorded.
6. **Given** a Personal Account with balance SGD 100.00 and another user's Personal Account phone number, **When** SGD 25.00 is transferred to that Personal Account, **Then** sender and recipient balances update together and linked completed transfer records are created.
7. **Given** a Personal Account with balance SGD 20.00, **When** SGD 25.00 is requested for transfer, **Then** the transfer is rejected, no balances change, and no completed transfer records are created.

---

### User Story 3 - Open and Use a Business Account (Priority: P1)

An Account Holder with an active Personal Account opens one Business Account by
providing business display name, unique UEN, and opening deposit of at least SGD
7,000.00. The user's own Personal Account becomes the sole authorised approver.
Inbound money completes immediately; outgoing withdrawals and transfers require
approval.

**Why this priority**: Business Account activation, UEN identity, approval, and
retained minimum-balance rules are the MVP's key governance distinction.

**Independent Test**: A Business Account can be created only when the signed-in
user already has an active Personal Account, supplies a unique UEN, supplies a
business display name, and supplies the required opening deposit.

**Acceptance Scenarios**:

1. **Given** a signed-in user has an active Personal Account and no Business Account uses UEN `202612345A`, **When** they open a Business Account with business display name, UEN `202612345A`, and exactly SGD 7,000.00, **Then** the Business Account is active and the user's Personal Account is the sole authorised approver.
2. **Given** a signed-in user has an active Personal Account, **When** they open a Business Account with more than SGD 7,000.00 and a unique UEN, **Then** the Business Account is active with the deposited balance.
3. **Given** a signed-in user has no active Personal Account, **When** they attempt to open a Business Account, **Then** creation is rejected.
4. **Given** a signed-in user has an active Personal Account, **When** they attempt to open a Business Account without a UEN, **Then** creation is rejected.
5. **Given** another Business Account already uses UEN `202612345A`, **When** the user attempts to open a Business Account with that UEN, **Then** creation is rejected.
6. **Given** a signed-in user has an active Personal Account, **When** they attempt to open a Business Account with less than SGD 7,000.00, **Then** creation is rejected and no inactive Business Account is saved.
7. **Given** a Business Account already has the user's Personal Account as authorised approver, **When** another Personal Account is selected or added, **Then** the change is rejected.
8. **Given** an active Business Account, **When** SGD 500.00 is deposited, **Then** the deposit completes without approval.
9. **Given** an active Business Account, **When** it receives an incoming transfer by UEN, **Then** the incoming transfer completes without approval.
10. **Given** an active Business Account, **When** the owner submits an outgoing withdrawal or transfer, **Then** a PENDING approval request is created, no funds are reserved, and the displayed balance remains unchanged.

---

### User Story 4 - Transfer Money Safely (Priority: P1)

An Account Holder sends SGD transfers by selecting a source account, selecting
recipient account type, entering the matching recipient identifier, reviewing
safe recipient confirmation, and receiving a completed, PENDING, or rejected
outcome.

**Why this priority**: Account-type-specific recipient identification prevents
misdirected money and resolves Personal phone versus Business UEN ambiguity.

**Independent Test**: The transfer flow adapts the identifier field to recipient
type, confirms safe recipient details before submission, rejects mismatched
identifiers, and creates linked records only after completion.

**Acceptance Scenarios**:

1. **Given** the sender selects Personal Account recipient, **When** they enter a known Personal Account phone number, **Then** safe recipient confirmation shows username, Personal Account type, partially masked phone number where appropriate, amount, and whether source-account approval is required.
2. **Given** the sender selects Business Account recipient, **When** they enter a known Business Account UEN, **Then** safe recipient confirmation shows business display name, Business Account type, masked or appropriately presented UEN, amount, and whether source-account approval is required.
3. **Given** a Personal Account sender has sufficient balance, **When** they confirm a transfer to another user's Personal Account by phone number, **Then** the transfer completes immediately and shows the transfer operation ID plus sender debit transaction ID.
4. **Given** a Personal Account sender has sufficient balance, **When** they confirm a transfer to another user's Business Account by UEN, **Then** the transfer completes without Business Account approval because funds are incoming to the Business Account.
5. **Given** a Business Account sender submits a transfer to a Personal Account or Business Account, **When** the request is submitted, **Then** it becomes PENDING approval and no balances change.
6. **Given** a PENDING Business Account transfer, **When** the authorised Personal Account approves and the retained minimum remains satisfied, **Then** the transfer becomes COMPLETED with one operation ID and linked debit and credit records.
7. **Given** the sender selects Personal Account recipient, **When** they enter a UEN, **Then** the transfer is rejected because recipient type and identifier do not match.
8. **Given** the sender selects Business Account recipient, **When** they enter a phone number, **Then** the transfer is rejected because recipient type and identifier do not match.
9. **Given** the sender selects Personal Account recipient and enters an unknown phone number, **When** they attempt transfer, **Then** the transfer is rejected with no balance or completed transaction changes.
10. **Given** the sender selects Business Account recipient and enters an unknown UEN, **When** they attempt transfer, **Then** the transfer is rejected with no balance or completed transaction changes.
11. **Given** a sender attempts a self-transfer or transfer between their own Personal Account and Business Account, **When** they attempt transfer, **Then** the transfer is rejected for the MVP.
12. **Given** a transfer fails validation or approval, **When** the user views histories, **Then** no completed debit or credit transaction appears.

---

### User Story 5 - Review Business Approvals (Priority: P1)

An Authorised Personal Account Holder reviews Business Account outgoing
withdrawal and transfer requests, sees projected balances, and approves or
rejects only PENDING requests. The Business Account owner may cancel PENDING
requests.

**Why this priority**: The Business Account approval workflow protects outgoing
business funds and must be easy to audit.

**Independent Test**: Multiple PENDING requests can exist without reserving
funds, only the sole authorised Personal Account can approve or reject them, and
each approval attempt revalidates current balance and retained minimum.

**Acceptance Scenarios**:

1. **Given** a PENDING Business Account withdrawal, **When** the authorised Personal Account views details, **Then** the request shows type, amount in SGD, requested date/time, current Business Account balance, projected balance, and whether SGD 7,000.00 will remain.
2. **Given** a PENDING request and all rules still pass, **When** the authorised Personal Account approves it, **Then** the request changes directly from PENDING to COMPLETED and the financial operation completes.
3. **Given** a PENDING request, **When** the authorised Personal Account rejects it, **Then** the request becomes REJECTED and no balances change.
4. **Given** a PENDING request, **When** the Business Account owner cancels it before completion, **Then** the request becomes CANCELLED and no balances change.
5. **Given** a PENDING request, **When** a non-authorised Personal Account attempts approval or rejection, **Then** the action is denied and the request remains PENDING.
6. **Given** a request is COMPLETED, REJECTED, CANCELLED, or FAILED, **When** any user attempts to approve, reject, or cancel it again, **Then** the action is rejected.
7. **Given** a PENDING request, **When** approval is attempted but requested amount, current balance, retained minimum, or authorised identity validation fails, **Then** the request becomes FAILED and no funds move.
8. **Given** a Business Account has balance SGD 8,500.00, **When** two outgoing withdrawal requests for SGD 1,000.00 are submitted, **Then** two PENDING requests exist and the displayed Business Account balance remains SGD 8,500.00.
9. **Given** those two PENDING requests exist, **When** the authorised Personal Account approves the first request, **Then** it becomes COMPLETED and the Business Account balance becomes SGD 7,500.00.
10. **Given** the second request remains PENDING, **When** approval is attempted and completion would leave less than SGD 7,000.00, **Then** it becomes FAILED, no additional money moves, Approval History shows one COMPLETED and one FAILED request, and Transaction History shows only the completed money movement.

---

### User Story 6 - Navigate the Midnight Ledger Interface (Priority: P2)

An authenticated user gets the premium "Midnight Ledger" banking experience with
clear navigation, account-type-specific recipient identifiers, polished empty
states, and safe confirmation flows for financial actions.

**Why this priority**: The MVP must feel like a credible banking product rather
than a basic training project.

**Independent Test**: A user can navigate Dashboard, Personal Account, Business
Account, Transfer, Approvals, and Transactions, complete primary flows with
visible labels and confirmations, and understand phone/UEN recipient identity.

**Acceptance Scenarios**:

1. **Given** a signed-in user is on desktop width, **When** the app loads, **Then** it shows a compact left navigation sidebar, a top bar with username and sign-out, and destinations for Dashboard, Personal Account, Business Account, Transfer, Approvals, and Transactions.
2. **Given** a user has no Business Account, **When** they open Business Account, **Then** a polished empty state explains the Personal Account prerequisite, business display name, UEN, opening deposit, and retained minimum requirements.
3. **Given** a user views Dashboard, **When** accounts exist, **Then** Personal and Business balance cards are visually distinguishable, balances are formatted in SGD with two decimal places, the Personal card shows receiving phone number, and the Business card shows receiving UEN.
4. **Given** a Business Account has PENDING outgoing requests, **When** Dashboard or Business Account is viewed, **Then** a pending-approvals indicator is noticeable without appearing alarming and the displayed balance is not reduced by PENDING requests.
5. **Given** a financial action is final or destructive, **When** the user proceeds, **Then** a review or confirmation step appears before completion or submission.
6. **Given** the browser width is narrow, **When** the user navigates the app, **Then** navigation adapts to a compact layout and primary content remains readable without horizontal scrolling for normal use.

---

### User Story 7 - View Transaction and Approval History (Priority: P2)

An Account Holder views completed financial movements in Transaction History and
Business Account outgoing workflow records in Approval History, with clear
distinctions between credits, debits, completed movements, and non-completed
requests.

**Why this priority**: Users need trust-building auditability without confusing
PENDING or failed requests with completed money movement.

**Independent Test**: Completed transactions are visible only in Transaction
History, approval workflow records are visible in Approval History, and a
COMPLETED Business outgoing operation appears in both places with different
purposes.

**Acceptance Scenarios**:

1. **Given** a Personal Account has completed deposits, withdrawals, and transfers, **When** the holder views Transaction History, **Then** each row or card shows type, amount in SGD, date/time, status, account, and UUID transaction ID.
2. **Given** a completed transfer to a Business Account using UEN exists, **When** sender or recipient views Transaction History, **Then** the record shows its own UUID transaction ID and the shared transfer operation ID.
3. **Given** PENDING, REJECTED, CANCELLED, or FAILED Business approval requests exist, **When** the user views Transaction History, **Then** those requests are not displayed as completed financial movements.
4. **Given** a COMPLETED Business withdrawal or outgoing transfer exists, **When** the user views histories, **Then** Transaction History shows the completed movement of funds and Approval History shows the COMPLETED approval outcome.
5. **Given** a user has no completed transaction history, **When** they open Transactions, **Then** a polished empty state explains that completed activity will appear there.
6. **Given** User A is signed in, **When** User A attempts to view User B's history, **Then** access is denied.

### Edge Cases

- Duplicate email during registration.
- Duplicate Personal Account phone number during Personal Account setup.
- Missing, duplicate, or already registered Business Account UEN during Business Account setup.
- Sign-in with incorrect credentials.
- Unauthenticated account, money-operation, history, or approval access.
- Access attempts against accounts or approval requests not owned or assigned to the signed-in user.
- Personal Account missing when Business Account creation is attempted.
- Business Account opening deposit below SGD 7,000.00.
- Attempt to authorise another user's Personal Account for a Business Account.
- Attempt to link more than one authorised Personal Account to a Business Account.
- Zero, negative, malformed, non-numeric, non-SGD, or invalid-precision monetary inputs.
- Amounts with more than two decimal places.
- Personal Account withdrawal or transfer exceeding available balance.
- Business Account outgoing withdrawal or transfer attempted without approval.
- Business Account outgoing withdrawal or transfer that would leave less than SGD 7,000.00.
- Multiple PENDING Business Account outgoing requests with no fund reservation.
- PENDING Business Account request failing approval because another request completed first.
- Approval attempted by a non-authorised Personal Account.
- Attempt to act on COMPLETED, REJECTED, CANCELLED, or FAILED approval requests.
- Personal Account transfer to an unknown phone number.
- Business Account transfer to an unknown UEN.
- Recipient account type and identifier mismatch.
- Self-transfer attempt.
- Transfer between the user's own Personal Account and Business Account.
- Failed, rejected, cancelled, or PENDING operation creating completed transaction records or changing balances.
- Attempt to edit or delete completed financial transaction records through ordinary user actions.
- Password exposure in pages, histories, recipient confirmation, or errors.
- Narrow browser width that would otherwise force horizontal scrolling.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow a user to register with username, unique email address, and password.
- **FR-002**: The system MUST reject registration when the email address is already registered.
- **FR-003**: The system MUST allow registered users to sign in and sign out.
- **FR-004**: The system MUST reject sign-in attempts with incorrect credentials without exposing which credential was incorrect.
- **FR-005**: The system MUST allow a signed-in user to view only accounts they own and Business Account approval requests assigned to their own authorised Personal Account.
- **FR-006**: The system MUST support exactly two account types: Personal Account and Business Account.
- **FR-007**: The system MUST allow a user to hold one Personal Account and one Business Account.
- **FR-008**: The system MUST allow a Personal Account to be opened without an opening deposit and with an initial balance of SGD 0.00.
- **FR-009**: The system MUST require each Personal Account to have one unique phone number used as its transfer recipient identifier.
- **FR-010**: The system MUST reject duplicate Personal Account phone numbers.
- **FR-011**: The system MUST allow Personal Account deposits of valid positive SGD amounts.
- **FR-012**: The system MUST allow Personal Account withdrawals of valid positive SGD amounts when the balance will not become negative.
- **FR-013**: The system MUST reject Personal Account withdrawals that would make the balance negative.
- **FR-014**: The system MUST allow Personal Account transfers of valid positive SGD amounts when the sender balance will not become negative.
- **FR-015**: The system MUST reject Personal Account transfers that would make the sender balance negative.
- **FR-016**: The system MUST require the signed-in user to have an active Personal Account before creating a Business Account.
- **FR-017**: The system MUST require a Business Account business display name before creation.
- **FR-018**: The system MUST require each Business Account to have one unique company UEN used as its transfer recipient identifier.
- **FR-019**: The system MUST reject Business Account creation when the UEN is missing.
- **FR-020**: The system MUST reject Business Account creation when the UEN is already registered to another Business Account.
- **FR-021**: The system MUST require a Business Account opening deposit of at least SGD 7,000.00 before creation.
- **FR-022**: The system MUST reject Business Account creation when the opening deposit is below SGD 7,000.00.
- **FR-023**: The system MUST reject Business Account creation when the signed-in user does not have an active Personal Account.
- **FR-024**: The system MUST make the signed-in user's own Personal Account the sole authorised approver for their Business Account.
- **FR-025**: The system MUST reject attempts to authorise another user's Personal Account for a Business Account.
- **FR-026**: The system MUST prevent more than one authorised Personal Account from being linked to a Business Account.
- **FR-027**: The system MUST allow deposits into active Business Accounts without approval.
- **FR-028**: The system MUST allow incoming transfers received by Business Accounts via UEN without approval.
- **FR-029**: The system MUST require Business Account withdrawals to enter PENDING approval before completion.
- **FR-030**: The system MUST require outgoing Business Account transfers to enter PENDING approval before completion.
- **FR-031**: The system MUST ensure PENDING Business Account outgoing requests do not reserve funds, change balances, or appear as completed financial transactions.
- **FR-032**: The system MUST display actual current Business Account balances without reducing them for PENDING requests.
- **FR-033**: The system MUST allow multiple PENDING outgoing withdrawals or transfers for the same Business Account.
- **FR-034**: The system MUST allow only the linked authorised Personal Account to approve or reject Business Account outgoing requests.
- **FR-035**: The system MUST revalidate requested amount, current Business Account balance, SGD 7,000.00 retained minimum, and authorised Personal Account identity when approval is attempted.
- **FR-036**: The system MUST complete a Business Account outgoing request only when approval-time validation passes and the Business Account retains at least SGD 7,000.00.
- **FR-037**: The system MUST mark a PENDING Business Account outgoing request as FAILED when approval-time validation fails.
- **FR-038**: The system MUST support approval request statuses PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED.
- **FR-039**: The system MUST NOT persist a separate APPROVED status in the MVP.
- **FR-040**: The system MUST allow only PENDING requests to be approved, rejected, or cancelled.
- **FR-041**: The system MUST treat COMPLETED, REJECTED, CANCELLED, and FAILED approval requests as final.
- **FR-042**: The system MUST allow the Business Account owner to cancel an unresolved PENDING outgoing request before completion.
- **FR-043**: The system MUST require the sender to select recipient account type before entering a transfer identifier.
- **FR-044**: The system MUST use a phone number when the selected recipient type is Personal Account.
- **FR-045**: The system MUST use a UEN when the selected recipient type is Business Account.
- **FR-046**: The system MUST reject transfers to unknown Personal Account phone numbers.
- **FR-047**: The system MUST reject transfers to unknown Business Account UENs.
- **FR-048**: The system MUST reject transfers where selected recipient account type and entered identifier do not match.
- **FR-049**: The system MUST show safe recipient confirmation before transfer submission using recipient username or business display name, recipient account type, partially masked identifier where appropriate, amount, and whether Business Account approval is required for the selected source account.
- **FR-050**: The system MUST reject self-transfer attempts for the MVP.
- **FR-051**: The system MUST reject transfers between the same user's own Personal Account and Business Account for the MVP.
- **FR-052**: The system MUST update sender and recipient balances together only when a transfer completes successfully.
- **FR-053**: The system MUST create one unique transfer operation ID for every successfully completed transfer.
- **FR-054**: The system MUST create one completed sender debit transaction record and one completed recipient credit transaction record for every successfully completed transfer.
- **FR-055**: The system MUST ensure linked transfer debit and credit records each have their own UUID transaction ID and share the same transfer operation ID.
- **FR-056**: The system MUST display Transaction History containing only completed deposits, withdrawals, transfer debits, and transfer credits.
- **FR-057**: The system MUST display Approval History containing Business Account outgoing requests in PENDING, COMPLETED, REJECTED, CANCELLED, or FAILED status.
- **FR-058**: The system MUST show COMPLETED Business Account withdrawals and outgoing transfers in both Approval History and Transaction History.
- **FR-059**: The system MUST exclude PENDING, REJECTED, CANCELLED, and FAILED approval requests from completed financial movements in Transaction History.
- **FR-060**: The system MUST display completed deposit records with credited account, amount in SGD, date/time, status, transaction type, and UUID transaction ID.
- **FR-061**: The system MUST display completed withdrawal records with debited account, amount in SGD, date/time, status, transaction type, and UUID transaction ID.
- **FR-062**: The system MUST display completed transfer debit and credit records with their own UUID transaction IDs and shared transfer operation ID.
- **FR-063**: The system MUST prevent ordinary users from editing or deleting completed financial transaction records.
- **FR-064**: The system MUST provide clear user-facing error outcomes for duplicate registration values, invalid sign-in, invalid money values, insufficient funds, minimum-balance breaches, unknown recipients, mismatched recipient identifiers, self-transfers, own-account transfers, unauthorised approval attempts, and rejected or cancelled Business Account operations.
- **FR-065**: The system MUST ensure error outcomes do not create completed transaction records or unintended balance changes.

### UI/UX Requirements

- **UX-001**: The application MUST present a premium "Midnight Ledger" banking experience that is crisp, modern, clean, confident, visually distinctive, and not playful, cluttered, or unsafe.
- **UX-002**: The visual direction MUST use a deep charcoal or midnight-navy foundation, bright mint, emerald, or teal accents for positive financial actions and highlights, off-white or soft-grey content surfaces, high-contrast typography, rounded cards with subtle depth, minimal polished icons, and restrained transitions only where they improve clarity.
- **UX-003**: The authenticated experience MUST provide a compact left navigation sidebar on desktop and a top bar showing the signed-in username and sign-out action.
- **UX-004**: Primary navigation MUST include Dashboard, Personal Account, Business Account, Transfer, Approvals, and Transactions.
- **UX-005**: The Dashboard MUST include a username welcome header, separate balance cards for available Personal and Business Accounts, clear account-type labels, SGD-formatted balances, quick actions for Deposit, Withdraw, and Transfer, recent-transactions preview, and pending-approvals indicator when applicable.
- **UX-006**: Personal Account and Business Account balance cards MUST be visually distinguishable.
- **UX-007**: Personal Account cards and transfer pages MUST show the Personal Account phone number as the receiving identifier.
- **UX-008**: Business Account cards and transfer pages MUST show the company UEN as the receiving identifier.
- **UX-009**: The Business Account card MUST communicate the SGD 7,000.00 retained-minimum rule clearly but unobtrusively.
- **UX-010**: Pending approval indicators MUST be noticeable without appearing alarming and MUST NOT imply funds have been reserved.
- **UX-011**: Registration and sign-in screens MUST show a branded application name, short value statement, visible form labels, clearly identified password fields, inline validation messages, obvious primary action buttons, and a clear switch between registration and sign-in.
- **UX-012**: Personal Account setup MUST state that no opening deposit is required, the account begins at SGD 0.00 if no funds are added, and a unique phone number is required for receiving transfers.
- **UX-013**: Business Account setup MUST request business display name, company UEN, and opening deposit; explain that an existing Personal Account is required; explain that the user's Personal Account becomes the sole authorised approver; and explain the SGD 7,000.00 opening and retained-minimum rules.
- **UX-014**: Deposit and withdrawal flows MUST show the selected account, an amount input labelled in SGD, applicable business-rule messages, and success confirmation after completion including the UUID transaction ID.
- **UX-015**: Withdrawal flows MUST include a review or confirmation step before completion or submission.
- **UX-016**: Business Account withdrawal submission MUST tell the user it will be sent for approval and will not immediately change the balance.
- **UX-017**: Transfer flow MUST be step-based: select source account, select Personal or Business recipient type, enter the matching phone number or UEN, enter SGD amount, show safe recipient confirmation, show review details, submit or confirm, and display completed, PENDING, or rejected outcome.
- **UX-018**: Transfer review MUST show sender account, recipient confirmation, amount in SGD, whether approval is required, and any Business Account retained-minimum notice.
- **UX-019**: Recipient confirmation MUST clearly indicate whether the destination is a Personal Account or Business Account and MUST show username or business display name plus masked or appropriately presented phone number or UEN.
- **UX-020**: Completed transfer confirmation MUST show amount, recipient confirmation, status, transfer operation ID, and sender debit UUID transaction ID.
- **UX-021**: Approvals MUST provide a modern list of requests with status chips for PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED, filtering by status, and request detail for PENDING actions.
- **UX-022**: Approval request rows or cards MUST show request type, amount in SGD, requested date/time, recipient account type and safe recipient confirmation for transfers, and current status.
- **UX-023**: Approval review MUST show Business Account balance, requested amount, projected balance after approval, and whether the projected balance satisfies the SGD 7,000.00 retained minimum.
- **UX-024**: Transaction History MUST provide readable rows or cards with type, amount in SGD, date/time, status, UUID transaction ID, shared transfer operation ID where applicable, clear credit/debit distinction, and filters for account type and transaction type.
- **UX-025**: Transaction displays involving a Business Account MAY display the business display name and masked or appropriately presented UEN.
- **UX-026**: The app MUST provide polished empty, error, and success states for no transaction history, no Business Account, no pending approvals, failed validation, rejected approval, successful deposit, successful withdrawal, successful transfer, and PENDING Business transaction submission.
- **UX-027**: Messages MUST be clear, calm, informative, and avoid vague technical language when a safe business-rule reason can be displayed.

### Business Rules

- **BR-001**: All monetary values and operations MUST be in Singapore Dollars (SGD) only.
- **BR-002**: Deposits, withdrawals, opening deposits, and transfers MUST use valid SGD amounts with a maximum of two decimal places.
- **BR-003**: Zero, negative, malformed, non-numeric, non-SGD, and invalid-precision money values MUST be rejected.
- **BR-004**: Valid transaction amount examples include SGD 10.00, SGD 105.50, and SGD 7000.00.
- **BR-005**: Invalid transaction amount examples include SGD 0.00, negative values, text input, malformed values, and values with more than two decimal places.
- **BR-006**: Failed, rejected, PENDING, or CANCELLED financial operations MUST NOT create completed transaction records.
- **BR-007**: Failed, rejected, PENDING, or CANCELLED financial operations MUST NOT change balances.
- **BR-008**: A Personal Account has no opening deposit requirement and no retained minimum balance.
- **BR-009**: A Personal Account MAY begin with balance SGD 0.00.
- **BR-010**: A Personal Account outgoing withdrawal or transfer MUST NOT make the balance negative.
- **BR-011**: A Personal Account MUST have one unique phone number for receiving transfers.
- **BR-012**: A Business Account MUST be created only for a signed-in user who already has an active Personal Account.
- **BR-013**: A Business Account MUST have a business display name and one unique UEN for receiving transfers.
- **BR-014**: A Business Account MUST receive an opening deposit of at least SGD 7,000.00 before creation.
- **BR-015**: Business Account creation below SGD 7,000.00 MUST be rejected rather than saved as inactive.
- **BR-016**: A Business Account MUST use the owner's own Personal Account as its exactly one authorised Personal Account.
- **BR-017**: Authorising another user's Personal Account is out of scope for the MVP.
- **BR-018**: A Business Account outgoing withdrawal or transfer MUST NOT complete without approval from its authorised Personal Account.
- **BR-019**: A completed outgoing Business Account withdrawal or transfer MUST leave the Business Account with at least SGD 7,000.00.
- **BR-020**: Deposits into Business Accounts and incoming transfers to Business Accounts do not require approval.
- **BR-021**: A PENDING Business Account outgoing request MUST NOT reserve funds, debit the sender, credit the recipient, alter displayed balance, or appear as a completed financial transaction.
- **BR-022**: A Business Account MAY have multiple PENDING outgoing requests simultaneously.
- **BR-023**: Approval MUST revalidate requested amount, current Business Account balance, retained minimum, and authorised Personal Account identity.
- **BR-024**: Approval does not bypass validation, ownership, sufficient-funds, or minimum-balance rules.
- **BR-025**: Only PENDING approval requests MAY be approved, rejected, or cancelled.
- **BR-026**: COMPLETED, REJECTED, CANCELLED, and FAILED approval requests are final.
- **BR-027**: There is no separately persisted APPROVED status in the MVP.
- **BR-028**: Transfers to Personal Accounts use the recipient Personal Account phone number.
- **BR-029**: Transfers to Business Accounts use the recipient Business Account UEN.
- **BR-030**: A Business Account does not use a phone number as its transfer recipient identifier.
- **BR-031**: Recipient account type and identifier MUST match.
- **BR-032**: Self-transfers are not supported in the MVP.
- **BR-033**: Transfers between the same user's Personal Account and Business Account are not supported in the MVP.
- **BR-034**: Every successful deposit and completed withdrawal MUST create one immutable completed transaction record with a UUID transaction ID.
- **BR-035**: Every completed transfer MUST create two immutable completed transaction records, one debit and one credit, each with its own UUID transaction ID.
- **BR-036**: Linked transfer records MUST share one transfer operation ID.
- **BR-037**: Sender debiting, recipient crediting, and transfer transaction-record creation MUST be atomic.
- **BR-038**: Completed financial transaction records MUST NOT be editable or deletable through ordinary user actions.
- **BR-039**: PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED Business Account approval records MUST be visible in Approval History and clearly distinguished from completed financial transactions.

### Security Requirements

- **SEC-001**: Users MUST authenticate before accessing accounts, histories, money operations, or approval actions.
- **SEC-002**: Users MUST access only accounts they own or Business Account approval requests assigned to their authorised Personal Account.
- **SEC-003**: Passwords MUST NOT appear in ordinary account pages, histories, transaction records, approval records, recipient confirmations, or error outputs.
- **SEC-004**: Financial operations and approval actions MUST be protected against unauthorised access.
- **SEC-005**: Error messages MUST NOT expose sensitive information.
- **SEC-006**: Recipient confirmation MUST NOT expose email addresses or sensitive account details.
- **SEC-007**: Sensitive configuration and secret-management implementation details MUST be handled in the technical plan consistent with the constitution.

### Non-Functional Requirements

- **NFR-001**: The feature MUST remain understandable to non-technical stakeholders and avoid implementation-specific decisions.
- **NFR-002**: The feature MUST provide auditable outcomes for all completed financial operations and Business Account approval workflow events.
- **NFR-003**: The feature MUST provide clear validation feedback that explains what prevented an invalid action.
- **NFR-004**: The feature MUST preserve atomic completion expectations: a financial operation either fully succeeds or leaves balances and completed transaction records unchanged.
- **NFR-005**: The feature MUST keep all applicable business rules traceable from specification to acceptance criteria, plan, tasks, code components, and tests.
- **NFR-006**: All forms MUST use visible field labels.
- **NFR-007**: Error messages MUST identify what must be corrected.
- **NFR-008**: Colour MUST NOT be the only method used to distinguish credits, debits, warnings, approvals, or failure states.
- **NFR-009**: Text and interactive controls MUST remain readable with strong contrast.
- **NFR-010**: Keyboard navigation MUST support primary user flows.
- **NFR-011**: Interactive controls MUST have clear focus states.
- **NFR-012**: Monetary values MUST consistently display the SGD currency marker and exactly two decimal places.
- **NFR-013**: Destructive or final financial actions MUST require clear confirmation before completion or submission.
- **NFR-014**: The primary target is a modern desktop browser on macOS, and the interface MUST remain usable at narrow browser widths.
- **NFR-015**: Navigation MAY adapt from sidebar to a simplified compact navigation layout on smaller screens.
- **NFR-016**: Balance cards, transaction history, transfer forms, and approval requests MUST remain readable without horizontal scrolling for normal use.

### Mandatory Test Requirements

- **TEST-001**: Verify successful Personal Account creation without an opening deposit.
- **TEST-002**: Verify a newly created Personal Account begins at SGD 0.00.
- **TEST-003**: Verify Personal Account phone number uniqueness.
- **TEST-004**: Verify Business Account creation succeeds only when the user already has an active Personal Account, business display name, unique UEN, and opening deposit of SGD 7,000.00 or more.
- **TEST-005**: Verify Business Account creation is rejected below SGD 7,000.00.
- **TEST-006**: Verify Business Account creation is rejected when the user has no active Personal Account.
- **TEST-007**: Verify duplicate Business Account UEN rejection.
- **TEST-008**: Verify duplicate email rejection.
- **TEST-009**: Verify secure password handling expectations and no password exposure.
- **TEST-010**: Verify successful positive deposits for both account types.
- **TEST-011**: Verify rejection of zero and negative deposits.
- **TEST-012**: Verify rejection of malformed, non-numeric, non-SGD, or invalid-precision money inputs.
- **TEST-013**: Verify successful Personal Account withdrawal where sufficient balance exists.
- **TEST-014**: Verify rejection of Personal Account withdrawal that would cause a negative balance.
- **TEST-015**: Verify successful Personal Account outgoing transfer where sufficient balance exists.
- **TEST-016**: Verify rejection of Personal Account transfer that would cause a negative balance.
- **TEST-017**: Verify successful permitted Business Account withdrawal after approval.
- **TEST-018**: Verify rejection or non-completion of unapproved Business Account withdrawals.
- **TEST-019**: Verify rejection of Business Account withdrawals that breach the SGD 7,000.00 minimum.
- **TEST-020**: Verify successful Personal Account transfer lookup by phone number.
- **TEST-021**: Verify successful Business Account transfer lookup by UEN.
- **TEST-022**: Verify rejection of unknown Personal Account phone number.
- **TEST-023**: Verify rejection of unknown Business Account UEN.
- **TEST-024**: Verify rejection when selected recipient account type and identifier do not match.
- **TEST-025**: Verify safe recipient confirmation before transfer completion or approval submission.
- **TEST-026**: Verify rejection of zero and negative transfers.
- **TEST-027**: Verify rejection of self-transfer attempts.
- **TEST-028**: Verify rejection of transfers between the same user's Personal and Business Accounts.
- **TEST-029**: Verify rejection or non-completion of unapproved outgoing Business Account transfers.
- **TEST-030**: Verify rejection of outgoing Business Account transfers that breach the SGD 7,000.00 minimum.
- **TEST-031**: Verify incoming Business Account deposits and UEN transfers proceed without approval.
- **TEST-032**: Verify multiple PENDING Business requests may exist simultaneously.
- **TEST-033**: Verify no fund reservation and unchanged displayed balance while requests are PENDING.
- **TEST-034**: Verify a PENDING request becomes FAILED when another completed request causes retained-minimum validation to fail at approval time.
- **TEST-035**: Verify absence of a separately persisted APPROVED status.
- **TEST-036**: Verify generation of UUID transaction IDs for completed deposits, withdrawals, and transfer records.
- **TEST-037**: Verify generation of one transfer operation ID shared by linked sender debit and recipient credit records.
- **TEST-038**: Verify atomic rollback when a financial operation fails.
- **TEST-039**: Verify unauthorised approval attempts are denied.
- **TEST-040**: Verify PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED approval status transitions and final-state immutability.
- **TEST-041**: Verify users cannot access another user's account, Transaction History, or Approval History.
- **TEST-042**: Verify completed financial transaction records cannot be edited or deleted through ordinary user actions.
- **TEST-043**: Verify Transaction History excludes PENDING, REJECTED, CANCELLED, and FAILED approval requests.
- **TEST-044**: Verify completed Business outgoing operations appear in both Approval History and Transaction History.
- **TEST-045**: Verify Dashboard shows username, account cards, SGD balances, recipient identifiers, quick actions, recent transactions, and pending-approvals indicator.
- **TEST-046**: Verify registration and sign-in screens include required branded, labelled, validated, and navigable elements.
- **TEST-047**: Verify Business Account setup requests business display name, UEN, opening deposit, and required explanatory notices.
- **TEST-048**: Verify transfer flow includes source account, recipient type selector, adaptive identifier field, safe confirmation, review, submission, and outcome states.
- **TEST-049**: Verify Approval screen supports status chips, status filtering, request details, recipient account type, safe recipient data, and PENDING-only actions.
- **TEST-050**: Verify Transaction History supports credit/debit distinction and filters by account type and transaction type.
- **TEST-051**: Verify empty, error, success, and PENDING states use clear, calm, non-technical messaging.
- **TEST-052**: Verify accessibility requirements for labels, contrast, non-colour indicators, keyboard navigation, focus states, and confirmations.
- **TEST-053**: Verify narrow-width usability without horizontal scrolling for normal use.

### Key Entities *(include if feature involves data)*

- **Account Holder**: A registered person with username, unique email, password credentials, and ownership of up to one Personal Account and one Business Account.
- **Personal Account**: An SGD account owned by an Account Holder with no opening deposit requirement, no minimum-balance requirement, and one unique phone number for receiving transfers.
- **Business Account**: An SGD account owned by an Account Holder that is created only when the owner already has an active Personal Account, supplies a business display name, supplies a unique UEN for receiving transfers, and supplies an opening deposit of at least SGD 7,000.00.
- **Authorised Personal Account**: The Business Account owner's own Personal Account, which is the sole account permitted to approve or reject outgoing withdrawal and transfer requests for that Business Account.
- **Money Operation**: A requested deposit, withdrawal, or transfer with an SGD amount, validation outcome, and account-type-specific completion rules.
- **Business Approval Request**: A workflow record for an outgoing Business Account withdrawal or transfer with status PENDING, COMPLETED, REJECTED, CANCELLED, or FAILED.
- **Completed Transaction Record**: An immutable audit record for a completed deposit, withdrawal, transfer debit, or transfer credit.
- **Transfer Operation**: The shared identity of a completed transfer that links one sender debit record and one recipient credit record.
- **Transaction History**: The user-facing view of completed financial movement records only.
- **Approval History**: The user-facing view of Business Account outgoing workflow requests and outcomes.

### Banking Rule Coverage *(mandatory for banking features)*

- **Technology Scope**: The feature remains a specification of the constitutionally approved MVP only; planning must stay within the approved local stack and must not add alternative databases, frontend frameworks, payment gateways, external bank integrations, cloud infrastructure, microservices, message queues, or third-party authentication.
- **MVP Scope**: The feature is limited to registration, authentication, Personal Accounts, Business Accounts, deposits, withdrawals, transfers, transaction history, Business Account outgoing approval, premium UI/UX, tests, traceability, and local deployment readiness.
- **Financial Correctness**: BR-001 through BR-007 define SGD-only money, two-decimal precision, invalid value rejections, negative-balance prevention, and unchanged state after failed operations.
- **Account Types and Identity**: FR-001 through FR-026 and BR-008 through BR-017 define exactly two account types, user ownership limits, unique email, Personal Account phone number, Business Account UEN, business display name, own Personal Account prerequisite, and own Personal Account authorisation.
- **Personal Account Rules**: FR-008 through FR-015 and BR-008 through BR-011 define no opening deposit, SGD 0.00 starting balance, no minimum balance, unique phone recipient identifier, and no negative outgoing balances.
- **Business Account Rules**: FR-016 through FR-042 and BR-012 through BR-027 define rejected creation when prerequisites fail, unique UEN, own-authoriser linkage, approval, revalidation, final statuses, multiple PENDING requests, no fund reservation, minimum balance, and inbound money behavior.
- **Deposits and Withdrawals**: FR-011 through FR-013, FR-027, FR-029, FR-031 through FR-042, BR-034, and TEST-010 through TEST-019 define deposit and withdrawal behavior.
- **Transfers and Linked Records**: FR-014, FR-015, FR-028, FR-030, FR-043 through FR-055, BR-028 through BR-037, and TEST-020 through TEST-038 define transfer behavior, recipient type selection, phone/UEN lookup, safe recipient confirmation, rejection rules, linkage, and atomicity.
- **Business Authorization**: FR-029 through FR-042, BR-016 through BR-027, and TEST-017 through TEST-040 define authorised approval and workflow statuses.
- **Transaction Auditability**: FR-053 through FR-063, BR-034 through BR-039, and TEST-036 through TEST-044 define immutable completed records and distinct approval history.
- **Security and Secrets**: SEC-001 through SEC-007 define authentication, access control, password non-exposure, safe recipient confirmation, and secure planning expectations.
- **UI/UX and Accessibility**: UX-001 through UX-027 and NFR-006 through NFR-016 define the Midnight Ledger app shell, screen-level expectations, empty/success/error states, accessibility, and responsive behavior.
- **Mandatory Tests**: TEST-001 through TEST-053 provide the required traceable test inventory.

### Traceability Matrix *(mandatory)*

| Rule ID | Requirement ID | Acceptance Criteria | Plan Reference | Task ID | Code Component | Test ID / Path |
|---------|----------------|---------------------|----------------|---------|----------------|----------------|
| BR-001 to BR-007 | FR-011, FR-012, FR-014, FR-021, FR-027, FR-036, FR-043, FR-064, FR-065 | Money validation, deposit, withdrawal, transfer, failure, and precision scenarios | Pending | Pending | Pending | TEST-010 to TEST-012, TEST-026, TEST-038 |
| BR-008 to BR-011 | FR-008 to FR-015 | Personal Account opening, unique phone, deposit, withdrawal, transfer success, and insufficient-funds rejection scenarios | Pending | Pending | Pending | TEST-001 to TEST-003, TEST-013 to TEST-016 |
| BR-012 to BR-017 | FR-016 to FR-026 | Business Account prerequisite, business display name, UEN, opening deposit, own-authoriser, and single-authoriser scenarios | Pending | Pending | Pending | TEST-004 to TEST-007 |
| BR-018 to BR-027 | FR-029 to FR-042 | Business outgoing approval, multiple PENDING requests, no reservation, revalidation, final-state, cancellation, failed, no APPROVED status, and unauthorised scenarios | Pending | Pending | Pending | TEST-017 to TEST-019, TEST-029 to TEST-035, TEST-039 to TEST-040 |
| BR-028 to BR-033 | FR-043 to FR-051 | Personal phone lookup, Business UEN lookup, mismatched identifier, unknown recipient, self-transfer, and own-account transfer rejection scenarios | Pending | Pending | Pending | TEST-020 to TEST-028 |
| BR-034 to BR-037 | FR-052 to FR-055, FR-060 to FR-062 | Completed deposit, withdrawal, and linked transfer record scenarios | Pending | Pending | Pending | TEST-036 to TEST-038 |
| BR-038, BR-039 | FR-056 to FR-063 | Transaction History and Approval History distinction and immutable record scenarios | Pending | Pending | Pending | TEST-042 to TEST-044 |
| SEC-001 to SEC-007 | FR-001 to FR-005, FR-034, FR-049, FR-064 | Authentication, access control, safe recipient confirmation, and sensitive-info scenarios | Pending | Pending | Pending | TEST-009, TEST-025, TEST-039, TEST-041 |
| UX-001 to UX-027 | UX-001 to UX-027 | App shell, dashboard, authentication, setup, money-operation, transfer, approval, history, and state scenarios | Pending | Pending | Pending | TEST-045 to TEST-051 |
| NFR-006 to NFR-016 | UX-001 to UX-027 | Accessibility, confirmation, formatting, and responsive scenarios | Pending | Pending | Pending | TEST-052, TEST-053 |
| NFR-002, NFR-005 | All BR, FR, SEC, UX, and TEST identifiers | Traceability and audit coverage sections | Pending | Pending | Pending | TEST-001 to TEST-053 |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new Account Holder can register, sign in, open a Personal Account with a unique phone number, and see an initial balance of SGD 0.00 in one complete user flow.
- **SC-002**: 100% of attempted duplicate email, duplicate Personal Account phone, and duplicate Business Account UEN entries are rejected with clear messages and no duplicate identifier.
- **SC-003**: 100% of Personal Account withdrawals and outgoing transfers that exceed available balance are rejected without balance changes or completed transaction records.
- **SC-004**: 100% of Business Account creation attempts are rejected unless the signed-in user has an active Personal Account, business display name, unique UEN, and opening deposit of at least SGD 7,000.00.
- **SC-005**: 100% of active Business Accounts use the owner's own Personal Account as exactly one authorised approver.
- **SC-006**: 100% of Business Account outgoing withdrawals and transfers require authorised approval before completion and revalidate current rules at approval time.
- **SC-007**: 100% of completed Business Account outgoing withdrawals and transfers leave the Business Account with at least SGD 7,000.00.
- **SC-008**: 100% of Personal Account recipient transfers require Personal Account selection plus phone number, and 100% of Business Account recipient transfers require Business Account selection plus UEN.
- **SC-009**: 100% of mismatched recipient account type and identifier combinations are rejected before money moves.
- **SC-010**: 100% of PENDING Business outgoing requests leave displayed balances unchanged and reserve no funds.
- **SC-011**: If multiple PENDING Business requests exist, each approval attempt is independently revalidated and may become FAILED if current rules no longer pass.
- **SC-012**: 100% of successful deposits and completed withdrawals are visible in Transaction History with amount in SGD, status, type, timestamp, account, and UUID transaction ID.
- **SC-013**: 100% of successful transfers show one sender debit record and one recipient credit record, each with its own UUID transaction ID and the same transfer operation ID.
- **SC-014**: 100% of failed, rejected, PENDING, or CANCELLED operations leave balances unchanged and create no completed financial transaction records.
- **SC-015**: 100% of unauthorised account, history, money-operation, and approval attempts are denied.
- **SC-016**: Every core business rule in this specification has at least one acceptance scenario and at least one `TEST-###` identifier for later automated testing.
- **SC-017**: Users can distinguish Transaction History from Approval History and can identify whether a Business outgoing request is PENDING, COMPLETED, REJECTED, CANCELLED, or FAILED.
- **SC-018**: 100% of monetary values displayed in primary account, transfer, approval, and transaction views include the SGD marker and exactly two decimal places.
- **SC-019**: Primary navigation destinations are reachable from the authenticated app shell in no more than one navigation action on desktop width.
- **SC-020**: 100% of primary forms show visible labels, inline validation messages, and a clear primary action.
- **SC-021**: 100% of final withdrawal, transfer, and approval actions provide a review or confirmation step before completion or submission.
- **SC-022**: Credit, debit, warning, approval, and failure states remain distinguishable without relying on colour alone.
- **SC-023**: Primary registration, sign-in, dashboard, transfer, approval, and transaction-history flows are usable with keyboard navigation and visible focus states.
- **SC-024**: Dashboard cards, transfer forms, approval requests, and transaction history remain readable at narrow browser widths without horizontal scrolling for normal use.
- **SC-025**: Users can identify the product as a polished Midnight Ledger banking application from the registration/sign-in screens and authenticated dashboard without relying on explanatory training text.

## Assumptions

- Account Holder identity is represented once per registered user, and that user may own up to one Personal Account and one Business Account for the MVP.
- A user's registered email belongs to the user identity, while Personal Account phone number and Business Account UEN belong to account-specific transfer recipient identity.
- A Business Account opening attempt that does not satisfy the Personal Account prerequisite, business display name, unique UEN, or SGD 7,000.00 opening deposit is rejected; inactive Business Account creation is not part of the MVP.
- The Business Account owner's own Personal Account is the only authorised approver for that Business Account in the MVP.
- Approval and completion of an outgoing Business Account request may occur as one user action, provided approval-time validation passes before money moves.
- A Business Account may have multiple PENDING outgoing requests, but none reserve funds or alter displayed balances.
- Date/time display must be understandable to the user and consistent within Transaction History and Approval History, while exact formatting belongs to later design work.
- Transaction History is limited to completed financial movements associated with accounts owned by the signed-in user.
- Approval History is limited to Business Account outgoing requests owned by the signed-in user's Business Account or assigned to the user's own authorised Personal Account role.
- This specification intentionally avoids implementation decisions, including database tables, models, URLs, form classes, templates, middleware, modules, test framework, server configuration, deployment details, UI libraries, CSS frameworks, and JavaScript frameworks.
