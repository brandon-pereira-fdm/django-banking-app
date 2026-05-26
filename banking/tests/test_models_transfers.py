from decimal import Decimal
from uuid import UUID

from django.test import TestCase

from banking.services import transfer_from_personal
from .helpers import make_personal, make_user


class TransferOperationModelTests(TestCase):
    def test_transfer_operation_uuid_and_linked_records(self):
        user = make_user()
        sender = make_personal(user, "91234567", Decimal("20.00"))
        recipient = make_personal(make_user("r@example.com", "R"), "92345678")
        op, debit, credit = transfer_from_personal(user, sender, "PERSONAL", "92345678", Decimal("10.00"))
        self.assertIsInstance(op.transfer_operation_id, UUID)
        self.assertEqual(debit.transfer_operation, op)
        self.assertEqual(credit.transfer_operation, op)
