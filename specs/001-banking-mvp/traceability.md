# Traceability Plan: Banking MVP

## Component Map

| Requirement Area | Planned Component(s) | Test Focus |
|------------------|----------------------|------------|
| Registration and authentication | `users.models`, `users.forms`, `users.views`, templates | `TEST-008`, `TEST-009`, `TEST-041`, `TEST-046` |
| Personal Account creation | `banking.models`, `banking.forms`, `banking.services.create_personal_account`, account templates | `TEST-001`, `TEST-002`, `TEST-003` |
| Business Account creation | `banking.models`, `banking.forms`, `banking.services.create_business_account`, Business setup template | `TEST-004`, `TEST-005`, `TEST-006`, `TEST-007`, `TEST-047` |
| Money validation | `banking.forms`, `banking.services`, model constraints | `TEST-010`, `TEST-011`, `TEST-012`, `TEST-026` |
| Deposits | `banking.services.deposit`, deposit views/templates | `TEST-010`, `TEST-036`, `TEST-038` |
| Personal withdrawals | `banking.services.withdraw_personal`, withdrawal views/templates | `TEST-013`, `TEST-014`, `TEST-036`, `TEST-038` |
| Business withdrawal approval | `banking.services.request_business_withdrawal`, `approve_request`, approval views/templates | `TEST-017`, `TEST-018`, `TEST-019`, `TEST-039`, `TEST-040` |
| Recipient lookup | `banking.services.resolve_transfer_recipient`, transfer forms/views/templates | `TEST-020`, `TEST-021`, `TEST-022`, `TEST-023`, `TEST-024`, `TEST-025` |
| Personal transfers | `TransferOperation`, `CompletedTransaction`, `banking.services.transfer_from_personal` | `TEST-015`, `TEST-016`, `TEST-027`, `TEST-028`, `TEST-036`, `TEST-037`, `TEST-038` |
| Business transfer approval | `ApprovalRequest`, `banking.services.request_business_transfer`, `approve_request` | `TEST-029`, `TEST-030`, `TEST-031`, `TEST-034`, `TEST-035`, `TEST-040` |
| Multiple PENDING requests | `ApprovalRequest`, `banking.services.approve_request`, approval history templates | `TEST-032`, `TEST-033`, `TEST-034`, `TEST-044` |
| Transaction history | `CompletedTransaction`, transaction views/templates | `TEST-036`, `TEST-037`, `TEST-042`, `TEST-043`, `TEST-050` |
| Access control | `users` auth, `banking.views`, `banking.services` permission checks | `TEST-039`, `TEST-041` |
| Midnight Ledger UI | shared templates, custom CSS, UI fragments | `TEST-045`, `TEST-046`, `TEST-047`, `TEST-048`, `TEST-049`, `TEST-050`, `TEST-051`, `TEST-052`, `TEST-053` |

## Requirement-to-Test Mapping

| Spec IDs | Planned Tests |
|----------|---------------|
| `FR-001` to `FR-005`, `SEC-001` to `SEC-003` | `TEST-008`, `TEST-009`, `TEST-041`, `TEST-046` |
| `FR-006` to `FR-010`, `BR-008` to `BR-011` | `TEST-001`, `TEST-002`, `TEST-003` |
| `FR-011` to `FR-015`, `BR-001` to `BR-010` | `TEST-010` to `TEST-016`, `TEST-026`, `TEST-038` |
| `FR-016` to `FR-026`, `BR-012` to `BR-017` | `TEST-004` to `TEST-007`, `TEST-047` |
| `FR-027` to `FR-030`, `BR-018` to `BR-020` | `TEST-017` to `TEST-019`, `TEST-029` to `TEST-031` |
| `FR-031` to `FR-042`, `BR-021` to `BR-027` | `TEST-032` to `TEST-035`, `TEST-039`, `TEST-040`, `TEST-044` |
| `FR-043` to `FR-051`, `BR-028` to `BR-033` | `TEST-020` to `TEST-028`, `TEST-048` |
| `FR-052` to `FR-055`, `BR-034` to `BR-037` | `TEST-036`, `TEST-037`, `TEST-038` |
| `FR-056` to `FR-063`, `BR-038` to `BR-039` | `TEST-042`, `TEST-043`, `TEST-044`, `TEST-050` |
| `FR-064` to `FR-065`, `NFR-003`, `NFR-004` | `TEST-011`, `TEST-012`, `TEST-014`, `TEST-016`, `TEST-019`, `TEST-022` to `TEST-024`, `TEST-026` to `TEST-030`, `TEST-034`, `TEST-038`, `TEST-051` |
| `SEC-004` to `SEC-007` | `TEST-025`, `TEST-039`, `TEST-041` |
| `UX-001` to `UX-027`, `NFR-006` to `NFR-016` | `TEST-045` to `TEST-053` |

## Mandatory Constitution Cases

- Personal Account transfer lookup by phone number: `TEST-020`.
- Business Account transfer lookup by UEN: `TEST-021`.
- Duplicate UEN rejection: `TEST-007`.
- Recipient type and identifier mismatch rejection: `TEST-024`.
- Safe recipient confirmation: `TEST-025`.
- Multiple PENDING Business requests: `TEST-032`.
- No fund reservation while PENDING: `TEST-033`.
- PENDING request becomes FAILED after retained-minimum revalidation fails:
  `TEST-034`.
- Absence of persisted APPROVED status: `TEST-035`.

## Planning Traceability Commitments

- Every implementation task generated later must reference one or more
  requirement IDs or test IDs.
- Every service-level banking rule must have direct tests.
- Every completed financial movement path must test both balance result and
  completed transaction record creation.
- Every failed, rejected, cancelled, or PENDING path must test unchanged
  balances and absence of completed financial movement records.
