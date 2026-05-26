from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from users.permissions import business_required, personal_required

from .forms import AmountForm, InvitationForm, ResolutionForm, TransferForm
from .models import (
    BusinessAccessAuditEvent,
    BusinessAccount,
    BusinessApprovalRequest,
    BusinessInvitation,
    BusinessMembership,
    CompletedFinancialTransaction,
)
from .services import (
    BankingError,
    accept_invitation,
    approve_request,
    cancel_request,
    create_invitation,
    deposit_business,
    deposit_personal,
    get_active_membership,
    promote_member,
    reject_request,
    remove_membership,
    request_business_transfer,
    request_business_withdrawal,
    require_authoriser,
    require_business_membership,
    transfer_from_personal,
    withdraw_personal,
)


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("account_type_selection")
    if request.user.access_context == "PERSONAL":
        return redirect("personal_dashboard")
    return redirect("business_home")


@personal_required
def personal_dashboard(request):
    account = request.user.personal_account
    transactions = account.completed_transactions.all()[:5]
    return render(request, "banking/personal/dashboard.html", {"account": account, "transactions": transactions})


@personal_required
def personal_account_detail(request):
    return render(request, "banking/personal/detail.html", {"account": request.user.personal_account})


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
            return render(request, "banking/personal/result.html", {"title": "Deposit completed", "transaction": tx})
    return render(request, "banking/personal/amount_form.html", {"form": form, "title": "Deposit"})


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
            return render(request, "banking/personal/result.html", {"title": "Withdrawal completed", "transaction": tx})
    return render(request, "banking/personal/amount_form.html", {"form": form, "title": "Withdraw"})


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
                "banking/transfers/result.html",
                {"transfer": transfer, "debit": debit, "credit": credit, "title": "Transfer completed"},
            )
    return render(request, "banking/transfers/form.html", {"form": form, "title": "Transfer"})


@personal_required
def personal_transactions(request):
    account = request.user.personal_account
    transactions = account.completed_transactions.select_related("transfer_operation")
    return render(request, "banking/histories/transactions.html", {"transactions": transactions, "scope": "Personal"})


@business_required
def business_home(request):
    memberships = BusinessMembership.objects.select_related("business_account").filter(user=request.user, is_active=True)
    if memberships.count() == 1:
        return redirect("business_dashboard", account_id=memberships.first().business_account.account_id)
    return render(request, "banking/business/selector.html", {"memberships": memberships})


def _business_context(request, account_id):
    account = get_object_or_404(BusinessAccount, account_id=account_id)
    membership = get_active_membership(request.user, account)
    if membership is None:
        raise PermissionDenied("Active Business membership is required.")
    return account, membership


@business_required
def business_dashboard(request, account_id):
    account, membership = _business_context(request, account_id)
    pending_count = account.approval_requests.filter(status=BusinessApprovalRequest.PENDING).count()
    recent_transactions = account.completed_transactions.all()[:5]
    recent_requests = account.approval_requests.all()[:5]
    return render(
        request,
        "banking/business/dashboard.html",
        {
            "account": account,
            "membership": membership,
            "pending_count": pending_count,
            "recent_transactions": recent_transactions,
            "recent_requests": recent_requests,
        },
    )


@business_required
@require_http_methods(["GET", "POST"])
def business_deposit(request, account_id):
    account, membership = _business_context(request, account_id)
    form = AmountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            tx = deposit_business(request.user, account, form.cleaned_data["amount"])
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            return render(request, "banking/business/result.html", {"title": "Business deposit completed", "transaction": tx, "account": account})
    return render(request, "banking/business/amount_form.html", {"form": form, "title": "Business Deposit", "account": account, "membership": membership})


@business_required
@require_http_methods(["GET", "POST"])
def business_withdraw_request(request, account_id):
    account, membership = _business_context(request, account_id)
    form = AmountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            approval = request_business_withdrawal(request.user, account, form.cleaned_data["amount"])
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            return render(request, "banking/approvals/result.html", {"title": "Withdrawal request pending", "approval": approval, "account": account})
    return render(request, "banking/business/amount_form.html", {"form": form, "title": "Request Withdrawal", "account": account, "membership": membership})


@business_required
@require_http_methods(["GET", "POST"])
def business_transfer_request(request, account_id):
    account, membership = _business_context(request, account_id)
    form = TransferForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            approval = request_business_transfer(
                request.user,
                account,
                form.cleaned_data["recipient_type"],
                form.cleaned_data["recipient_identifier"],
                form.cleaned_data["amount"],
            )
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            return render(request, "banking/approvals/result.html", {"title": "Transfer request pending", "approval": approval, "account": account})
    return render(request, "banking/transfers/form.html", {"form": form, "title": "Request Transfer", "account": account, "membership": membership})


@business_required
def approvals_list(request, account_id):
    account, membership = _business_context(request, account_id)
    approvals = account.approval_requests.select_related("requested_by", "actioned_by")
    return render(request, "banking/approvals/list.html", {"account": account, "membership": membership, "approvals": approvals})


@business_required
def approvals_detail(request, account_id, request_id):
    account, membership = _business_context(request, account_id)
    approval = get_object_or_404(account.approval_requests, request_id=request_id)
    return render(request, "banking/approvals/detail.html", {"account": account, "membership": membership, "approval": approval})


@business_required
@require_POST
def approval_action(request, account_id, request_id, action):
    account, membership = _business_context(request, account_id)
    approval = get_object_or_404(account.approval_requests, request_id=request_id)
    form = ResolutionForm(request.POST or None)
    if form.is_valid():
        try:
            if action == "approve":
                approve_request(request.user, approval)
            elif action == "reject":
                reject_request(request.user, approval, form.cleaned_data.get("reason") or "Rejected by AUTHORISER.")
            elif action == "cancel":
                cancel_request(request.user, approval)
            else:
                raise BankingError("Unsupported approval action.")
            messages.success(request, "Request updated.")
        except BankingError as exc:
            messages.error(request, str(exc))
    return redirect("approvals_detail", account_id=account.account_id, request_id=approval.request_id)


@business_required
@require_http_methods(["GET", "POST"])
def invitations(request, account_id):
    account, membership = _business_context(request, account_id)
    form = InvitationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            create_invitation(request.user, account, form.cleaned_data["invited_email"], form.cleaned_data["intended_role"])
        except BankingError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Invitation stored.")
            return redirect("business_invitations", account_id=account.account_id)
    items = account.invitations.select_related("accepted_by")
    return render(request, "banking/invitations/list.html", {"account": account, "membership": membership, "form": form, "invitations": items})


@business_required
@require_http_methods(["GET", "POST"])
def accept_invitation_view(request, invitation_id):
    invitation = get_object_or_404(BusinessInvitation, invitation_id=invitation_id)
    if request.method == "POST":
        try:
            membership = accept_invitation(request.user, invitation)
        except BankingError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "Invitation accepted.")
            return redirect("business_dashboard", account_id=membership.business_account.account_id)
    return render(request, "banking/invitations/accept.html", {"invitation": invitation})


@business_required
def members(request, account_id):
    account, membership = _business_context(request, account_id)
    roster = account.memberships.select_related("user").filter(is_active=True)
    return render(request, "banking/members/list.html", {"account": account, "membership": membership, "memberships": roster})


@business_required
@require_POST
def member_action(request, account_id, membership_id, action):
    account, membership = _business_context(request, account_id)
    target = get_object_or_404(account.memberships.select_related("user"), membership_id=membership_id)
    try:
        if action == "promote":
            promote_member(request.user, target)
        elif action == "remove":
            remove_membership(request.user, target)
        else:
            raise BankingError("Unsupported membership action.")
        messages.success(request, "Membership updated.")
    except BankingError as exc:
        messages.error(request, str(exc))
    return redirect("business_members", account_id=account.account_id)


@business_required
def business_transactions(request, account_id):
    account, membership = _business_context(request, account_id)
    transactions = account.completed_transactions.select_related("transfer_operation", "actor_user")
    return render(request, "banking/histories/transactions.html", {"account": account, "membership": membership, "transactions": transactions, "scope": "Business"})


@business_required
def approval_history(request, account_id):
    account, membership = _business_context(request, account_id)
    approvals = account.approval_requests.select_related("requested_by", "actioned_by")
    return render(request, "banking/histories/approvals.html", {"account": account, "membership": membership, "approvals": approvals})


@business_required
def access_audit(request, account_id):
    account, membership = _business_context(request, account_id)
    events = account.access_audit_events.select_related("acting_user", "affected_user")
    return render(request, "banking/histories/access_audit.html", {"account": account, "membership": membership, "events": events})
