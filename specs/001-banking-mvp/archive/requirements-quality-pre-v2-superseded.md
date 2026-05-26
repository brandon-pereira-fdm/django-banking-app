# Superseded Notice

This checklist belongs to the pre-version-2.0.0 account model, where a Personal Account authorised a Business Account. It is preserved only as a historical artefact.

This file must not be used as an implementation gate. It was replaced by `../checklists/requirements-quality-v2.md`.

# Requirements-Quality Checklist: Banking MVP

**Purpose**: Validate specification completeness, clarity, constitutional
alignment, security, testability, and readiness before `/speckit-plan`.
**Created**: 2026-05-25
**Feature**: [spec.md](../spec.md)

## Scope and Constitution Alignment

- [ ] **CHK-SCOPE-001**: Does the specification keep the MVP scope aligned with the constitution's local Python/Django/SQLite3/templates/Waitress constraint without introducing alternative databases, frontend frameworks, payment platforms, external bank integrations, cloud infrastructure, microservices, message queues, or third-party authentication? **Failure: Blocking** [Consistency, Spec §Banking Rule Coverage, Constitution §I]
- [ ] **CHK-SCOPE-002**: Are all financial requirements explicitly limited to SGD-only operations with no other currency path implied? **Failure: Blocking** [Completeness, Spec §BR-001, Spec §SC-014, Constitution §I]
- [ ] **CHK-SCOPE-003**: Are Personal Account and Business Account requirements consistent with the constitution's approved account types and MVP scope? **Failure: Blocking** [Consistency, Spec §FR-007, Spec §BR-008 to BR-018, Constitution §III-V]
- [ ] **CHK-SCOPE-004**: Does the specification avoid plan-level implementation choices such as models, schema, views, forms, routes, middleware, UI libraries, deployment configuration, or technical architecture? **Failure: Blocking** [Clarity, Spec §Assumptions]

## Account Ownership and Identity

- [ ] **CHK-ACCOUNT-001**: Does the specification clearly state that one user may own one Personal Account and one Business Account for the MVP? **Failure: Blocking** [Completeness, Spec §FR-008, Spec §Account Holder]
- [ ] **CHK-ACCOUNT-002**: Are Personal Account opening requirements unambiguous that no opening deposit is required and no minimum balance applies? **Failure: Blocking** [Clarity, Spec §FR-009, Spec §BR-008 to BR-010]
- [ ] **CHK-ACCOUNT-003**: Are Business Account creation requirements unambiguous that an active Personal Account and at least SGD 7,000.00 opening deposit are required before creation? **Failure: Blocking** [Clarity, Spec §FR-015 to FR-018, Spec §BR-011 to BR-013]
- [ ] **CHK-ACCOUNT-004**: Does the specification clearly state that each Business Account has exactly one authorised Personal Account and that it must be the owner's own Personal Account for the MVP? **Failure: Blocking** [Completeness, Spec §FR-019 to FR-021, Spec §BR-014 to BR-015]
- [ ] **CHK-ACCOUNT-005**: Is the transfer recipient identity model clear enough when phone numbers are unique to users but a user may own both account types? **Failure: Blocking** [Ambiguity, Spec §FR-036 to FR-040, Spec §Account Holder, Spec §Personal Account, Spec §Business Account]

## Personal Account Rules

- [ ] **CHK-PERSONAL-001**: Are Personal Account withdrawal requirements clear that any valid positive amount is allowed when sufficient funds exist? **Failure: Blocking** [Completeness, Spec §FR-011, Spec §BR-010]
- [ ] **CHK-PERSONAL-002**: Are Personal Account outgoing transfer requirements clear that any valid positive amount is allowed when sufficient funds exist? **Failure: Blocking** [Completeness, Spec §FR-013, Spec §BR-010]
- [ ] **CHK-PERSONAL-003**: Does the specification clearly allow a Personal Account to reach exactly SGD 0.00 after a valid withdrawal or transfer? **Failure: Blocking** [Clarity, Spec §BR-008 to BR-010, Spec §SC-003]
- [ ] **CHK-PERSONAL-004**: Are overdraft and negative-balance rejection requirements measurable and linked to acceptance scenarios and test IDs? **Failure: Blocking** [Traceability, Spec §FR-012, Spec §FR-014, Spec §TEST-013, Spec §TEST-015]

## Business Account Rules

- [ ] **CHK-BUSINESS-001**: Are Business Account deposit and incoming-transfer requirements clear that approval is not required? **Failure: Blocking** [Completeness, Spec §FR-022 to FR-023, Spec §BR-018]
- [ ] **CHK-BUSINESS-002**: Are outgoing Business Account withdrawal and transfer requirements clear that approval is required before completion? **Failure: Blocking** [Completeness, Spec §FR-024 to FR-027, Spec §BR-016]
- [ ] **CHK-BUSINESS-003**: Is the retained-minimum rule measurable as at least SGD 7,000.00 after every completed outgoing withdrawal or transfer? **Failure: Blocking** [Measurability, Spec §FR-029 to FR-030, Spec §BR-017, Spec §SC-007]
- [ ] **CHK-BUSINESS-004**: Are approval-time revalidation requirements complete for amount, current balance, retained minimum, and authorised Personal Account identity? **Failure: Blocking** [Completeness, Spec §FR-028, Spec §BR-020]

## Transfers and Transaction Records

- [ ] **CHK-TRANSFER-001**: Are transfer initiation requirements clear that recipient phone number is used, and is the recipient account resolution unambiguous? **Failure: Blocking** [Ambiguity, Spec §FR-036 to FR-037]
- [ ] **CHK-TRANSFER-002**: Are self-transfers and same-user Personal-to-Business transfers explicitly allowed or rejected? **Failure: Blocking** [Clarity, Spec §FR-039 to FR-040, Spec §BR-024 to BR-025]
- [ ] **CHK-TRANSFER-003**: Are completed transfer record requirements complete: one transfer operation ID, one sender debit record, one recipient credit record, and linked IDs? **Failure: Blocking** [Completeness, Spec §FR-041 to FR-044, Spec §BR-027 to BR-029]
- [ ] **CHK-TRANSFER-004**: Are UUID transaction ID requirements specified for each completed transaction record? **Failure: Blocking** [Completeness, Spec §FR-048 to FR-050, Spec §BR-026 to BR-028]
- [ ] **CHK-TRANSFER-005**: Are failed, Pending, Rejected, or Cancelled transfer requirements clear that no balances move and no completed transaction records are created? **Failure: Blocking** [Clarity, Spec §FR-026, Spec §FR-053, Spec §BR-006 to BR-007]
- [ ] **CHK-TRANSFER-006**: Are atomic completion requirements stated for transfers in measurable language? **Failure: Blocking** [Measurability, Spec §FR-041, Spec §BR-029, Spec §NFR-004]

## Business Approval Workflow

- [ ] **CHK-APPROVAL-001**: Are the allowed workflow statuses defined as Pending, Completed, Rejected, Cancelled, and Failed? **Failure: Blocking** [Completeness, Spec §FR-032, Spec §Business Approval Request]
- [ ] **CHK-APPROVAL-002**: Is any constitution/spec terminology mismatch around an `Approved` status resolved before planning? **Failure: Blocking** [Conflict, Spec §FR-032, Constitution §VIII]
- [ ] **CHK-APPROVAL-003**: Does the specification clearly define who may approve, reject, and cancel Business Account outgoing requests? **Failure: Blocking** [Clarity, Spec §FR-027, Spec §FR-035, Spec §User Story 5]
- [ ] **CHK-APPROVAL-004**: Does the specification state that only Pending requests may transition to another status? **Failure: Blocking** [Completeness, Spec §FR-033, Spec §BR-022]
- [ ] **CHK-APPROVAL-005**: Does the specification state that Completed, Rejected, Cancelled, and Failed statuses are terminal and cannot be actioned again? **Failure: Blocking** [Completeness, Spec §FR-034, Spec §BR-023]
- [ ] **CHK-APPROVAL-006**: Does the specification define whether multiple Pending requests are allowed for the same Business Account and how that affects review expectations? **Failure: Blocking** [Gap, Spec §FR-024 to FR-035]
- [ ] **CHK-APPROVAL-007**: Does the specification clearly state that funds are not reserved while requests are Pending? **Failure: Blocking** [Clarity, Spec §FR-026, Spec §BR-019]

## Validation and Security

- [ ] **CHK-SECURITY-001**: Are zero, negative, non-numeric, malformed, non-SGD, and excessive-precision money inputs all rejected by explicit requirements? **Failure: Blocking** [Completeness, Spec §BR-002 to BR-005, Spec §TEST-010 to TEST-011]
- [ ] **CHK-SECURITY-002**: Are authentication and ownership restrictions measurable for accounts, transactions, approvals, and financial operations? **Failure: Blocking** [Measurability, Spec §SEC-001 to SEC-004, Spec §SC-011]
- [ ] **CHK-SECURITY-003**: Are password and sensitive-information protection requirements complete for account pages, histories, recipient confirmations, and errors? **Failure: Blocking** [Completeness, Spec §SEC-003, Spec §SEC-005 to SEC-006]
- [ ] **CHK-SECURITY-004**: Are clear error-message requirements defined without permitting unintended balance changes or completed transaction records? **Failure: Blocking** [Consistency, Spec §FR-052 to FR-053, Spec §NFR-003]

## Transaction and Approval History

- [ ] **CHK-HISTORY-001**: Are completed financial transaction records clearly distinct from approval workflow records? **Failure: Blocking** [Clarity, Spec §FR-045 to FR-047, Spec §BR-031]
- [ ] **CHK-HISTORY-002**: Are UUID transaction IDs and shared transfer operation IDs visible where appropriate in history requirements? **Failure: Blocking** [Completeness, Spec §FR-048 to FR-050, Spec §UX-022]
- [ ] **CHK-HISTORY-003**: Are access restrictions for Transaction History and Approval History complete and measurable? **Failure: Blocking** [Measurability, Spec §SEC-001 to SEC-002, Spec §TEST-032]
- [ ] **CHK-HISTORY-004**: Are history requirements explicit that Pending, Rejected, Cancelled, and Failed approval requests are excluded from Transaction History? **Failure: Blocking** [Clarity, Spec §FR-045 to FR-047, Spec §TEST-034]

## UI/UX Requirements

- [ ] **CHK-UX-001**: Is the premium visual direction sufficiently defined, and is the requested "Midnight Ledger" style name or equivalent product identity explicitly specified? **Failure: Non-Blocking** [Gap, Spec §UX-001 to UX-002]
- [ ] **CHK-UX-002**: Are requirements present for authentication, dashboard, account pages, deposit, withdrawal, transfer, approvals, and transactions screens? **Failure: Blocking** [Completeness, Spec §UX-003 to UX-024]
- [ ] **CHK-UX-003**: Are business-rule notices specified for account setup, Business Account retained minimum, pending approvals, and money-operation flows? **Failure: Blocking** [Coverage, Spec §UX-007, Spec §UX-012, Spec §UX-015, Spec §UX-017, Spec §UX-021]
- [ ] **CHK-UX-004**: Are confirmation steps specified for destructive or final financial actions? **Failure: Blocking** [Completeness, Spec §UX-014, Spec §NFR-013, Spec §SC-017]
- [ ] **CHK-UX-005**: Are success, error, empty, rejected, and pending states specified clearly enough for planning? **Failure: Non-Blocking** [Completeness, Spec §UX-023 to UX-024]
- [ ] **CHK-UX-006**: Are accessibility requirements defined for visible labels, contrast, non-colour indicators, keyboard navigation, focus states, and confirmations? **Failure: Blocking** [Coverage, Spec §NFR-006 to NFR-013]
- [ ] **CHK-UX-007**: Are responsive behavior requirements clear enough for desktop-first macOS use and narrow browser widths? **Failure: Non-Blocking** [Clarity, Spec §NFR-014 to NFR-016, Spec §SC-020]

## Testability and Traceability

- [ ] **CHK-TRACE-001**: Does each core business rule have at least one measurable acceptance scenario and one `TEST-###` identifier? **Failure: Blocking** [Traceability, Spec §Traceability Matrix, Spec §TEST-001 to TEST-043]
- [ ] **CHK-TRACE-002**: Are requirement identifiers present across functional, business, security, non-functional, UI/UX, and test requirements? **Failure: Blocking** [Completeness, Spec §Requirements]
- [ ] **CHK-TRACE-003**: Does the traceability matrix provide enough mapping for `/speckit-plan` to preserve links from requirement to acceptance criteria, tasks, code components, and tests? **Failure: Blocking** [Traceability, Spec §Traceability Matrix]
- [ ] **CHK-TRACE-004**: Are success criteria measurable and technology-agnostic enough to validate readiness without implementation details? **Failure: Blocking** [Measurability, Spec §Success Criteria]

## Blocking Ambiguities Found

- **CHK-ACCOUNT-005 / CHK-TRANSFER-001**: The specification says phone numbers are unique to registered users and transfers use recipient phone numbers, while users may own both a Personal Account and a Business Account. The spec does not fully define how an external sender's phone-number transfer resolves which recipient account receives funds when the recipient owns both account types.
- **CHK-APPROVAL-002**: The current spec uses Pending, Completed, Rejected, Cancelled, and Failed, while the constitution still mentions approved-state treatment. The spec needs either explicit wording that approval is an action that immediately leads to Completed or Failed, or the constitution/spec terminology must be reconciled before planning.
- **CHK-APPROVAL-006**: The specification states that Pending requests do not reserve funds, but it does not define whether multiple Pending outgoing requests may exist concurrently for the same Business Account.

## Specification Corrections Required Before Planning

- Clarify phone-number transfer account resolution for recipients who own both account types.
- Reconcile approval lifecycle terminology with the constitution's approved-state wording.
- Define whether multiple Pending Business Account outgoing requests are allowed, limited, or rejected.

## Readiness Verdict

**Not ready until blocking clarifications are resolved.**

The specification is strong overall and covers the constitution, banking rules,
security, traceability, and premium UI/UX direction well. The three blocking
items above affect transfer behavior, approval workflow testing, and
constitution compliance, so they should be resolved before `/speckit-plan`.

---

# Requirements-Quality Re-Run: Constitution 1.1.0 Banking MVP

**Purpose**: Re-review the updated specification after constitution amendment
1.1.0 and clarification updates, with special focus on the three previous
blocking ambiguities.
**Created**: 2026-05-25
**Feature**: [spec.md](../spec.md)

## Amendment 1.1.0 Resolution Checks

- [x] **CHK-RERUN-001**: Are Personal Account transfer recipient requirements clearly defined as unique Personal Account phone numbers rather than user-level phone numbers? **Failure: Blocking** **Result: Resolved** [Clarity, Spec §FR-009 to FR-010, Spec §BR-011, Spec §Personal Account]
- [x] **CHK-RERUN-002**: Are Business Account transfer recipient requirements clearly defined as unique company UEN values, with Business Accounts explicitly not using phone numbers as incoming transfer identifiers? **Failure: Blocking** **Result: Resolved** [Clarity, Spec §FR-018 to FR-020, Spec §BR-013, Spec §BR-029 to BR-030, Spec §Business Account]
- [x] **CHK-RERUN-003**: Does the transfer flow require recipient account type selection before identifier entry, so Personal recipients use phone numbers and Business recipients use UENs? **Failure: Blocking** **Result: Resolved** [Completeness, Spec §FR-043 to FR-045, Spec §UX-017, Spec §SC-008]
- [x] **CHK-RERUN-004**: Is recipient account resolution unambiguous for users who own both account types because identifiers belong to account-specific recipient identity? **Failure: Blocking** **Result: Resolved** [Clarity, Spec §Assumptions, Spec §BR-028 to BR-031, Spec §Key Entities]
- [x] **CHK-RERUN-005**: Are safe recipient confirmation requirements present before transfer completion or approval submission, without exposing sensitive details? **Failure: Blocking** **Result: Resolved** [Completeness, Spec §FR-049, Spec §SEC-006, Spec §UX-019, Spec §TEST-025]

## Approval Lifecycle Terminology

- [x] **CHK-RERUN-006**: Are Business approval request statuses consistently limited to PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED? **Failure: Blocking** **Result: Resolved** [Consistency, Spec §FR-038, Spec §BR-025 to BR-027, Spec §Business Approval Request]
- [x] **CHK-RERUN-007**: Does the specification state that approval is an action and not a separate persisted APPROVED status? **Failure: Blocking** **Result: Resolved** [Clarity, Spec §FR-039, Spec §BR-027, Spec §TEST-035]
- [x] **CHK-RERUN-008**: Are completed financial transactions created only when approval succeeds and money movement completes? **Failure: Blocking** **Result: Resolved** [Consistency, Spec §FR-036 to FR-037, Spec §FR-052 to FR-055, Spec §BR-034 to BR-037]
- [x] **CHK-RERUN-009**: Are terminal workflow states defined so COMPLETED, REJECTED, CANCELLED, and FAILED requests cannot be actioned again? **Failure: Blocking** **Result: Resolved** [Completeness, Spec §FR-040 to FR-041, Spec §BR-025 to BR-026, User Story 5]

## Multiple Pending Business Requests

- [x] **CHK-RERUN-010**: Does the specification explicitly allow multiple PENDING outgoing Business Account withdrawal or transfer requests at the same time? **Failure: Blocking** **Result: Resolved** [Completeness, Spec §FR-033, Spec §BR-022, Spec §TEST-032]
- [x] **CHK-RERUN-011**: Are PENDING requests specified as not reserving funds, moving funds, altering displayed balances, or appearing as completed financial transactions? **Failure: Blocking** **Result: Resolved** [Clarity, Spec §FR-031 to FR-032, Spec §BR-021, Spec §TEST-033]
- [x] **CHK-RERUN-012**: Are approval-time revalidation requirements complete for requested amount, current balance, retained minimum, and authorised Personal Account identity? **Failure: Blocking** **Result: Resolved** [Completeness, Spec §FR-035 to FR-037, Spec §BR-023 to BR-024]
- [x] **CHK-RERUN-013**: Is the later-failure scenario specified when one completed request causes another PENDING request to fail retained-minimum validation? **Failure: Blocking** **Result: Resolved** [Scenario Coverage, User Story 5 Scenario 8 to 10, Spec §TEST-034, Spec §SC-011]

## Account Identity and Setup

- [x] **CHK-RERUN-014**: Are Business Account requirements complete for business display name, unique UEN, owner, exactly one authorised Personal Account, and opening deposit of at least SGD 7,000.00? **Failure: Blocking** **Result: Resolved** [Completeness, Spec §FR-016 to FR-026, Spec §BR-012 to BR-017, Spec §Business Account]
- [x] **CHK-RERUN-015**: Are rejection requirements present for missing UEN, duplicate UEN, missing Personal Account prerequisite, and insufficient opening deposit? **Failure: Blocking** **Result: Resolved** [Coverage, Spec §FR-019 to FR-023, User Story 3 Scenario 3 to 6]
- [x] **CHK-RERUN-016**: Are Personal Account unique phone-number receiving identifier requirements retained after the UEN amendment? **Failure: Blocking** **Result: Resolved** [Consistency, Spec §FR-009 to FR-010, Spec §BR-011, User Story 2 Scenario 1 to 2]

## Transfer and UI Requirements

- [x] **CHK-RERUN-017**: Are transfer UI requirements present for Personal-by-phone and Business-by-UEN recipient selection? **Failure: Blocking** **Result: Resolved** [Completeness, Spec §UX-017 to UX-019, User Story 4]
- [x] **CHK-RERUN-018**: Are Business Account setup UI requirements updated to request business display name, UEN, opening deposit, and explanatory notices? **Failure: Blocking** **Result: Resolved** [Completeness, Spec §UX-013, User Story 6 Scenario 2, Spec §TEST-047]
- [x] **CHK-RERUN-019**: Are acceptance scenarios present for duplicate UEN, unknown UEN, identifier-type mismatch, multiple PENDING requests, and approval revalidation failure? **Failure: Blocking** **Result: Resolved** [Scenario Coverage, User Story 3 Scenario 5, User Story 4 Scenario 7 to 10, User Story 5 Scenario 7 to 10]
- [x] **CHK-RERUN-020**: Are no superseded phone-number-only transfer requirements left in the specification? **Failure: Blocking** **Result: Resolved** [Consistency, Spec §FR-043 to FR-049, Spec §BR-028 to BR-031, Spec §SC-008]

## Constitution 1.1.0 Alignment

- [x] **CHK-RERUN-021**: Does the specification remain aligned with constitution version 1.1.0 for recipient identifiers, UEN uniqueness, safe confirmation, approval lifecycle, and multiple PENDING requests? **Failure: Blocking** **Result: Resolved** [Consistency, Spec §Clarifications, Spec §Banking Rule Coverage, Constitution §III, §VII, §VIII]
- [x] **CHK-RERUN-022**: Does the specification preserve unchanged constitutional rules for SGD-only money, Personal Account no-minimum-balance behavior, Business Account SGD 7,000.00 opening and retained-minimum rules, transaction UUIDs, transfer operation IDs, security, tests, and traceability? **Failure: Blocking** **Result: Resolved** [Consistency, Spec §BR-001 to BR-039, Spec §TEST-001 to TEST-053, Spec §Traceability Matrix]
- [x] **CHK-RERUN-023**: Does the specification still avoid implementation architecture, database schema, Django model, view, form, URL, CSS framework, JavaScript framework, and deployment configuration decisions? **Failure: Blocking** **Result: Resolved** [Scope Control, Spec §Assumptions, Spec §Banking Rule Coverage]

## Previous Blocking Issues Status

- **Transfer recipient identification**: Resolved. The specification now separates Personal Account phone numbers from Business Account UENs, requires recipient account type selection, rejects mismatched identifier/type combinations, and makes recipient mapping account-specific and unambiguous.
- **Business approval lifecycle terminology**: Resolved. The specification consistently uses PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED; approval is an action; no persisted APPROVED status is allowed; completed transaction records are created only when money movement completes.
- **Multiple Pending Business outgoing requests**: Resolved. The specification allows multiple PENDING requests, states that they do not reserve or move funds, requires independent approval-time revalidation, and defines the later FAILED outcome after another request completes.

## Blocking Ambiguities Found

None found in the reviewed constitution 1.1.0 amendment areas.

## Specification Corrections Required Before Planning

No blocking corrections required before planning. Optional editorial cleanup may archive or supersede the earlier checklist verdict so readers do not mistake the old pre-amendment status for the current readiness state.

## Readiness Verdict

**Ready for `/speckit-plan`.**

The updated specification is constitutionally aligned with version 1.1.0,
resolves the three previous blocking ambiguities, preserves the approved banking
rules, and remains technology-agnostic enough for technical planning.
