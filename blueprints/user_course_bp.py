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
    # Deserialises the information from the request's body into the an object defined by UserCourse schema.
    # Only the equivalent and date of completion fields are used from UserSchema, the other fields are provided by route.
    usercourse_info = UserCourseSchema(only=("equivalent","date_of_completion")).load(request.json)
    # The database is checked to ensure this UserCourse isn't a duplicate.
    check = check_preexisting_graduation(user_id, course_id)
    if check:
        # If it is, an exception is raised
        abort(406, description='Record already exists.')
        # If not, a new Usercourse object is created seeded with data from usercourse_info
    usercourse = UserCourse(
        user_id=user_id,
        course_id=course_id,
        equivalent = bool(usercourse_info.get("equivalent", False)), # currently put "" to indicate false, literally anything else to indicate true. I hate this.
        date_of_completion = usercourse_info.get("date_of_completion",datetime.datetime.now()) #YYYY-MM-DD
    )
    # The new UserCourse object is added to the database.
    db.session.add(usercourse)
    # The session is committed.
    db.session.commit()

    return UserCourseSchema().dump(usercourse), 201


# Updating a completed course to from equivalent to non-equivalent
@usercourses_bp.route('/<int:user_id>/<int:course_id>', methods=['PUT','PATCH'])
@jwt_required()
def update_usercourse(user_id,course_id):
    admin_or_committee_only()
    # Checks if there is pre-existing record of the User graduating the specified course (User id and course id supplied by the route.)
    usercourse = check_preexisting_graduation(user_id,course_id)
    if usercourse: 
        # If there is a matching Usercourse, check what value is stored for equivalent
        if usercourse.equivalent == True:
            # If it is true, change to false
            usercourse.equivalent = False
            # Update date of compeletion to today's date.
            usercourse.date_of_completion = datetime.datetime.now()
            #C Commit the session
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
    # Create a statement selecting all UserCourses where the id of the course matches the course id specifed in the route
    stmt = db.select(UserCourse).where(UserCourse.course_id==course_id)
    # Excutes the statment and saves in in a variable called graduated_users
    graduated_users = db.session.scalars(stmt).all()
    # Deserialise the graduated_users into a JSON defined by UserCourse schema and returns that to the client
    return UserCourseSchema(many=True).dump(graduated_users)


#Delete a user's courses
@usercourses_bp.route('/<int:user_id>/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_usercourse(user_id,course_id):
    admin_only()
    # Selects all UserCourses where the id of the course matches the course id & user id specifed in the route from the database
    usercourse = check_preexisting_graduation(user_id,course_id)
    # If a matching UserCourse is found...
    if usercourse:
        # Delete the UserCourse
        db.session.delete(usercourse)
        # Commit the session
        db.session.commit()
        return {'Success': 'Course deleted successfully'}, 200
    else:
        return {'Error':'No record of user graduating specificed course'}, 404
    

def check_preexisting_graduation(user_id, course_id):
    # Creates a database query to select the UserCourse that has the user id and the course_id specifed in the function
    stmt = db.select(UserCourse).where(UserCourse.user_id==user_id,UserCourse.course_id==course_id)
    # Executes the query and stored the result in the record variable.
    record = db.session.scalar(stmt)
    # Returns the record variable
    return record

