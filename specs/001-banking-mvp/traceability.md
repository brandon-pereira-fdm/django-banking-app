# Traceability: Banking MVP Constitution v2.0.0

This map links specification requirements to planned components and tests. Task IDs and code paths will be finalized after `/speckit.tasks` is regenerated.

## Requirement to Component and Test Map

| Requirement IDs | Planned Component(s) | Planned Test Coverage |
|---|---|---|
| FR-001 to FR-010, BR-007 to BR-009, SEC-001 to SEC-002 | `users.models.CustomUser`, registration forms/views, context guards | TEST-001 to TEST-006, TEST-011 |
| FR-011 to FR-019, BR-010 to BR-013 | `banking.models.PersonalAccount`, `banking.services.accounts`, Personal pages | TEST-007 to TEST-018 |
| FR-020 to FR-026, BR-014 to BR-018 | `banking.models.BusinessAccount`, `BusinessMembership`, `CompletedFinancialTransaction`, `BusinessAccessAuditEvent`, Business registration service | TEST-002, TEST-009 to TEST-010 |
| FR-027 to FR-048, BR-018 to BR-022, SEC-003 to SEC-006 | `BusinessMembership`, `BusinessInvitation`, `BusinessAccessAuditEvent`, membership/invitation services, member pages | TEST-037 to TEST-049, TEST-054 |
| FR-049 to FR-056, BR-034 to BR-038 | recipient resolution service, transfer forms, `TransferOperation`, completed transaction records | TEST-019 to TEST-022 |
| FR-057 to FR-068, BR-023 to BR-033 | `BusinessApprovalRequest`, approval services, approval pages | TEST-023 to TEST-036 |
| FR-069 to FR-073, BR-001 to BR-006, BR-037 to BR-039, NFR-004 | money validation helper, transaction services, transfer services, transaction models | TEST-012 to TEST-022, TEST-035 to TEST-036 |
| FR-074 to FR-080, BR-040 to BR-041 | Transaction History, Approval History, Access Audit History pages and queries | TEST-050 to TEST-054 |
| SEC-001 to SEC-010, NFR-007 to NFR-008 | auth decorators/helpers, membership checks, CSRF-protected forms, secret settings | TEST-004 to TEST-006, TEST-041, TEST-047, TEST-049, TEST-054 |
| UX-001 to UX-021, NFR-006 | Django templates, custom CSS, navigation shells, reusable includes | TEST-055 plus manual UI acceptance checklist in tasks |
| NFR-001 to NFR-005 | plan/tasks governance, services, tests, traceability docs | All TEST identifiers; `/speckit.analyze` before implementation |

## Mandatory Test Inventory

| TEST ID | Planned Test Area |
|---|---|
| TEST-001 | Personal registration creates Personal-only access and one Personal Account |
| TEST-002 | Business registration creates Business-only access, Business Account, initial AUTHORISER membership, and opening-deposit transaction |
| TEST-003 | Duplicate email rejected across Personal and Business identities |
| TEST-004 | Personal login denied Business pages and invitations |
| TEST-005 | Business login denied Personal pages |
| TEST-006 | Separate credentials required for both contexts |
| TEST-007 | Personal starts at SGD 0.00 and requires unique phone |
| TEST-008 | Duplicate Personal phone rejected |
| TEST-009 | Business registration requires display name, unique UEN, and opening deposit >= SGD 7,000.00 |
| TEST-010 | Missing/duplicate UEN and insufficient opening deposit rejected |
| TEST-011 | Password hashing and no password exposure |
| TEST-012 | Successful positive deposits for Personal and Business Accounts |
| TEST-013 | MEMBER and AUTHORISER may deposit into Business Account without approval |
| TEST-014 | Zero, negative, malformed, non-numeric, non-SGD, and excessive-precision amounts rejected |
| TEST-015 | Personal withdrawal and full-balance withdrawal to SGD 0.00 |
| TEST-016 | Personal negative-balance withdrawal rejected |
| TEST-017 | Personal outgoing transfer and full-balance transfer to SGD 0.00 |
| TEST-018 | Personal transfer that would make balance negative rejected |
| TEST-019 | Personal recipient lookup by phone |
| TEST-020 | Business recipient lookup by UEN |
| TEST-021 | Unknown phone, unknown UEN, mismatch, and self-transfer rejected |
| TEST-022 | Completed transfer creates one operation ID and two linked UUID records |
| TEST-023 | MEMBER may submit withdrawal and transfer requests |
| TEST-024 | AUTHORISER may submit withdrawal and transfer requests |
| TEST-025 | PENDING requests do not move, reserve funds, or create completed records |
| TEST-026 | MEMBER cannot approve, reject, invite, assign roles, promote, remove, or cancel another user's request |
| TEST-027 | AUTHORISER may approve any PENDING request; one approval is sufficient |
| TEST-028 | AUTHORISER may approve own PENDING request |
| TEST-029 | AUTHORISER may reject any PENDING request |
| TEST-030 | MEMBER may cancel own PENDING request only |
| TEST-031 | AUTHORISER may cancel any PENDING request |
| TEST-032 | No persisted APPROVED status exists |
| TEST-033 | Terminal statuses cannot be actioned again |
| TEST-034 | Multiple PENDING requests coexist and are independently revalidated |
| TEST-035 | Business outgoing completion may leave exactly SGD 7,000.00 |
| TEST-036 | Business approval fails at SGD 6,999.99 with FAILED status, no movement, and no completed records |
| TEST-037 | AUTHORISER can invite MEMBER and AUTHORISER roles |
| TEST-038 | Invitations grant no access before acceptance |
| TEST-039 | Invited Business-only login can accept invitation |
| TEST-040 | New Business-only registration from invitation can accept invitation |
| TEST-041 | Personal-only login cannot accept Business invitation |
| TEST-042 | Business User can belong to multiple Business Accounts |
| TEST-043 | Removal from one Business Account preserves other memberships |
| TEST-044 | AUTHORISER may promote MEMBER to AUTHORISER |
| TEST-045 | AUTHORISER may remove MEMBER |
| TEST-046 | AUTHORISER may remove another AUTHORISER only when another remains |
| TEST-047 | Final AUTHORISER removal is rejected |
| TEST-048 | AUTHORISER-to-MEMBER demotion is rejected |
| TEST-049 | Removed user immediately loses access |
| TEST-050 | Access Audit History records creation, invitations, acceptances, role assignments, promotions, and removals |
| TEST-051 | Transaction History contains completed financial movements only |
| TEST-052 | Approval History contains Business outgoing workflow records |
| TEST-053 | Access Audit History is separate from Transaction History and Approval History |
| TEST-054 | Unauthorised account, history, membership, approval, and financial operation access is denied |
| TEST-055 | Midnight Ledger registration choice, navigation, role-aware controls, forms, confirmations, accessibility, and narrow-width usability |

## Superseded Traceability Notice

Any previous traceability entries mapping Business approval to a linked Personal Account, an authorised Personal Account field, exactly one Business authoriser, or same-user Personal/Business transfer rejection are superseded. `/speckit.tasks` must regenerate task-level traceability from this document and the v2.0.0 plan.
