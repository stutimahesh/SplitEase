from flask import abort

from .models import GroupMember


def require_member(group_id, user_id):
    """Abort with 403 unless user_id is a member of group_id, else return the membership row."""
    membership = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not membership:
        abort(403, description="not a member of this group")
    return membership
