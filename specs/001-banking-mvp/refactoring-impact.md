# Refactoring Impact: Banking MVP Constitution v2.0.0

## Superseded Model Assessment

The pre-version-2.0.0 implementation assumed one login could own both Personal and Business accounts, that a Personal Account could authorise a Business Account, and that Business outgoing approvals were performed by that authorised Personal Account. Those assumptions conflict with `BR-007`, `BR-014`, `BR-018`, `BR-036`, and `SC-024`.

## Affected Paths Found Before Reset

- `users/models.py` used a custom user without an exclusive `PERSONAL` or `BUSINESS` access context.
- `banking/models.py` used one `BankAccount` model with `owner`, `account_type`, and `authorised_personal_account` fields.
- `banking/services.py` required a Personal Account before Business creation, checked authorised Personal Account approval, and rejected same-user Personal/Business transfers.
- `banking/views.py`, `banking/forms.py`, and `templates/banking/` contained Business setup and approval language tied to the authorised-Personal-Account model.
- `banking/tests/` contained tests for exactly-one authorised Personal Account behavior and old approval permissions.
- `users/migrations/0001_initial.py`, `banking/migrations/0001_initial.py`, `banking/migrations/0002_initial.py`, and local `db.sqlite3` represented the superseded local schema.

## Reset Decision

The project is a local learning MVP with no approved production data preservation requirement. The approved approach is to remove the local SQLite database and obsolete generated migrations before creating fresh v2.0.0 migrations. No user data preservation assumption is introduced.

## Removal and Rewrite Targets

- Remove the `authorised_personal_account` field and any references to authorised Personal Account approval.
- Replace the old single `BankAccount` model with separate `PersonalAccount` and `BusinessAccount` records plus shared money-operation references.
- Replace single-owner Business access with `BusinessMembership`, `BusinessInvitation`, and `BusinessAccessAuditEvent`.
- Replace old approval permission logic with active `AUTHORISER` membership checks.
- Remove the superseded same-user Personal/Business transfer rejection. Transfers now reject only true self-transfers from an account to itself.
- Replace old tests, templates, and views with v2.0.0 behavior.

## Baseline Verification

The active checklists are `requirements-quality-v2.md` and `requirements.md`; both pass. The superseded pre-v2 checklist is archived outside the active checklist directory. The v2.0.0 implementation baseline is ready after fresh migrations are generated from the replacement model definitions.

## Post-Implementation Search Notes

Searches over `users/`, `banking/`, `templates/`, and `static/` found no remaining implementation references to the superseded `authorised_personal_account` field, Personal-Account-as-approver behavior, same-user Personal/Business transfer rejection, or old single `BankAccount` model. Remaining references to `BusinessApprovalRequest` and `CompletedFinancialTransaction` are v2.0.0 model names. Remaining `APPROVED` references in tests and approved artefacts assert that no persisted `APPROVED` status exists.
