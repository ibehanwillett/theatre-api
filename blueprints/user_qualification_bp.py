from flask import Blueprint, request
from config import db
from models.user_qualification import UserQualification, UserQualificationSchema
from auth import *
import datetime
from flask_jwt_extended import jwt_required
userqualifications_bp = Blueprint('userqualification', __name__, url_prefix='/users/qualifications')


#Give a user a new qualification
@userqualifications_bp.route("/", methods=["POST"])
@jwt_required()
def register_qualification():
    admin_or_committee_only()
    userqualification_info = UserQualificationSchema().load(request.json)
    check = check_preexisting_qualification(userqualification_info["user_id"], userqualification_info["qualification_id"])
    if check:
        abort(406, description='Record already exists.')
    userqualification = UserQualification(
        user_id=userqualification_info["user_id"],
        qualification_id=userqualification_info["qualification_id"],
    )
    db.session.add(userqualification)
    db.session.commit()
    return UserQualificationSchema().dump(userqualification), 201

# Update the last refresher for a qualification
@userqualifications_bp.route('/<int:user_id>/<int:qualification_id>', methods=['PUT','PATCH'])
@jwt_required()
def update_userqualification(user_id,qualification_id):
    userqualification_info = UserQualificationSchema().load(request.json)
    userqualification = check_preexisting_qualification(user_id, qualification_id)
    if userqualification: 
        admin_or_committee_only()
        userqualification.last_refresher = userqualification_info.get('last_refresher', datetime.datetime.now())
        db.session.commit()
        return UserQualificationSchema().dump(userqualification)
    else:
        return {'Error': 'Qualification cannot be found for that user'}

# Return a list of all users with specific qualification
@userqualifications_bp.route('/<int:qualification_id>')
@jwt_required()
def all_users_qualified(qualification_id):
    admin_or_committee_only()
    stmt = db.select(UserQualification).where(UserQualification.qualification_id==qualification_id)
    qualified_users = db.session.scalars(stmt).all()
    if qualified_users:
        return UserQualificationSchema(many=True).dump(qualified_users), 200
    else:
        return {'Error': 'No records found.'},404


#Delete a user's qualifications
@userqualifications_bp.route('/<int:user_id>/<int:qualification_id>', methods=['DELETE'])
@jwt_required()
def delete_userqualification(user_id,qualification_id):
    # userqualification_info = UserQualificationSchema().load(request.json)
    userqualification = check_preexisting_qualification(user_id,qualification_id)
    if userqualification:
        admin_or_committee_only()
        db.session.delete(userqualification)
        db.session.commit()
        return {'Success': 'Qualification deleted successfully'}, 200
    else:
        return {'Error':'User/Qualification combo not found'}, 404
    

def check_preexisting_qualification(user_id, qualification_id):
    stmt = db.select(UserQualification).where(UserQualification.user_id==user_id,UserQualification.qualification_id==qualification_id)
    record = db.session.scalar(stmt)
    return record
