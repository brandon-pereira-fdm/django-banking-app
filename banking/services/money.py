from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from . import ValidationBankingError


MIN_BUSINESS_BALANCE = Decimal("7000.00")
ZERO_MONEY = Decimal("0.00")
MAX_MONEY = Decimal("9999999999.99")
TWOPLACES = Decimal("0.01")


def validate_sgd_amount(value):
    if isinstance(value, str):
        raw = value.strip().replace(",", "")
    else:
        raw = value
    try:
        amount = Decimal(raw)
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationBankingError("Enter a valid SGD amount.")
    if amount.is_nan() or amount.is_infinite():
        raise ValidationBankingError("Enter a valid SGD amount.")
    if amount <= ZERO_MONEY:
        raise ValidationBankingError("Amount must be greater than SGD 0.00.")
    if amount > MAX_MONEY:
        raise ValidationBankingError("Amount exceeds the supported limit.")
    if amount.as_tuple().exponent < -2:
        raise ValidationBankingError("Amounts may use no more than two decimal places.")
    return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def format_sgd(value):
    amount = Decimal(value).quantize(TWOPLACES)
    return f"SGD {amount:,.2f}"


def normalize_phone(value):
    return "".join(ch for ch in (value or "").strip() if ch.isdigit() or ch == "+")


def normalize_uen(value):
    return (value or "").strip().upper().replace(" ", "")


def mask_identifier(value):
    value = value or ""
    if len(value) <= 4:
        return value
    return f"{value[:2]}...{value[-2:]}"
