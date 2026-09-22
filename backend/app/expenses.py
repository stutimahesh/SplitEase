from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .extensions import db
from .models import Expense, ExpenseSplit, GroupMember
from .utils import require_member

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/groups/<int:group_id>/expenses", methods=["POST"])
@jwt_required()
def add_expense(group_id):
    user_id = int(get_jwt_identity())
    require_member(group_id, user_id)

    data = request.get_json() or {}
    amount = data.get("amount")
    description = data.get("description")
    paid_by = data.get("paid_by", user_id)
    custom_splits = data.get("splits")  # optional: [{user_id, amount_owed}, ...]

    if not amount or not description:
        return jsonify({"error": "amount and description are required"}), 400

    members = GroupMember.query.filter_by(group_id=group_id).all()
    member_ids = [m.user_id for m in members]

    if custom_splits:
        total_split = sum(float(s["amount_owed"]) for s in custom_splits)
        if round(total_split, 2) != round(float(amount), 2):
            return jsonify({"error": "splits must add up to the total amount"}), 400
        splits = custom_splits
    else:
        share = round(float(amount) / len(member_ids), 2)
        splits = [{"user_id": uid, "amount_owed": share} for uid in member_ids]

    expense = Expense(
        group_id=group_id, paid_by=paid_by, amount=amount, description=description
    )
    db.session.add(expense)
    db.session.flush()

    for s in splits:
        db.session.add(
            ExpenseSplit(
                expense_id=expense.id,
                user_id=s["user_id"],
                amount_owed=s["amount_owed"],
            )
        )

    db.session.commit()
    return jsonify(expense.to_dict()), 201


@expenses_bp.route("/groups/<int:group_id>/expenses", methods=["GET"])
@jwt_required()
def list_expenses(group_id):
    user_id = int(get_jwt_identity())
    require_member(group_id, user_id)

    expenses = (
        Expense.query.filter_by(group_id=group_id)
        .order_by(Expense.created_at.desc())
        .all()
    )
    return jsonify([e.to_dict() for e in expenses])
