from decimal import Decimal

from django.test import TestCase

from banking.models import BankAccount, CompletedTransaction
from banking.services import BankingError, create_business_account, create_personal_account
from .helpers import make_business, make_user


class BusinessAccountTests(TestCase):
    def test_create_at_exactly_7000_and_above_links_own_personal(self):
        user = make_user()
        personal = create_personal_account(user, "91234567")
        business, tx = create_business_account(user, "Acme", "202612345A", Decimal("7000.00"))
        self.assertEqual(business.balance, Decimal("7000.00"))
        self.assertEqual(business.authorised_personal_account, personal)
        self.assertEqual(tx.transaction_type, CompletedTransaction.BUSINESS_OPENING_DEPOSIT)

        user2 = make_user("two@example.com", "Two")
        create_personal_account(user2, "92345678")
        business2, _ = create_business_account(user2, "Beta", "202612346B", Decimal("8000.00"))
        self.assertEqual(business2.balance, Decimal("8000.00"))

    def test_creation_rejections(self):
        user = make_user()
        with self.assertRaises(BankingError):
            create_business_account(user, "No Personal", "202612345A", Decimal("7000.00"))
        create_personal_account(user, "91234567")
        with self.assertRaises(BankingError):
            create_business_account(user, "", "202612345A", Decimal("7000.00"))
        with self.assertRaises(BankingError):
            create_business_account(user, "Low", "202612345A", Decimal("6999.99"))
        create_business_account(user, "Acme", "202612345A", Decimal("7000.00"))
        other = make_user("other@example.com", "Other")
        create_personal_account(other, "92345678")
        with self.assertRaises(BankingError):
            create_business_account(other, "Dup", "202612345A", Decimal("7000.00"))
