from flask import Blueprint, request
from config import db
from models.user_course import UserCourse, UserCourseSchema
from models.user import User, UserSchema
import datetime
from flask_jwt_extended import jwt_required
from auth import *

usercourses_bp = Blueprint('usercourse', __name__, url_prefix='/user_courses')

# @usercourses_bp.route('/<int:course_id>')
# def all_users_qualified(course_id):
#     stmt = db.select(usercourse).where(usercourse.course_id==course_id)
#     qualified_users = db.session.scalars(stmt).all()
#     return usercourseSchema(many=True).dump(qualified_users)

#Give a user a new course
@usercourses_bp.route("/", methods=["POST"])
@jwt_required()
def register_course():
    admin_or_committee_only()
    usercourse_info = UserCourseSchema().load(request.json)
    check = check_preexisting_graduation(usercourse_info["user_id"],usercourse_info["course_id"])
    if check:
        abort(406, description='Record already exists.')
    usercourse = UserCourse(
        user_id=usercourse_info["user_id"],
        course_id=usercourse_info["course_id"],
        equivalent = bool(usercourse_info.get("equivalent"))
    )
    db.session.add(usercourse)
    db.session.commit()

    return UserCourseSchema().dump(usercourse), 201


# Updating a completed course
@usercourses_bp.route('/<int:user_id>/<int:course_id>', methods=['PUT','PATCH'])
@jwt_required()
def update_usercourse(user_id,course_id):
    admin_or_committee_only()
    # usercourse_info = UserCourseSchema().load(request.json)
    usercourse = check_preexisting_graduation(user_id,course_id)
    if usercourse: 
        if usercourse.equivalent == True:
            usercourse.equivalent = False
            usercourse.date_of_completion = datetime.datetime.now()
            db.session.commit()
            return UserSchema().dump(usercourse)
        else: 
            return {'Error': 'Course already completed'}, 400
    else:
        return {'Error': 'Course cannot be found for that user'}, 404

# Return a list of all users with specific course
@usercourses_bp.route('/<int:course_id>')
@jwt_required()
def all_users_graduated(course_id):
    admin_or_committee_only()
    stmt = db.select(User).join(UserCourse).where(UserCourse.course_id==course_id)
    graduated_users = db.session.scalars(stmt).all()
    return UserSchema(many=True, exclude=["id","password","is_admin","is_committee"]).dump(graduated_users)


#Delete a user's courses
@usercourses_bp.route('/<int:user_id>/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_usercourse(user_id,course_id):
    admin_only()
    usercourse_info = UserCourseSchema().load(request.json)
    usercourse = check_preexisting_graduation(usercourse_info["user_id"],usercourse_info["course_id"])
    if usercourse:
        db.session.delete(usercourse)
        db.session.commit()
        return {'Success': 'Course deleted successfully'}, 200
    else:
        return {'Error':'No record of user graduating specificed course'}, 404
    
# Return a list of all users with only the equivalent
@usercourses_bp.route('/equivalent/<int:course_id>')
@jwt_required()
def equivalent_graduated(course_id):
    admin_or_committee_only()
    stmt = db.select(User).join(UserCourse).where(db.and_(UserCourse.course_id==course_id, UserCourse.equivalent==True))
    graduated_users = db.session.scalars(stmt).all()
    return UserSchema(many=True, exclude=["id","password","is_admin","is_committee"]).dump(graduated_users)

def check_preexisting_graduation(user_id, course_id):
    stmt = db.select(UserCourse).where(UserCourse.user_id==user_id,UserCourse.course_id==course_id)
    record = db.session.scalar(stmt)
    return record