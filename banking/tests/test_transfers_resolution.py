from decimal import Decimal

from django.test import TestCase

from banking.models import BankAccount
from banking.services import BankingError, resolve_transfer_recipient
from .helpers import make_business, make_personal, make_user


class TransferResolutionTests(TestCase):
    def setUp(self):
        self.sender_user = make_user()
        self.sender = make_personal(self.sender_user, "91234567", Decimal("100.00"))
        self.recipient = make_personal(make_user("p@example.com", "Personal"), "92345678")
        _, self.business, _ = make_business(make_user("b@example.com", "Business"), "93456789", "202612345A")

    def test_personal_by_phone_and_business_by_uen(self):
        self.assertEqual(resolve_transfer_recipient(self.sender, BankAccount.PERSONAL, "9234 5678"), self.recipient)
        self.assertEqual(resolve_transfer_recipient(self.sender, BankAccount.BUSINESS, "202612345a"), self.business)

    def test_unknown_mismatch_self_and_same_user_rejections(self):
        for recipient_type, identifier in [(BankAccount.PERSONAL, "99999999"), (BankAccount.BUSINESS, "UNKNOWN")]:
            with self.assertRaises(BankingError):
                resolve_transfer_recipient(self.sender, recipient_type, identifier)
        with self.assertRaises(BankingError):
            resolve_transfer_recipient(self.sender, BankAccount.PERSONAL, "202612345A")
        with self.assertRaises(BankingError):
            resolve_transfer_recipient(self.sender, BankAccount.BUSINESS, "92345678")
        with self.assertRaises(BankingError):
            resolve_transfer_recipient(self.sender, BankAccount.PERSONAL, "91234567")
        _, own_business, _ = make_business(self.sender_user, "94567890", "202612346B")
        with self.assertRaises(BankingError):
            resolve_transfer_recipient(self.sender, BankAccount.BUSINESS, own_business.uen)
