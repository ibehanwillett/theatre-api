from flask import Blueprint, request
from config import db
from models.user_qualification import UserQualification, UserQualificationSchema
from models.user import User, UserSchema

userqualifications_bp = Blueprint('userqualification', __name__, url_prefix='/user_qualifications')

# @userqualifications_bp.route('/<int:qualification_id>')
# def all_users_qualified(qualification_id):
#     stmt = db.select(UserQualification).where(UserQualification.qualification_id==qualification_id)
#     qualified_users = db.session.scalars(stmt).all()
#     return UserQualificationSchema(many=True).dump(qualified_users)

#Give a user a new qualification
@userqualifications_bp.route("/", methods=["POST"])
def register_qualification():
    userqualification_info = UserQualificationSchema().load(request.json)
    userqualification = UserQualification(
        user_id=userqualification_info["user_id"],
        qualification_id=userqualification_info["qualification_id"],
        last_refresher=userqualification_info.get("last_refresher"),
    )
    db.session.add(userqualification)
    db.session.commit()

    return UserQualificationSchema().dump(userqualification), 201
# Note to self- need to create error handler for this one

@userqualifications_bp.route('/<int:user_id/int:qualification_id>', methods=['PUT','PATCH'])
def update_userqualification(user_id,qualification_id):
    userqualification_info = UserQualificationSchema().load(request.json)
    stmt = db.select(UserQualification).filter_by(UserQualification.user_id==user_id,UserQualification.qualification_id==qualification_id)
    userqualification = db.session.scalar(stmt)
    if userqualification: 
        # authorisation here
        userqualification.last_refresher = userqualification_info.get('last_refresher', userqualification.last_refresher)
        db.session.commit()
        return UserSchema().dump(userqualification)
    else:
        return {'error': 'Qualification cannot be found for that user'}

# Return a list of all users with specific qualification
@userqualifications_bp.route('/<int:qualification_id>')
def all_users_qualified(qualification_id):
    stmt = db.select(User).join(UserQualification).where(UserQualification.qualification_id==qualification_id)
    qualified_users = db.session.scalars(stmt).all()
    return UserSchema(many=True, exclude=["id","password","is_admin","is_committee"]).dump(qualified_users)


#Delete a user's qualifications
@userqualifications_bp.route('/<int:user_id/int:qualification_id>', methods=['PUT','PATCH'])
def delete_userqualification(user_id,qualification_id):
    userqualification_info = UserQualificationSchema().load(request.json)
    stmt = db.select(UserQualification).filter_by(UserQualification.user_id==user_id,UserQualification.qualification_id==qualification_id)
    userqualification = db.session.scalar(stmt)
      if userqualification:
        # authorize(user.user_id)
        db.session.delete(userqualification)
        db.session.commit()
        return {'success': 'Qualification deleted successfully'}, 200
    else:
        return {'error':'User/Qualification combo not found'}, 404