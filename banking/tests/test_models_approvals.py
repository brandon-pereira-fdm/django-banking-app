from django.test import TestCase

from banking.models import ApprovalRequest


class ApprovalRequestModelTests(TestCase):
    def test_status_choices_exclude_approved(self):
        statuses = [choice[0] for choice in ApprovalRequest.STATUSES]
        self.assertEqual(statuses, ["PENDING", "COMPLETED", "REJECTED", "CANCELLED", "FAILED"])
        self.assertNotIn("APPROVED", statuses)
