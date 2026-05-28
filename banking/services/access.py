from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from banking.models import AccessAuditEvent, BusinessEmployeeAccess, PersonalAccount

from . import PermissionDeniedError, ValidationBankingError
from .access_audit import create_access_audit_event


def require_personal_owner(actor, personal_account):
    if not getattr(actor, "is_authenticated", False) or actor.login_context != "PERSONAL":
        raise PermissionDeniedError("Personal access is required.")
    if personal_account.owner_id != actor.id:
        raise PermissionDeniedError("Only the Personal Account owner may perform this action.")
    return personal_account


def get_current_business_access(actor):
    if not getattr(actor, "is_authenticated", False) or actor.login_context != "BUSINESS_EMPLOYEE":
        raise PermissionDeniedError("Business Employee access is required.")
    try:
        return actor.business_access
    except BusinessEmployeeAccess.DoesNotExist:
        raise PermissionDeniedError("Business Employee access is required.")


def require_active_employee(actor, business_account=None):
    access = get_current_business_access(actor)
    if access.access_status == BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED:
        raise PermissionDeniedError("Password change is required before accessing Business Account functions.")
    if access.access_status == BusinessEmployeeAccess.DEACTIVATED:
        raise PermissionDeniedError("Business Employee access is deactivated.")
    if business_account is not None and access.business_account_id != business_account.id:
        raise PermissionDeniedError("This employee access is scoped to a different Business Account.")
    return access


def require_authoriser(actor, business_account=None):
    access = require_active_employee(actor, business_account)
    if access.role != BusinessEmployeeAccess.AUTHORISER:
        raise PermissionDeniedError("AUTHORISER access is required.")
    return access


def active_authoriser_count(business_account, exclude_access=None):
    qs = business_account.employee_accesses.filter(
        role=BusinessEmployeeAccess.AUTHORISER,
        access_status=BusinessEmployeeAccess.ACTIVE,
    )
    if exclude_access is not None:
        qs = qs.exclude(pk=exclude_access.pk)
    return qs.count()


def ensure_not_final_authoriser(target_access):
    if target_access.role == BusinessEmployeeAccess.AUTHORISER and active_authoriser_count(target_access.business_account, target_access) < 1:
        raise ValidationBankingError("The final active AUTHORISER cannot be deactivated.")


def team_access_summary(actor):
    access = require_active_employee(actor)
    account = access.business_account
    roster = account.employee_accesses.select_related("user").order_by("user__username", "user__email")
    return {
        "account": account,
        "access": access,
        "employees": roster,
        "active_count": roster.filter(access_status=BusinessEmployeeAccess.ACTIVE).count(),
        "authoriser_count": roster.filter(
            role=BusinessEmployeeAccess.AUTHORISER,
            access_status=BusinessEmployeeAccess.ACTIVE,
        ).count(),
        "password_change_required_count": roster.filter(access_status=BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED).count(),
        "deactivated_count": roster.filter(access_status=BusinessEmployeeAccess.DEACTIVATED).count(),
    }


@transaction.atomic
def provision_employee_access(actor, display_name, email, role, temporary_password):
    authoriser = require_authoriser(actor)
    if role not in {BusinessEmployeeAccess.MEMBER, BusinessEmployeeAccess.AUTHORISER}:
        raise ValidationBankingError("Choose MEMBER or AUTHORISER.")
    User = get_user_model()
    normalized_email = User.objects.normalize_email(email).lower()
    if User.objects.filter(email__iexact=normalized_email).exists():
        raise ValidationBankingError("An account with this email address already exists.")
    user = User.objects.create_user(
        email=normalized_email,
        username=display_name.strip(),
        password=temporary_password,
        login_context=User.BUSINESS_EMPLOYEE,
    )
    access = BusinessEmployeeAccess.objects.create(
        user=user,
        business_account=authoriser.business_account,
        role=role,
        access_status=BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED,
    )
    create_access_audit_event(
        business_account=authoriser.business_account,
        acting_employee=authoriser,
        affected_employee=access,
        event_type=AccessAuditEvent.EMPLOYEE_ACCESS_CREATED,
        new_role=role,
        new_status=BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED,
        safe_metadata=f"Employee access created for {user.email}.",
    )
    create_access_audit_event(
        business_account=authoriser.business_account,
        acting_employee=authoriser,
        affected_employee=access,
        event_type=AccessAuditEvent.TEMPORARY_PASSWORD_ISSUED,
        new_status=BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED,
        safe_metadata=f"Temporary credential issued for {user.email}.",
    )
    return access


@transaction.atomic
def complete_mandatory_password_change(actor, new_password):
    access = get_current_business_access(actor)
    if access.access_status != BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED:
        raise ValidationBankingError("Password change is not required for this employee access.")
    actor.set_password(new_password)
    actor.save(update_fields=["password"])
    access.access_status = BusinessEmployeeAccess.ACTIVE
    access.activated_at = timezone.now()
    access.save(update_fields=["access_status", "activated_at"])
    create_access_audit_event(
        business_account=access.business_account,
        acting_employee=access,
        affected_employee=access,
        event_type=AccessAuditEvent.PASSWORD_CHANGE_COMPLETED,
        previous_status=BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED,
        new_status=BusinessEmployeeAccess.ACTIVE,
        safe_metadata=f"Employee {actor.email} completed mandatory credential change.",
    )
    create_access_audit_event(
        business_account=access.business_account,
        acting_employee=access,
        affected_employee=access,
        event_type=AccessAuditEvent.EMPLOYEE_ACTIVATED,
        previous_status=BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED,
        new_status=BusinessEmployeeAccess.ACTIVE,
        safe_metadata=f"Employee {actor.email} activated access.",
    )
    return access


@transaction.atomic
def reset_employee_temporary_password(actor, target_access, temporary_password):
    authoriser = require_authoriser(actor, target_access.business_account)
    target = BusinessEmployeeAccess.objects.select_for_update().select_related("user", "business_account").get(pk=target_access.pk)
    if target.pk == authoriser.pk:
        raise ValidationBankingError("Administrative self-reset is outside MVP scope.")
    target.user.set_password(temporary_password)
    target.user.save(update_fields=["password"])
    old_status = target.access_status
    target.access_status = BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED
    target.save(update_fields=["access_status"])
    create_access_audit_event(
        business_account=target.business_account,
        acting_employee=authoriser,
        affected_employee=target,
        event_type=AccessAuditEvent.TEMPORARY_PASSWORD_RESET,
        previous_status=old_status,
        new_status=BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED,
        safe_metadata=f"Temporary credential reset for {target.user.email}.",
    )
    return target


@transaction.atomic
def promote_member_to_authoriser(actor, target_access):
    authoriser = require_authoriser(actor, target_access.business_account)
    target = BusinessEmployeeAccess.objects.select_for_update().get(pk=target_access.pk)
    if target.role == BusinessEmployeeAccess.AUTHORISER:
        raise ValidationBankingError("Employee is already an AUTHORISER.")
    old_role = target.role
    target.role = BusinessEmployeeAccess.AUTHORISER
    target.save(update_fields=["role"])
    create_access_audit_event(
        business_account=target.business_account,
        acting_employee=authoriser,
        affected_employee=target,
        event_type=AccessAuditEvent.MEMBER_PROMOTED_TO_AUTHORISER,
        previous_role=old_role,
        new_role=target.role,
        safe_metadata=f"Employee {target.user.email} promoted to AUTHORISER.",
    )
    return target


def deactivate_employee_access(actor, target_access):
    authoriser = require_authoriser(actor, target_access.business_account)
    target = BusinessEmployeeAccess.objects.select_for_update().get(pk=target_access.pk)
    try:
        ensure_not_final_authoriser(target)
    except ValidationBankingError:
        create_access_audit_event(
            business_account=target.business_account,
            acting_employee=authoriser,
            affected_employee=target,
            event_type=AccessAuditEvent.FINAL_AUTHORISER_DEACTIVATION_REJECTED,
            outcome=AccessAuditEvent.REJECTED,
            previous_status=target.access_status,
            new_status=target.access_status,
            safe_metadata=f"Rejected final AUTHORISER deactivation for {target.user.email}.",
        )
        raise
    if target.pk == authoriser.pk:
        raise ValidationBankingError("An AUTHORISER cannot deactivate their own access in this MVP.")
    old_status = target.access_status
    target.access_status = BusinessEmployeeAccess.DEACTIVATED
    target.deactivated_at = timezone.now()
    target.deactivated_by = authoriser
    target.save(update_fields=["access_status", "deactivated_at", "deactivated_by"])
    create_access_audit_event(
        business_account=target.business_account,
        acting_employee=authoriser,
        affected_employee=target,
        event_type=AccessAuditEvent.EMPLOYEE_DEACTIVATED,
        previous_status=old_status,
        new_status=BusinessEmployeeAccess.DEACTIVATED,
        safe_metadata=f"Employee {target.user.email} deactivated.",
    )
    return target


@transaction.atomic
def reactivate_employee_access(actor, target_access, temporary_password):
    authoriser = require_authoriser(actor, target_access.business_account)
    target = BusinessEmployeeAccess.objects.select_for_update().select_related("user").get(pk=target_access.pk)
    if target.access_status != BusinessEmployeeAccess.DEACTIVATED:
        raise ValidationBankingError("Only deactivated employee access can be reactivated.")
    target.user.set_password(temporary_password)
    target.user.save(update_fields=["password"])
    target.access_status = BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED
    target.reactivated_at = timezone.now()
    target.save(update_fields=["access_status", "reactivated_at"])
    create_access_audit_event(
        business_account=target.business_account,
        acting_employee=authoriser,
        affected_employee=target,
        event_type=AccessAuditEvent.EMPLOYEE_REACTIVATED,
        previous_status=BusinessEmployeeAccess.DEACTIVATED,
        new_status=BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED,
        safe_metadata=f"Employee {target.user.email} reactivated.",
    )
    create_access_audit_event(
        business_account=target.business_account,
        acting_employee=authoriser,
        affected_employee=target,
        event_type=AccessAuditEvent.TEMPORARY_PASSWORD_ISSUED,
        new_status=BusinessEmployeeAccess.PASSWORD_CHANGE_REQUIRED,
        safe_metadata=f"Temporary credential issued for reactivated employee {target.user.email}.",
    )
    return target
