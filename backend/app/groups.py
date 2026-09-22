from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .extensions import db
from .models import Group, GroupMember, User
from .utils import require_member

groups_bp = Blueprint("groups", __name__)


@groups_bp.route("", methods=["POST"])
@jwt_required()
def create_group():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    name = data.get("name")
    member_emails = data.get("member_emails", [])

    if not name:
        return jsonify({"error": "group name is required"}), 400

    group = Group(name=name, created_by=user_id)
    db.session.add(group)
    db.session.flush()

    db.session.add(GroupMember(group_id=group.id, user_id=user_id))

    for email in member_emails:
        member = User.query.filter_by(email=email).first()
        if member and member.id != user_id:
            db.session.add(GroupMember(group_id=group.id, user_id=member.id))

    db.session.commit()
    return jsonify(group.to_dict()), 201


@groups_bp.route("", methods=["GET"])
@jwt_required()
def list_groups():
    user_id = int(get_jwt_identity())
    memberships = GroupMember.query.filter_by(user_id=user_id).all()
    return jsonify([m.group.to_dict() for m in memberships])


@groups_bp.route("/<int:group_id>", methods=["GET"])
@jwt_required()
def get_group(group_id):
    user_id = int(get_jwt_identity())
    require_member(group_id, user_id)

    group = Group.query.get_or_404(group_id)
    members = GroupMember.query.filter_by(group_id=group_id).all()

    data = group.to_dict()
    data["members"] = [m.user.to_dict() for m in members]
    return jsonify(data)


@groups_bp.route("/<int:group_id>/members", methods=["POST"])
@jwt_required()
def add_member(group_id):
    user_id = int(get_jwt_identity())
    require_member(group_id, user_id)

    data = request.get_json() or {}
    email = data.get("email")
    member = User.query.filter_by(email=email).first()
    if not member:
        return jsonify({"error": "no user found with that email"}), 404

    existing = GroupMember.query.filter_by(group_id=group_id, user_id=member.id).first()
    if existing:
        return jsonify({"error": "user is already a member"}), 409

    db.session.add(GroupMember(group_id=group_id, user_id=member.id))
    db.session.commit()
    return jsonify(member.to_dict()), 201
