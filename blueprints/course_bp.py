from flask import Blueprint, request
from config import db
from models.course import Course, CourseSchema
from flask_jwt_extended import jwt_required
from auth import *

courses_bp = Blueprint('course', __name__, url_prefix='/courses')

# Return a list of all courses
@courses_bp.route('/')
@jwt_required()
def all_courses():
    stmt = db.select(Course)
    courses = db.session.scalars(stmt).all()
    return CourseSchema(many=True).dump(courses)

# Create a new course
@courses_bp.route('/', methods=['POST'])
@jwt_required()
def create_course():
    admin_only()
    course_info = CourseSchema(exclude=['id']).load(request.json)
    course = Course(
        name=course_info['name'],
        description=course_info.get('description','')
    )
    db.session.add(course)
    db.session.commit()
    return CourseSchema().dump(course),201

# Updating a course
@courses_bp.route('/<int:id>', methods=['PUT','PATCH'])
@jwt_required()
def update_course(id):
    admin_or_committee_only()
    course_info = CourseSchema(exclude=['id']).load(request.json)
    stmt = db.select(Course).filter_by(id=id)
    course = db.session.scalar(stmt)
    if course: 
        course.name = course_info.get('name', course.name)
        course.description = course_info.get('description', course.description)
        db.session.commit()
        return CourseSchema().dump(course)
    else:
        return {'Error':'Course not found'}, 404
    
# Deleting a Course
@courses_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_course(id):
    admin_only()
    stmt = db.select(Course).filter_by(id=id)
    course = db.session.scalar(stmt)
    if course: 
        db.session.delete(course)
        db.session.commit()
        return {'sucess': 'Course successfully deleted'},200
    else:
        return {'error':'Course not found'}, 404
    
