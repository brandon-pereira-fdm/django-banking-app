from django.db import transaction
from django.utils import timezone

from banking.models import BusinessAccessAuditEvent, BusinessMembership

from . import PermissionDeniedError, ValidationBankingError


def require_personal_owner(user, personal_account):
    if not getattr(user, "is_authenticated", False) or user.access_context != "PERSONAL":
        raise PermissionDeniedError("Personal access is required.")
    if personal_account.owner_id != user.id:
        raise PermissionDeniedError("Only the Personal Account owner may perform this action.")
    return personal_account


def get_active_membership(user, business_account):
    if not getattr(user, "is_authenticated", False) or user.access_context != "BUSINESS":
        return None
    return (
        BusinessMembership.objects.select_related("business_account", "user")
        .filter(user=user, business_account=business_account, is_active=True)
        .first()
    )


def require_business_membership(user, business_account):
    membership = get_active_membership(user, business_account)
    if membership is None:
        raise PermissionDeniedError("Active Business membership is required.")
    return membership


def require_authoriser(user, business_account):
    membership = require_business_membership(user, business_account)
    if membership.role != BusinessMembership.AUTHORISER:
        raise PermissionDeniedError("AUTHORISER access is required.")
    return membership


def active_authoriser_count(business_account):
    return BusinessMembership.objects.filter(
        business_account=business_account,
        is_active=True,
        role=BusinessMembership.AUTHORISER,
    ).count()


def ensure_last_authoriser_not_removed(target_membership):
    if target_membership.role != BusinessMembership.AUTHORISER:
        return
    remaining = BusinessMembership.objects.filter(
        business_account=target_membership.business_account,
        is_active=True,
        role=BusinessMembership.AUTHORISER,
    ).exclude(pk=target_membership.pk).count()
    if remaining < 1:
        raise ValidationBankingError("The final AUTHORISER cannot be removed.")


@transaction.atomic
def promote_member(actor, target_membership):
    acting_membership = require_authoriser(actor, target_membership.business_account)
    target_membership = BusinessMembership.objects.select_for_update().get(pk=target_membership.pk)
    if not target_membership.is_active:
        raise ValidationBankingError("Removed members cannot be promoted.")
    if target_membership.role == BusinessMembership.AUTHORISER:
        raise ValidationBankingError("AUTHORISER demotion is unsupported in the MVP.")
    target_membership.role = BusinessMembership.AUTHORISER
    target_membership.save(update_fields=["role"])
    BusinessAccessAuditEvent.objects.create(
        business_account=target_membership.business_account,
        acting_user=acting_membership.user,
        affected_user=target_membership.user,
        role=BusinessMembership.AUTHORISER,
        event_type=BusinessAccessAuditEvent.MEMBER_PROMOTED_TO_AUTHORISER,
        details="Member promoted to AUTHORISER.",
    )
    return target_membership


def remove_membership(actor, target_membership):
    acting_membership = require_authoriser(actor, target_membership.business_account)
    target_membership = BusinessMembership.objects.get(pk=target_membership.pk)
    if not target_membership.is_active:
        raise ValidationBankingError("Membership is already removed.")
    try:
        ensure_last_authoriser_not_removed(target_membership)
    except ValidationBankingError:
        BusinessAccessAuditEvent.objects.create(
            business_account=target_membership.business_account,
            acting_user=acting_membership.user,
            affected_user=target_membership.user,
            role=target_membership.role,
            event_type=BusinessAccessAuditEvent.LAST_AUTHORISER_REMOVAL_REJECTED,
            outcome=BusinessAccessAuditEvent.REJECTED,
            details="Attempted removal would leave no AUTHORISER.",
        )
        raise
    with transaction.atomic():
        target_membership = BusinessMembership.objects.select_for_update().get(pk=target_membership.pk)
        target_membership.is_active = False
        target_membership.removed_at = timezone.now()
        target_membership.save(update_fields=["is_active", "removed_at"])
        event_type = (
            BusinessAccessAuditEvent.AUTHORISER_REMOVED
            if target_membership.role == BusinessMembership.AUTHORISER
            else BusinessAccessAuditEvent.MEMBER_REMOVED
        )
        BusinessAccessAuditEvent.objects.create(
            business_account=target_membership.business_account,
            acting_user=acting_membership.user,
            affected_user=target_membership.user,
            role=target_membership.role,
            event_type=event_type,
            details="Membership removed.",
        )
    return target_membership


def reject_demote_authoriser():
    raise ValidationBankingError("AUTHORISER demotion to MEMBER is unsupported in the MVP.")
