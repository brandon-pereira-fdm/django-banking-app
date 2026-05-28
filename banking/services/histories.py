from .access import require_active_employee, require_personal_owner


def personal_transactions(actor):
    account = actor.personal_account
    require_personal_owner(actor, account)
    return account.completed_transactions.select_related("transfer_operation", "actor_user")


def business_transactions(actor):
    access = require_active_employee(actor)
    return access.business_account.completed_transactions.select_related("transfer_operation", "actor_user")


def business_approval_history(actor):
    access = require_active_employee(actor)
    return access.business_account.outgoing_requests.select_related("requested_by__user", "actioned_by__user")


def business_access_audit_history(actor):
    access = require_active_employee(actor)
    return access.business_account.access_audit_events.select_related("acting_employee__user", "affected_employee__user")
