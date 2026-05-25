# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`

**Created**: [DATE]

**Status**: Draft

**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST [specific capability, e.g., "allow users to create accounts"]
- **FR-002**: System MUST [specific capability, e.g., "validate email addresses"]
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

### Banking Rule Coverage *(mandatory for banking features)*

- **Technology Scope**: Confirm the feature uses Python 3.11+, Django, SQLite3,
  Django templates, and Waitress only, restricts money to SGD, and does not add
  alternative databases, frontend frameworks, payment gateways, external bank
  integrations, cloud infrastructure, microservices, message queues, or
  third-party authentication.
- **MVP Scope**: Confirm the feature is limited to approved MVP scope or cite
  the approved constitutional amendment.
- **Financial Correctness**: List all monetary validations, decimal arithmetic
  requirements, invalid-value rejections, negative-balance prevention, and
  failed-operation rollback expectations.
- **Account Types and Identity**: State requirements for exactly Personal
  Account and Business Account, users with both account types, unique user
  emails, Django password hashing, user-selected usernames, unique Personal
  Account phone numbers, unique Business Account UENs, and business display
  names.
- **Personal Account Rules**: State no-opening-deposit, SGD 0.00 starting
  balance, no minimum balance, withdrawal, transfer, and audit requirements.
- **Business Account Rules**: State SGD 7,000.00 opening-deposit handling,
  rejection behavior for insufficient opening deposits, unique UEN requirements,
  own authorised Personal Account linkage, minimum-balance enforcement, and
  inbound money behavior.
- **Deposits and Withdrawals**: State account-type-specific deposit and
  withdrawal validation, approval, and UUID transaction-record rules.
- **Transfers and Linked Records**: State Personal Account phone lookup,
  Business Account UEN lookup, recipient account type selection, safe recipient
  confirmation, mismatched identifier rejection, self/own-account transfer
  handling, transfer operation ID, linked debit/credit records, and atomicity
  requirements.
- **Business Authorization**: Define the authorised Personal Account link and
  PENDING, COMPLETED, REJECTED, CANCELLED, and FAILED states for outgoing
  Business Account withdrawals/transfers; state that approval is an action and
  no separate APPROVED status is persisted; define multiple PENDING request and
  approval-time revalidation behavior.
- **Transaction Auditability**: Define immutable completed transaction fields
  and distinguish workflow audit records from completed financial transactions.
- **Security and Secrets**: Identify any sensitive configuration and how it is
  kept out of GitHub, including `.gitignore` coverage and server-side
  enforcement.
- **Mandatory Tests**: Identify all applicable `TEST-###` cases required by the
  constitution for account creation, duplicates, password hashing, deposits,
  withdrawals, Personal Account phone lookup, Business Account UEN lookup,
  duplicate UEN rejection, mismatched recipient identifiers, safe recipient
  confirmation, transfers, business approvals, multiple PENDING requests, no
  fund reservation, FAILED revalidation outcomes, absence of persisted APPROVED
  status, UUIDs, linked transfer IDs, and rollback.

### Traceability Matrix *(mandatory)*

| Rule ID | Requirement ID | Acceptance Criteria | Plan Reference | Task ID | Code Component | Test ID / Path |
|---------|----------------|---------------------|----------------|---------|----------------|----------------|
| [BR-###/SEC-###/NFR-###] | [FR-###] | [Scenario #] | [Plan section or Pending] | [T### or Pending] | [Path or Pending] | [TEST-### / path or Pending] |

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]

## Assumptions

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right assumptions based on reasonable defaults
  chosen when the feature description did not specify certain details.
-->

- [Assumption about target users, e.g., "Users have stable internet connectivity"]
- [Assumption about scope boundaries, e.g., "Mobile support is out of scope for v1"]
- [Assumption about data/environment, e.g., "Existing authentication system will be reused"]
- [Dependency on existing system/service, e.g., "Requires access to the existing user profile API"]
