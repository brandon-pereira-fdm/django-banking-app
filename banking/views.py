from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import (
    AccountAmountForm,
    ApprovalActionForm,
    ApprovalFilterForm,
    BusinessAccountForm,
    DepositForm,
    PersonalAccountForm,
    TransactionFilterForm,
    TransferStartForm,
)
from .models import ApprovalRequest, BankAccount, CompletedTransaction
from .services import (
    BankingError,
    PermissionDeniedError,
    approval_requests_for_user,
    approve_request,
    cancel_request,
    completed_transactions_for_user,
    create_business_account,
    create_personal_account,
    deposit,
    format_sgd,
    preview_transfer,
    reject_request,
    request_business_transfer,
    request_business_withdrawal,
    transfer_from_personal,
    user_business_account,
    user_personal_account,
    withdraw_personal,
)


def _recent_transactions(user, limit=6):
    return completed_transactions_for_user(user)[:limit]


@login_required
def dashboard(request):
    personal = user_personal_account(request.user)
    business = user_business_account(request.user)
    pending_count = 0
    if business:
        pending_count = business.approval_requests.filter(status=ApprovalRequest.PENDING).count()
    return render(
        request,
        "banking/dashboard.html",
        {
            "personal": personal,
            "business": business,
            "recent_transactions": _recent_transactions(request.user),
            "pending_count": pending_count,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def personal_setup(request):
    if user_personal_account(request.user):
        return redirect("personal_detail")
    form = PersonalAccountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            create_personal_account(request.user, form.cleaned_data["phone_number"])
            messages.success(request, "Personal Account opened with balance SGD 0.00.")
            return redirect("personal_detail")
        except BankingError as exc:
            form.add_error(None, str(exc))
    return render(request, "banking/personal_setup.html", {"form": form})


@login_required
def personal_detail(request):
    personal = user_personal_account(request.user)
    if not personal:
        return redirect("personal_setup")
    return render(
        request,
        "banking/personal_detail.html",
        {"account": personal, "transactions": personal.transactions.all()[:8]},
    )


@login_required
@require_http_methods(["GET", "POST"])
def business_setup(request):
    if user_business_account(request.user):
        return redirect("business_detail")
    if not user_personal_account(request.user):
        messages.info(request, "Open a Personal Account before opening a Business Account.")
        return redirect("personal_setup")
    form = BusinessAccountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            create_business_account(
                request.user,
                form.cleaned_data["business_display_name"],
                form.cleaned_data["uen"],
                form.cleaned_data["opening_deposit"],
            )
            messages.success(request, "Business Account opened and funded.")
            return redirect("business_detail")
        except BankingError as exc:
            form.add_error(None, str(exc))
    return render(request, "banking/business_setup.html", {"form": form})


@login_required
def business_detail(request):
    business = user_business_account(request.user)
    if not business:
        return render(request, "banking/business_empty.html")
    return render(
        request,
        "banking/business_detail.html",
        {
            "account": business,
            "transactions": business.transactions.all()[:8],
            "pending_requests": business.approval_requests.filter(status=ApprovalRequest.PENDING),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def deposit_view(request):
    form = DepositForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        if "confirm" not in request.POST:
            return render(request, "banking/deposit_confirm.html", {"form": form, "data": form.cleaned_data})
        try:
            tx = deposit(request.user, form.cleaned_data["account"], form.cleaned_data["amount"])
            return render(request, "banking/deposit_success.html", {"transaction": tx})
        except BankingError as exc:
            form.add_error(None, str(exc))
    return render(request, "banking/deposit_form.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def withdraw_view(request):
    form = AccountAmountForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        account = form.cleaned_data["account"]
        amount = form.cleaned_data["amount"]
        if "confirm" not in request.POST:
            return render(request, "banking/withdraw_confirm.html", {"form": form, "account": account, "amount": amount})
        try:
            if account.account_type == BankAccount.PERSONAL:
                tx = withdraw_personal(request.user, account, amount)
                return render(request, "banking/withdraw_success.html", {"transaction": tx})
            approval = request_business_withdrawal(request.user, account, amount)
            return render(request, "banking/withdraw_pending.html", {"approval": approval})
        except BankingError as exc:
            form.add_error(None, str(exc))
    return render(request, "banking/withdraw_form.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def transfer_view(request):
    form = TransferStartForm(request.POST or None, user=request.user)
    if request.method == "POST" and form.is_valid():
        source = form.cleaned_data["source_account"]
        recipient_type = form.cleaned_data["recipient_type"]
        identifier = form.cleaned_data["identifier"]
        amount = form.cleaned_data["amount"]
        try:
            preview = preview_transfer(request.user, source, recipient_type, identifier, amount)
            if "confirm" not in request.POST:
                return render(request, "banking/transfer_confirm.html", {"form": form, "preview": preview})
            if source.account_type == BankAccount.PERSONAL:
                op, debit, credit = transfer_from_personal(request.user, source, recipient_type, identifier, amount)
                return render(request, "banking/transfer_success.html", {"operation": op, "debit": debit, "credit": credit, "preview": preview})
            approval = request_business_transfer(request.user, source, recipient_type, identifier, amount)
            return render(request, "banking/transfer_pending.html", {"approval": approval, "preview": preview})
        except BankingError as exc:
            form.add_error(None, str(exc))
    return render(request, "banking/transfer_start.html", {"form": form})


@login_required
def approvals_list(request):
    form = ApprovalFilterForm(request.GET or None)
    requests = approval_requests_for_user(request.user)
    if form.is_valid() and form.cleaned_data.get("status"):
        requests = requests.filter(status=form.cleaned_data["status"])
    return render(request, "banking/approvals_list.html", {"form": form, "approval_requests": requests})


@login_required
@require_http_methods(["GET", "POST"])
def approval_detail(request, request_id):
    approval = get_object_or_404(ApprovalRequest.objects.select_related("business_account", "recipient_account", "authorised_personal_account"), request_id=request_id)
    can_view = approval.business_account.owner_id == request.user.id or approval.authorised_personal_account.owner_id == request.user.id
    if not can_view:
        return HttpResponseForbidden("You cannot view this approval request.")
    projected_balance = approval.business_account.balance - approval.amount
    form = ApprovalActionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            action = form.cleaned_data["action"]
            if action == ApprovalActionForm.ACTION_APPROVE:
                approve_request(approval, request.user)
            elif action == ApprovalActionForm.ACTION_REJECT:
                reject_request(approval, request.user)
            elif action == ApprovalActionForm.ACTION_CANCEL:
                cancel_request(approval, request.user)
            return redirect("approval_detail", request_id=approval.request_id)
        except PermissionDeniedError:
            return HttpResponseForbidden("You cannot action this approval request.")
        except BankingError as exc:
            messages.error(request, str(exc))
    return render(
        request,
        "banking/approvals_detail.html",
        {
            "approval": approval,
            "form": form,
            "projected_balance": projected_balance,
            "retained_minimum_ok": projected_balance >= 7000,
        },
    )


@login_required
def transactions_view(request):
    form = TransactionFilterForm(request.GET or None, user=request.user)
    transactions = completed_transactions_for_user(request.user)
    if form.is_valid():
        account = form.cleaned_data.get("account")
        transaction_type = form.cleaned_data.get("transaction_type")
        if account:
            transactions = transactions.filter(account=account)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
    return render(request, "banking/transactions.html", {"form": form, "transactions": transactions})
