from django.core.exceptions import ValidationError

from banking.models import AccessAuditEvent


def create_access_audit_event(
    *,
    business_account,
    event_type,
    acting_employee=None,
    affected_employee=None,
    previous_role="",
    new_role="",
    previous_status="",
    new_status="",
    outcome=AccessAuditEvent.SUCCESS,
    safe_metadata="",
):
    event = AccessAuditEvent(
        business_account=business_account,
        acting_employee=acting_employee,
        affected_employee=affected_employee,
        event_type=event_type,
        previous_role=previous_role or "",
        new_role=new_role or "",
        previous_status=previous_status or "",
        new_status=new_status or "",
        outcome=outcome,
        safe_metadata=safe_metadata or "",
    )
    if any(word in event.safe_metadata.lower() for word in ("password", "hash", "secret")):
        raise ValidationError("Access Audit History must not include password or secret values.")
    event.full_clean()
    event.save()
    return event
