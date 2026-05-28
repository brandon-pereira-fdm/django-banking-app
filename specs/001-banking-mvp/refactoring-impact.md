# Refactoring Impact: Banking MVP Constitution v3.0.0

## Superseded Model Assessment

Constitution v3.0.0 supersedes the v2 invitation-and-membership implementation where employees accepted invitations, a Business login could hold multiple Business memberships, and the UI included a Business Account selector. It also keeps superseded all pre-v2 Personal-Account-authorises-Business-Account behavior.

## Affected Existing Paths

The repository currently contains implementation files that may reflect superseded v2 behavior and must be inspected/refactored before new v3 work:

- `banking/models.py`: invitation, membership, and access-state assumptions must be replaced with `BusinessEmployeeAccess`.
- `banking/forms.py`: invitation and multi-membership forms must be replaced with Team Access forms.
- `banking/views.py` and `banking/urls.py`: invitation routes, selector routes, and invitation acceptance must be removed/replaced.
- `banking/services/invitations.py`: superseded; replace with employee provisioning/password reset services.
- `banking/services/memberships.py`: multi-Business membership logic is superseded; replace with one-account employee access governance.
- `banking/tests/test_invitations_memberships.py`: superseded tests must be replaced by employee access, password, deactivation, and reactivation tests.
- `templates/users/register_business_invited.html`: superseded invitation registration page.
- Business navigation/templates: remove `Invitations`; add `Team Access` or `Access Control`; remove Business Account selector.
- `banking/migrations/0001_initial.py`, `banking/migrations/0002_initial.py`, and local SQLite state: likely v2 development schema and subject to local reset/replacement strategy.

## Required Replacement

- Replace invitation issuance/acceptance with AUTHORISER-created employee access credentials.
- Replace `BusinessMembership` multi-account semantics with `BusinessEmployeeAccess` one-account semantics.
- Replace invitation audit events with access-security events for employee creation, temporary password issuance/reset, password change activation, promotion, deactivation, reactivation, and final-AUTHORISER rejection.
- Replace Business Account selector with direct access to the employee's assigned Business Account.
- Preserve completed financial transaction, transfer, approval, retained-minimum, and history-separation rules where not contradicted by v3.

## Local Database and Migration Strategy

The project is a local learning MVP with no approved production data preservation requirement.

Preferred implementation strategy:

1. Do not preserve obsolete local SQLite data.
2. Remove or replace superseded uncommitted development migrations where safe.
3. Reset local SQLite database before applying v3 migrations.
4. Generate fresh v3 migrations during implementation.
5. Regenerate test data through tests or setup functions.

If later repository policy requires preserving committed migrations, use a forward-migration strategy instead and explicitly map removed invitation/membership structures to the new employee access model.

## Baseline Verification Required Before Implementation

Implementation tasks must verify:

- no active Personal-Account-authorises-Business-Account behavior remains;
- no active invitation access flow remains;
- no Business Employee login can access multiple Business Accounts;
- no Business Account selector remains active;
- no persisted `APPROVED` status exists;
- no access-management workflow deletes employee access records through ordinary UI;
- no password values or password hashes are displayed or stored in audit events.

## Implementation Completion Notes

The v3 implementation replaced the active invitation and multi-membership runtime surface:

- `BusinessInvitation` and `BusinessMembership` models were replaced by `BusinessEmployeeAccess`.
- Invitation services, invitation routes, invitation templates, invitation registration, and membership services were removed.
- Business navigation now uses Team Access and no Business Account selector route remains active.
- Fresh local-development migrations were generated for the v3 schema and the ignored local SQLite database was reset before applying them.
- Searches across active `users/`, `banking/`, `templates/`, and `static/` paths found no active invitation implementation labels or routes after refactoring; remaining old-model terms only appear in negative regression assertions.
