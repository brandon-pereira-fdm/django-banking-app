from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from users.permissions import active_business_employee_required, personal_required

from .forms import AddEmployeeAccessForm, AmountForm, ResolutionForm, TemporaryPasswordForm, TransferForm
from .models import BusinessEmployeeAccess, BusinessOutgoingRequest
from .services import (
    BankingError,
    approve_business_request,
    cancel_business_request,
    deactivate_employee_access,
    deposit_business,
    deposit_personal,
    promote_member_to_authoriser,
    provision_employee_access,
    reactivate_employee_access,
    reject_business_request,
    reset_employee_temporary_password,
    submit_business_transfer_request,
    submit_business_withdrawal_request,
    team_access_summary,
    transfer_from_personal,
    withdraw_personal,
)
from .services.histories import business_access_audit_history, business_approval_history, business_transactions, personal_transactions


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("account_type_selection")
    if request.user.login_context == "PERSONAL":
        return redirect("personal_dashboard")
    return redirect("business_dashboard")


@personal_required
def personal_dashboard(request):
    account = request.user.personal_account
    transactions = account.completed_transactions.all()[:5]
    return render(request, "banking/personal_dashboard.html", {"account": account, "transactions": transactions})


@personal_required
def personal_account_detail(request):
    return render(request, "banking/personal_account.html", {"account": request.user.personal_account})


@personal_required
@require_http_methods(["GET", "POST"])
def personal_deposit(request):
    form = AmountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            tx = deposit_personal(request.user, request.user.personal_account, form.cleaned_data["amount"])
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            return render(request, "banking/result.html", {"title": "Deposit completed", "transaction": tx})
    return render(request, "banking/amount_form.html", {"form": form, "title": "Deposit", "scope": "Personal", "base_template": "base_personal.html"})


@personal_required
@require_http_methods(["GET", "POST"])
def personal_withdraw(request):
    form = AmountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            tx = withdraw_personal(request.user, request.user.personal_account, form.cleaned_data["amount"])
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            return render(request, "banking/result.html", {"title": "Withdrawal completed", "transaction": tx})
    return render(request, "banking/amount_form.html", {"form": form, "title": "Withdraw", "scope": "Personal", "base_template": "base_personal.html"})


@personal_required
@require_http_methods(["GET", "POST"])
def personal_transfer(request):
    form = TransferForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            transfer, debit, credit = transfer_from_personal(
                request.user,
                request.user.personal_account,
                form.cleaned_data["recipient_type"],
                form.cleaned_data["recipient_identifier"],
                form.cleaned_data["amount"],
            )
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            return render(
                request,
                "banking/transfer_result.html",
                {"transfer": transfer, "debit": debit, "credit": credit, "title": "Transfer completed"},
            )
    return render(request, "banking/transfer_form.html", {"form": form, "title": "Transfer", "scope": "Personal"})


@personal_required
def personal_transaction_history(request):
    return render(
        request,
        "banking/transaction_history.html",
        {"transactions": personal_transactions(request.user), "scope": "Personal", "base_template": "base_personal.html"},
    )


@active_business_employee_required
def business_dashboard(request):
    access = request.business_access
    account = access.business_account
    pending_count = account.outgoing_requests.filter(status=BusinessOutgoingRequest.PENDING).count()
    recent_transactions = account.completed_transactions.all()[:5]
    recent_requests = account.outgoing_requests.select_related("requested_by__user", "actioned_by__user")[:5]
    summary = team_access_summary(request.user) if access.role == BusinessEmployeeAccess.AUTHORISER else None
    return render(
        request,
        "banking/business_dashboard.html",
        {
            "account": account,
            "access": access,
            "pending_count": pending_count,
            "recent_transactions": recent_transactions,
            "recent_requests": recent_requests,
            "team_summary": summary,
        },
    )


@active_business_employee_required
@require_http_methods(["GET", "POST"])
def business_deposit(request):
    account = request.business_account
    form = AmountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            tx = deposit_business(request.user, account, form.cleaned_data["amount"])
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            return render(request, "banking/result.html", {"title": "Business deposit completed", "transaction": tx, "account": account})
    return render(request, "banking/amount_form.html", {"form": form, "title": "Business Deposit", "scope": "Business", "account": account, "base_template": "base_business.html"})


@active_business_employee_required
@require_http_methods(["GET", "POST"])
def business_withdraw_request(request):
    account = request.business_account
    form = AmountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            approval = submit_business_withdrawal_request(request.user, account, form.cleaned_data["amount"])
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            return render(request, "banking/request_result.html", {"title": "Withdrawal request pending", "approval": approval, "account": account})
    return render(request, "banking/amount_form.html", {"form": form, "title": "Request Withdrawal", "scope": "Business", "account": account, "base_template": "base_business.html"})


@active_business_employee_required
@require_http_methods(["GET", "POST"])
def business_transfer_request(request):
    account = request.business_account
    form = TransferForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            approval = submit_business_transfer_request(
                request.user,
                account,
                form.cleaned_data["recipient_type"],
                form.cleaned_data["recipient_identifier"],
                form.cleaned_data["amount"],
            )
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            return render(request, "banking/request_result.html", {"title": "Transfer request pending", "approval": approval, "account": account})
    return render(request, "banking/transfer_form.html", {"form": form, "title": "Request Transfer", "scope": "Business", "account": account, "base_template": "base_business.html"})


@active_business_employee_required
def approvals_list(request):
    approvals = request.business_account.outgoing_requests.select_related("requested_by__user", "actioned_by__user")
    return render(request, "banking/approvals.html", {"account": request.business_account, "access": request.business_access, "approvals": approvals})


@active_business_employee_required
def approvals_detail(request, request_id):
    approval = get_object_or_404(request.business_account.outgoing_requests, request_id=request_id)
    return render(request, "banking/approval_detail.html", {"account": request.business_account, "access": request.business_access, "approval": approval})


@active_business_employee_required
@require_POST
def approval_action(request, request_id, action):
    approval = get_object_or_404(request.business_account.outgoing_requests, request_id=request_id)
    form = ResolutionForm(request.POST or None)
    if form.is_valid():
        try:
            if action == "approve":
                approve_business_request(request.user, approval)
            elif action == "reject":
                reject_business_request(request.user, approval, form.cleaned_data.get("reason") or "Rejected by AUTHORISER.")
            elif action == "cancel":
                cancel_business_request(request.user, approval)
            else:
                raise BankingError("Unsupported approval action.")
            messages.success(request, "Request updated.")
        except BankingError as exc:
            messages.error(request, str(exc))
    return redirect("approvals_detail", request_id=approval.request_id)


@active_business_employee_required
def team_access(request):
    context = team_access_summary(request.user)
    return render(request, "banking/team_access.html", context)


@active_business_employee_required
@require_http_methods(["GET", "POST"])
def add_employee_access(request):
    if request.business_access.role != BusinessEmployeeAccess.AUTHORISER:
        raise PermissionDenied("AUTHORISER access is required.")
    form = AddEmployeeAccessForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            access = provision_employee_access(
                request.user,
                form.cleaned_data["display_name"],
                form.cleaned_data["email"],
                form.cleaned_data["role"],
                form.cleaned_data["temporary_password1"],
            )
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            return render(request, "banking/add_employee_access_success.html", {"employee_access": access})
    return render(request, "banking/add_employee_access.html", {"form": form, "account": request.business_account})


def _target_access(request, access_id):
    return get_object_or_404(request.business_account.employee_accesses.select_related("user"), access_id=access_id)


@active_business_employee_required
@require_http_methods(["GET", "POST"])
def reset_employee_password(request, access_id):
    target = _target_access(request, access_id)
    form = TemporaryPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            reset_employee_temporary_password(request.user, target, form.cleaned_data["temporary_password1"])
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Temporary password reset. Employee must change it before normal access.")
            return redirect("team_access")
    return render(request, "banking/reset_employee_password.html", {"form": form, "target": target})


@active_business_employee_required
@require_POST
def promote_employee(request, access_id):
    try:
        promote_member_to_authoriser(request.user, _target_access(request, access_id))
        messages.success(request, "Employee promoted to AUTHORISER.")
    except BankingError as exc:
        messages.error(request, str(exc))
    return redirect("team_access")


@active_business_employee_required
@require_POST
def deactivate_employee(request, access_id):
    try:
        deactivate_employee_access(request.user, _target_access(request, access_id))
        messages.success(request, "Employee access deactivated.")
    except BankingError as exc:
        messages.error(request, str(exc))
    return redirect("team_access")


@active_business_employee_required
@require_http_methods(["GET", "POST"])
def reactivate_employee(request, access_id):
    target = _target_access(request, access_id)
    form = TemporaryPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            reactivate_employee_access(request.user, target, form.cleaned_data["temporary_password1"])
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Employee access reactivated. Password change is required.")
            return redirect("team_access")
    return render(request, "banking/reactivate_employee.html", {"form": form, "target": target})


@active_business_employee_required
def business_transaction_history(request):
    return render(
        request,
        "banking/transaction_history.html",
        {"account": request.business_account, "access": request.business_access, "transactions": business_transactions(request.user), "scope": "Business", "base_template": "base_business.html"},
    )


@active_business_employee_required
def approval_history(request):
    return render(
        request,
        "banking/approval_history.html",
        {"account": request.business_account, "access": request.business_access, "approvals": business_approval_history(request.user)},
    )


@active_business_employee_required
def access_audit(request):
    return render(
        request,
        "banking/access_audit_history.html",
        {"account": request.business_account, "access": request.business_access, "events": business_access_audit_history(request.user)},
    )
