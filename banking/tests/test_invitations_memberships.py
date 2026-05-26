from django.test import TestCase

from banking.models import BusinessAccessAuditEvent, BusinessInvitation, BusinessMembership
from banking.services import (
    PermissionDeniedError,
    ValidationBankingError,
    accept_invitation,
    create_invitation,
    promote_member,
    remove_membership,
)
from banking.tests.factories import business_account, business_user, membership, personal_account, personal_user


class InvitationAndMembershipTests(TestCase):
    def test_invitation_acceptance_and_personal_rejection(self):
        authoriser = business_user("auth@example.com")
        account = business_account()
        membership(authoriser, account, BusinessMembership.AUTHORISER)
        invite = create_invitation(authoriser, account, "invitee@example.com", BusinessMembership.MEMBER)
        self.assertEqual(invite.status, BusinessInvitation.PENDING)
        self.assertEqual(account.memberships.filter(user__email="invitee@example.com", is_active=True).count(), 0)
        invitee = business_user("invitee@example.com")
        accepted = accept_invitation(invitee, invite)
        self.assertEqual(accepted.role, BusinessMembership.MEMBER)
        invite.refresh_from_db()
        self.assertEqual(invite.status, BusinessInvitation.ACCEPTED)
        p_user = personal_user("p@example.com")
        personal_account(p_user, phone="+6590002222")
        second = create_invitation(authoriser, account, "p@example.com", BusinessMembership.MEMBER)
        with self.assertRaises(PermissionDeniedError):
            accept_invitation(p_user, second)

    def test_member_cannot_invite_or_manage_and_last_authoriser_protected(self):
        authoriser = business_user("auth@example.com")
        member = business_user("member@example.com")
        account = business_account()
        auth_membership = membership(authoriser, account, BusinessMembership.AUTHORISER)
        member_membership = membership(member, account, BusinessMembership.MEMBER)
        with self.assertRaises(PermissionDeniedError):
            create_invitation(member, account, "x@example.com", BusinessMembership.MEMBER)
        with self.assertRaises(PermissionDeniedError):
            promote_member(member, member_membership)
        promote_member(authoriser, member_membership)
        member_membership.refresh_from_db()
        self.assertEqual(member_membership.role, BusinessMembership.AUTHORISER)
        remove_membership(authoriser, member_membership)
        member_membership.refresh_from_db()
        self.assertFalse(member_membership.is_active)
        with self.assertRaises(ValidationBankingError):
            remove_membership(authoriser, auth_membership)
        self.assertTrue(BusinessAccessAuditEvent.objects.filter(event_type=BusinessAccessAuditEvent.LAST_AUTHORISER_REMOVAL_REJECTED).exists())
