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
