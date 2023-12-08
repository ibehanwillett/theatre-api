from flask import Blueprint, request
from config import db
from models.user_course import UserCourse, UserCourseSchema
from models.user import User, UserSchema

usercourses_bp = Blueprint('usercourse', __name__, url_prefix='/user_courses')

# @usercourses_bp.route('/<int:course_id>')
# def all_users_qualified(course_id):
#     stmt = db.select(usercourse).where(usercourse.course_id==course_id)
#     qualified_users = db.session.scalars(stmt).all()
#     return usercourseSchema(many=True).dump(qualified_users)

#Give a user a new course
@usercourses_bp.route("/", methods=["POST"])
def register_course():
    usercourse_info = UserCourseSchema().load(request.json)
    usercourse = UserCourse(
        user_id=usercourse_info["user_id"],
        course_id=usercourse_info["course_id"],
        equivalent=usercourse_info.get("equivalent")
    )
    db.session.add(usercourse)
    db.session.commit()

    return UserCourseSchema().dump(usercourse), 201
# Note to self- need to create error handler for this one

# Do we need to update the user's course?

# @usercourses_bp.route('/<int:user_id>/<int:course_id>', methods=['PUT','PATCH'])
# def update_usercourse(user_id,course_id):
#     usercourse_info = UserCourseSchema().load(request.json)
#     stmt = db.select(UserCourse).filter_by(UserCourse.user_id==user_id,UserCourse.course_id==course_id)
#     usercourse = db.session.scalar(stmt)
#     if usercourse: 
#         # authorisation here
#         usercourse.last_refresher = usercourse_info.get('last_refresher', usercourse.last_refresher)
#         db.session.commit()
#         return UserSchema().dump(usercourse)
#     else:
#         return {'error': 'Qualification cannot be found for that user'}

# Return a list of all users with specific course
@usercourses_bp.route('/<int:course_id>')
def all_users_graduated(course_id):
    stmt = db.select(User).join(UserCourse).where(UserCourse.course_id==course_id)
    graduated_users = db.session.scalars(stmt).all()
    return UserSchema(many=True, exclude=["id","password","is_admin","is_committee"]).dump(graduated_users)


#Delete a user's courses
@usercourses_bp.route('/<int:user_id>/<int:course_id>', methods=['PUT','PATCH'])
def delete_usercourse(user_id,course_id):
    usercourse_info = UserCourseSchema().load(request.json)
    stmt = db.select(UserCourse).filter_by(UserCourse.user_id==user_id,UserCourse.course_id==course_id)
    usercourse = db.session.scalar(stmt)
    if usercourse:
        # authorize(user.user_id)
        db.session.delete(usercourse)
        db.session.commit()
        return {'success': 'Course deleted successfully'}, 200
    else:
        return {'error':'User/Course combo not found'}, 404
    
    # Return a list of all users with only the equivalent
@usercourses_bp.route('/equivalent/<int:course_id>')
def equivalent_graduated(course_id):
    stmt = db.select(User).join(UserCourse).where(db.and_(UserCourse.course_id==course_id, UserCourse.equivalent==True))
    graduated_users = db.session.scalars(stmt).all()
    return UserSchema(many=True, exclude=["id","password","is_admin","is_committee"]).dump(graduated_users)