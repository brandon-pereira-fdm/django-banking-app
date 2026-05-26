class BankingError(Exception):
    """Safe domain error that can be shown to users."""


class PermissionDeniedError(BankingError):
    pass


class ValidationBankingError(BankingError):
    pass


from .accounts import (  # noqa: E402,F401
    deposit_business,
    deposit_personal,
    register_business_creator,
    register_personal_user,
    withdraw_personal,
)
from .approvals import (  # noqa: E402,F401
    approve_request,
    cancel_request,
    reject_request,
    request_business_transfer,
    request_business_withdrawal,
)
from .invitations import accept_invitation, create_invitation, register_business_user_from_invitation  # noqa: E402,F401
from .memberships import (  # noqa: E402,F401
    get_active_membership,
    promote_member,
    remove_membership,
    require_authoriser,
    require_business_membership,
    require_personal_owner,
)
from .money import format_sgd, mask_identifier, normalize_phone, normalize_uen, validate_sgd_amount  # noqa: E402,F401
from .transfers import preview_transfer_recipient, resolve_transfer_recipient, transfer_from_personal  # noqa: E402,F401
