from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from banking.models import BusinessAccessAuditEvent, BusinessInvitation, BusinessMembership

from . import PermissionDeniedError, ValidationBankingError
from .memberships import require_authoriser


@transaction.atomic
def create_invitation(actor, business_account, invited_email, intended_role):
    authoriser_membership = require_authoriser(actor, business_account)
    invited_email = invited_email.strip().lower()
    if intended_role not in {BusinessMembership.MEMBER, BusinessMembership.AUTHORISER}:
        raise ValidationBankingError("Choose MEMBER or AUTHORISER.")
    if BusinessInvitation.objects.filter(
        business_account=business_account,
        invited_email__iexact=invited_email,
        status=BusinessInvitation.PENDING,
    ).exists():
        raise ValidationBankingError("A Pending invitation already exists for this email.")
    invitation = BusinessInvitation.objects.create(
        business_account=business_account,
        invited_email=invited_email,
        intended_role=intended_role,
        inviting_membership=authoriser_membership,
    )
    BusinessAccessAuditEvent.objects.create(
        business_account=business_account,
        acting_user=actor,
        invited_email=invited_email,
        role=intended_role,
        event_type=BusinessAccessAuditEvent.INVITATION_ISSUED,
        details="Invitation issued.",
    )
    return invitation


@transaction.atomic
def accept_invitation(actor, invitation):
    invitation = BusinessInvitation.objects.select_for_update().get(pk=invitation.pk)
    if invitation.status != BusinessInvitation.PENDING:
        raise ValidationBankingError("Only Pending invitations can be accepted.")
    if actor.access_context != "BUSINESS":
        raise PermissionDeniedError("Personal logins cannot accept Business invitations.")
    if actor.email.lower() != invitation.invited_email.lower():
        raise PermissionDeniedError("This invitation is addressed to a different email.")
    membership, created = BusinessMembership.objects.get_or_create(
        business_account=invitation.business_account,
        user=actor,
        is_active=True,
        defaults={"role": invitation.intended_role},
    )
    if not created:
        raise ValidationBankingError("This Business user already has active access.")
    invitation.status = BusinessInvitation.ACCEPTED
    invitation.accepted_at = timezone.now()
    invitation.accepted_by = actor
    invitation.save(update_fields=["status", "accepted_at", "accepted_by"])
    BusinessAccessAuditEvent.objects.create(
        business_account=invitation.business_account,
        acting_user=actor,
        affected_user=actor,
        invited_email=invitation.invited_email,
        role=invitation.intended_role,
        event_type=BusinessAccessAuditEvent.INVITATION_ACCEPTED,
        details="Invitation accepted and membership assigned.",
    )
    return membership


@transaction.atomic
def register_business_user_from_invitation(invitation, username, password):
    invitation = BusinessInvitation.objects.select_for_update().get(pk=invitation.pk)
    if invitation.status != BusinessInvitation.PENDING:
        raise ValidationBankingError("Only Pending invitations can be accepted.")
    User = get_user_model()
    user = User.objects.create_user(
        email=invitation.invited_email.lower(),
        username=username.strip(),
        password=password,
        access_context=User.BUSINESS,
    )
    membership = accept_invitation(user, invitation)
    return user, membership
