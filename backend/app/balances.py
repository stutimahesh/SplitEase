from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from .models import Expense, GroupMember, User
from .utils import require_member

balances_bp = Blueprint("balances", __name__)


@balances_bp.route("/groups/<int:group_id>/balances", methods=["GET"])
@jwt_required()
def get_balances(group_id):
    user_id = int(get_jwt_identity())
    require_member(group_id, user_id)

    net_balances = _calculate_net_balances(group_id)
    users = {u.id: u.to_dict() for u in User.query.filter(User.id.in_(net_balances.keys()))}

    result = [
        {"user": users[uid], "balance": round(balance, 2)}
        for uid, balance in net_balances.items()
    ]
    return jsonify(result)


@balances_bp.route("/groups/<int:group_id>/settle-up", methods=["GET"])
@jwt_required()
def get_settle_up(group_id):
    user_id = int(get_jwt_identity())
    require_member(group_id, user_id)

    net_balances = _calculate_net_balances(group_id)
    transactions = _minimize_transactions(net_balances)

    users = {u.id: u.to_dict() for u in User.query.filter(User.id.in_(net_balances.keys()))}
    result = [
        {
            "from": users[t["from"]],
            "to": users[t["to"]],
            "amount": round(t["amount"], 2),
        }
        for t in transactions
    ]
    return jsonify(result)


def _minimize_transactions(net_balances):
    """Greedily match the largest creditor with the largest debtor until every
    balance is zero. This minimizes the number of payments needed to settle
    the group, instead of everyone paying back every individual expense.
    """
    creditors = sorted(
        ([uid, amt] for uid, amt in net_balances.items() if amt > 0.01),
        key=lambda x: -x[1],
    )
    debtors = sorted(
        ([uid, -amt] for uid, amt in net_balances.items() if amt < -0.01),
        key=lambda x: -x[1],
    )

    transactions = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor_id, debt_amt = debtors[i]
        creditor_id, credit_amt = creditors[j]
        settled = min(debt_amt, credit_amt)

        transactions.append({"from": debtor_id, "to": creditor_id, "amount": settled})

        debtors[i][1] -= settled
        creditors[j][1] -= settled

        if debtors[i][1] < 0.01:
            i += 1
        if creditors[j][1] < 0.01:
            j += 1

    return transactions


def _calculate_net_balances(group_id):
    """net balance = total the member paid - total of their own split shares.

    Positive means the group owes them money, negative means they owe the group.
    """
    members = GroupMember.query.filter_by(group_id=group_id).all()
    balances = {m.user_id: 0.0 for m in members}

    expenses = Expense.query.filter_by(group_id=group_id).all()
    for expense in expenses:
        balances[expense.paid_by] = balances.get(expense.paid_by, 0.0) + expense.amount
        for split in expense.splits:
            balances[split.user_id] = balances.get(split.user_id, 0.0) - split.amount_owed

    return balances
