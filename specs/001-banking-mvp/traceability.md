# Traceability: Banking MVP Constitution v3.0.0

This map links v3 specification requirements to planned components and tests. Task IDs will be finalized after `/speckit.tasks` is regenerated.

## Requirement to Component and Test Map

| Requirement IDs | Planned Component(s) | Planned Test Coverage |
|---|---|---|
| FR-001 to FR-010, BR-007 to BR-011, SEC-001 to SEC-003 | `users.CustomUser`, login context guards, auth views/forms | TEST-001 to TEST-006, TEST-011 |
| FR-011 to FR-020, BR-012 to BR-015 | `PersonalAccount`, Personal registration service, Personal pages | TEST-007 to TEST-008, TEST-036, TEST-039 to TEST-042 |
| FR-021 to FR-031, BR-016 to BR-020 | `BusinessAccount`, `BusinessEmployeeAccess`, opening transaction, Access Audit events | TEST-002, TEST-009 to TEST-010 |
| FR-032 to FR-047, BR-021 to BR-027, SEC-004 to SEC-006 | `BusinessEmployeeAccess`, Team Access services/forms/views, password-change/reset services | TEST-012 to TEST-024, TEST-034 to TEST-035 |
| FR-048 to FR-066, SEC-006 to SEC-013 | role permission helpers, Team Access admin services, deactivation/reactivation, audit | TEST-025 to TEST-033, TEST-050, TEST-061 to TEST-062, TEST-066 to TEST-067 |
| FR-067 to FR-075, BR-039 to BR-042 | recipient resolution service, transfer forms/views, `TransferOperation` | TEST-043 to TEST-046 |
| FR-076 to FR-086, BR-030 to BR-038 | `BusinessOutgoingRequest`, request/approval services, approval pages | TEST-047 to TEST-060 |
| FR-087 to FR-091, BR-001 to BR-006, BR-043 to BR-044, NFR-004 | money validation, transaction services, completed transaction records | TEST-036 to TEST-046, TEST-059 to TEST-060 |
| FR-092 to FR-097, BR-045 to BR-046 | Transaction History, Approval History, Access Audit History pages/queries | TEST-061 to TEST-067 |
| UX-001 to UX-029, NFR-006 | Django templates, custom CSS, navigation shells, reusable UI components | TEST-068 to TEST-069 plus manual UI checks |
| NFR-001 to NFR-009 | governance, atomicity, traceability docs, services, test suite | All TEST identifiers |

## Planned Test Module Mapping

| Test Module | Primary Coverage |
|---|---|
| `users/tests/test_authentication.py` | FR-002 to FR-005, TEST-003, TEST-011 |
| `users/tests/test_access_context.py` | FR-006 to FR-010, SEC-002 to SEC-003, TEST-004 to TEST-006 |
| `banking/tests/test_personal_registration.py` | FR-011 to FR-015, TEST-001, TEST-007 to TEST-008 |
| `banking/tests/test_business_registration.py` | FR-021 to FR-031, TEST-002, TEST-009 to TEST-010 |
| `banking/tests/test_employee_access.py` | FR-032 to FR-043, TEST-012 to TEST-020, TEST-034 to TEST-035 |
| `banking/tests/test_password_workflows.py` | FR-041 to FR-047, TEST-018 to TEST-024 |
| `banking/tests/test_team_access.py` | FR-048 to FR-066, TEST-025 to TEST-033, TEST-061 |
| `banking/tests/test_money_validation.py` | BR-001 to BR-006, TEST-038 |
| `banking/tests/test_deposits_withdrawals.py` | FR-016 to FR-020, FR-049, TEST-036 to TEST-040 |
| `banking/tests/test_recipient_resolution.py` | FR-067 to FR-072, TEST-043 to TEST-045 |
| `banking/tests/test_transfers.py` | FR-073 to FR-075, FR-087 to FR-091, TEST-041 to TEST-046 |
| `banking/tests/test_business_requests.py` | FR-075 to FR-079, TEST-047 to TEST-049 |
| `banking/tests/test_approvals.py` | FR-080 to FR-086, TEST-050 to TEST-057, TEST-059 to TEST-060 |
| `banking/tests/test_multiple_pending.py` | FR-077 to FR-082, TEST-058 to TEST-060 |
| `banking/tests/test_histories.py` | FR-092 to FR-097, TEST-061 to TEST-067 |
| `banking/tests/test_ui_permissions.py` | UX-001 to UX-029, TEST-068 to TEST-069 |

## Superseded Traceability Notice

The following v2 or earlier requirements are not active and must not receive implementation tasks:

- Personal Account authorises Business Account.
- Business access through invitations or invitation acceptance.
- One Business login has memberships in multiple Business Accounts.
- Business Account selector for employee logins.
- Invitation-specific registration.
- Shared Business credentials.
- Deleting employee access records through ordinary workflows.
- Exactly one AUTHORISER only.
- Persisted `APPROVED` status.

These are replaced by `BusinessEmployeeAccess`, Team Access provisioning, mandatory password change, password reset, deactivation/reactivation, and Access Audit events under constitution v3.0.0.
