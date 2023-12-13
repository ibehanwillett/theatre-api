from flask import Blueprint, request
from config import db
from models.user_course import UserCourse, UserCourseSchema
from models.user import User, UserSchema
import datetime
from flask_jwt_extended import jwt_required
from auth import *

usercourses_bp = Blueprint('usercourse', __name__, url_prefix='/users/courses')

#Give a user a new course
@usercourses_bp.route("/<int:user_id>/<int:course_id>", methods=["POST"])
@jwt_required()
def register_course(user_id, course_id):
    admin_or_committee_only()
    usercourse_info = UserCourseSchema(only=("equivalent","date_of_completion")).load(request.json)
    check = check_preexisting_graduation(user_id, course_id)
    if check:
        abort(406, description='Record already exists.')
    usercourse = UserCourse(
        user_id=user_id,
        course_id=course_id,
        equivalent = bool(usercourse_info.get("equivalent", False)), # currently put "" to indicate false, literally anything else to indicate true. I hate this.
        date_of_completion = usercourse_info.get("date_of_completion",datetime.datetime.now()) #YYYY-MM-DD
    )
    db.session.add(usercourse)
    db.session.commit()

    return UserCourseSchema().dump(usercourse), 201


# Updating a completed course to from equivalent to non-equivalent
@usercourses_bp.route('/<int:user_id>/<int:course_id>', methods=['PUT','PATCH'])
@jwt_required()
def update_usercourse(user_id,course_id):
    admin_or_committee_only()
    usercourse = check_preexisting_graduation(user_id,course_id)
    if usercourse: 
        if usercourse.equivalent == True:
            usercourse.equivalent = False
            usercourse.date_of_completion = datetime.datetime.now()
            db.session.commit()
            return UserCourseSchema().dump(usercourse)
        else: 
            return {'Error': 'Course already completed'}, 400
    else:
        return {'Error': 'Course cannot be found for that user'}, 404

# Return a list of all users with specific course
@usercourses_bp.route('/<int:course_id>')
@jwt_required()
def all_users_graduated(course_id):
    admin_or_committee_only()
    stmt = db.select(UserCourse).where(UserCourse.course_id==course_id)
    graduated_users = db.session.scalars(stmt).all()
    return UserCourseSchema(many=True).dump(graduated_users)


#Delete a user's courses
@usercourses_bp.route('/<int:user_id>/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_usercourse(user_id,course_id):
    admin_only()
    usercourse = check_preexisting_graduation(user_id,course_id)
    if usercourse:
        db.session.delete(usercourse)
        db.session.commit()
        return {'Success': 'Course deleted successfully'}, 200
    else:
        return {'Error':'No record of user graduating specificed course'}, 404
    

def check_preexisting_graduation(user_id, course_id):
    stmt = db.select(UserCourse).where(UserCourse.user_id==user_id,UserCourse.course_id==course_id)
    record = db.session.scalar(stmt)
    return record

