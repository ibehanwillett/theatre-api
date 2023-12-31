from flask_jwt_extended import get_jwt_identity
from flask import abort
from models.user import User
from config import db

def authorize(accessed_id):
    current_user = get_jwt_identity()
    stmt = db.select(User).filter_by(id=current_user)
    user = db.session.scalar(stmt)
    if not (user.is_admin or (user.id and current_user == accessed_id)):
        abort(401,  description='User unauthorized to perform this action')

def authorize_committee(accessed_id):
    current_user = get_jwt_identity()
    stmt = db.select(User).filter_by(id=current_user)
    user = db.session.scalar(stmt)
    if not (user.is_admin or (user.is_committee or (user.id and current_user == accessed_id))):
        abort(401, description='User unauthorized to perform this action.')

def admin_or_committee_only():
    current_user = get_jwt_identity()
    stmt = db.select(User).filter_by(id=current_user)
    user = db.session.scalar(stmt)
    if not (user.is_admin or (user.is_committee)):
        abort(401, description='Invalid action. User must be an administrator or committee member.')

def admin_only():
    current_user = get_jwt_identity()
    stmt = db.select(User).filter_by(id=current_user)
    user = db.session.scalar(stmt)
    if not user.is_admin:
        abort(401, description='Invalid action. User must be an administrator.')
