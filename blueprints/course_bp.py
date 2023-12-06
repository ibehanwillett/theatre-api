from flask import Blueprint, request
from config import db
from models.course import Course, CourseSchema

courses_bp = Blueprint('course', __name__, url_prefix='/courses')

# Return a list of all courses
@courses_bp.route('/')
def all_courses():
    stmt = db.select(Course)
    courses = db.session.scalars(stmt).all()
    return CourseSchema(many=True).dump(courses)

# Create a new course
@courses_bp.route('/', methods=['POST'])
def create_course():
    course_info = CourseSchema(exclude=['id']).load(request.json)
    course = Course(
        name=course_info['name'],
        description=course_info.get('description','')
    )
    db.session.add(course)
    db.session.commit()
    return CourseSchema().dump(course),201

# Updating a Course

@courses_bp.route('/<int:id>', methods=['PUT','PATCH'])
def update_course(id):
    course_info = CourseSchema(exclude=['id']).load(request.json)
    stmt = db.select(Course).filter_by(id=id)
    course = db.session.scalar(stmt)
    if course: 
        course.name = course_info.get('name', course.name)
        course.description = course_info.get('description', course.description)
        db.session.commit()
        return CourseSchema().dump(course)
    else:
        return {'error':'Course not found'}, 404
    
# Deleting a course
@courses_bp.route('/<int:id>', methods=['DELETE'])
def delete_course(id):
    course_info = CourseSchema(exclude=['id']).load(request.json)
    stmt = db.select(Course).filter_by(id=id)
    course = db.session.scalar(stmt)
    if course: 
        db.session.delete(course)
        db.session.commit()
        return {'sucess': 'Course successfully deleted'},200
    else:
        return {'error':'Course not found'}, 404
    
