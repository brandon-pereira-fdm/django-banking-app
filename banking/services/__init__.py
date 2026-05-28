class BankingError(Exception):
    """Safe domain error that can be shown to users."""


class PermissionDeniedError(BankingError):
    pass


class ValidationBankingError(BankingError):
    pass


from .accounts import deposit_business, deposit_personal, withdraw_personal  # noqa: E402,F401
from .access import (  # noqa: E402,F401
    complete_mandatory_password_change,
    deactivate_employee_access,
    get_current_business_access,
    promote_member_to_authoriser,
    provision_employee_access,
    reactivate_employee_access,
    require_active_employee,
    require_authoriser,
    require_personal_owner,
    reset_employee_temporary_password,
    team_access_summary,
)
from .approvals import (  # noqa: E402,F401
    approve_business_request,
    cancel_business_request,
    reject_business_request,
    submit_business_transfer_request,
    submit_business_withdrawal_request,
)
from .money import format_sgd, mask_identifier, normalize_phone, normalize_uen, validate_sgd_amount  # noqa: E402,F401
from .registration import register_business_account, register_personal_account  # noqa: E402,F401
from .transfers import preview_transfer_recipient, resolve_transfer_recipient, transfer_from_personal  # noqa: E402,F401
