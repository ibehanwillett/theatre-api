from flask import Blueprint, request
from config import db
from models.course import Course, CourseSchema
from flask_jwt_extended import jwt_required
from auth import *
from models.user_course import UserCourse, UserCourseSchema

courses_bp = Blueprint('course', __name__, url_prefix='/courses')

# Return a list of all courses
@courses_bp.route('/')
@jwt_required()
def all_courses():
    # Creates a statement to return all courses in database
    stmt = db.select(Course)
    # Executes that query and returns the result in scalars
    courses = db.session.scalars(stmt).all()
    # Seralizes the scalars into a JSON object defined by the UserCourse Schema
    return CourseSchema(many=True).dump(courses)

# Create a new course
@courses_bp.route('/', methods=['POST'])
@jwt_required()
def create_course():
    admin_only()
    # Deserializes the information in the body of the request into a object defined by the Course Schema
    course_info = CourseSchema(exclude=['id']).load(request.json)
    # Creates a new Course object using data from course_info
    course = Course(
        name=course_info['name'],
        description=course_info.get('description','')
    )
    # Add the new Course object as a new entry in the course table in the database
    db.session.add(course)
    # Commits this session
    db.session.commit()
    return CourseSchema().dump(course),201

# Updating a course
@courses_bp.route('/<int:id>', methods=['PUT','PATCH'])
@jwt_required()
def update_course(id):
    admin_or_committee_only()
    # Deserialises the data from the body of the request into a Python object defined by the CourseSchema.
    # Some things are excluded from the Schema and partial is set to True.
    course_info = CourseSchema(exclude=['id'], partial=True).load(request.json)
    # A database query is created selecting the course in the database that matches the id in the course_info
    stmt = db.select(Course).filter_by(id=id)
    # Statement is executed.
    course = db.session.scalar(stmt)
    # If a course is found to match the id in the course_info, then the course is updated with other information from course_info
    if course: 
        course.name = course_info.get('name', course.name)
        course.description = course_info.get('description', course.description)
        db.session.commit() # The session is committed
        # Serialises the course data into a JSON defined by CourseSchema and returns it to the client
        return CourseSchema().dump(course) 
    else:
        return {'Error':'Course not found'}, 404
    
# Deleting a Course
@courses_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_course(id):
    admin_only()
    # A database query is created selecting the course in the database that matches the id specified in the route
    stmt = db.select(Course).filter_by(id=id)
    # The query is excuted
    course = db.session.scalar(stmt)
    if course: 
        # If a course is found, it is deleted from the database
        db.session.delete(course)
        # The session is committed
        db.session.commit()
        return {'success': 'Course successfully deleted'},200
    else:
        return {'error':'Course not found'}, 404
    
# Return a list of all users with only the equivalent
@courses_bp.route('/equivalent/<int:course_id>')
@jwt_required()
def equivalent_graduated(course_id):
    admin_or_committee_only()
    # Creates a database query to retrieve all UserCourse entities that are both of the id specified in the route and True for their equivalent attribute
    stmt = db.select(UserCourse).where(UserCourse.equivalent==True,UserCourse.course_id==course_id)
    # Executes the query and returns the result as scalars
    graduated_users = db.session.scalars(stmt).all()
    # Serialises the graduated users into a JSON defined by the UserCourse Schema
    return UserCourseSchema(many=True).dump(graduated_users)
    
