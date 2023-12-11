from flask import Blueprint, request
from models.user import User, UserSchema
from config import bcrypt, db
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required
from datetime import timedelta
from models.user_qualification import UserQualification, UserQualificationSchema
from models.qualification import Qualification, QualificationSchema
from models.user_course import UserCourse, UserCourseSchema
from models.course import Course, CourseSchema
from auth import *




users_bp = Blueprint('users', __name__, url_prefix='/users')

# Create a new user
@users_bp.route("/register", methods=["POST"]) #Note to self- is having /register still RESTful?
def register():
    try:
        user_info = UserSchema(exclude=["id", "is_admin", "is_committee"]).load(request.json)
        user = User(
            email=user_info["email"],
            password=bcrypt.generate_password_hash(user_info["password"]).decode(
                "utf8"
            ),
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            phone_number=user_info.get("phone_number"),
        )
        db.session.add(user)
        db.session.commit()

        return UserSchema(exclude=["password"]).dump(user), 201
    except IntegrityError:
        return {"error": "Email address already in use"}, 409
    
@users_bp.route("/login", methods=["POST"])
def login():
    user_info = UserSchema(only=["email", "password"]).load(request.json)
    stmt = db.select(User).where(User.email == user_info["email"])
    user = db.session.scalar(stmt)
    if user and bcrypt.check_password_hash(user.password, user_info["password"]):
        token = create_access_token(identity=user.id, expires_delta=timedelta(hours=2))
        return {'token': token, 'user': UserSchema(exclude=["password", "is_admin", "is_committee"]).dump(user)}
    else:
        return {"error": "Invalid email or password"}, 401

# Returns list of all users
@users_bp.route('/')
@jwt_required()
def all_users():
    stmt = db.select(User)
    users = db.session.scalars(stmt).all()
    return UserSchema(many=True, only=["first_name","last_name"]).dump(users)

# Returns list of all comittee members
@users_bp.route('/committee')
@jwt_required()
def all_committee():
    stmt = db.select(User).where(db.or_(User.is_committee == True))
    users = db.session.scalars(stmt).all()
    return UserSchema(many=True, only=["first_name","last_name"]).dump(users)

# Updates single user
@users_bp.route('/<int:user_id>', methods=['PUT','PATCH'])
@jwt_required()
def update_user(user_id):
    user_info = UserSchema().load(request.json)
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if user: 
        authorize()
        user.email = user_info.get('email', user.email)
        user.password = user_info.get('password', user.password)
        user.first_name = user_info.get('first_name', user.first_name)
        user.last_name = user_info.get('last_name', user.last_name)
        user.phone_number = user_info.get('phone_number', user.phone_number)
        admin = is_admin()
        # if admin is True:
        #     user.is_admin = user_info.get('is_admin', user.is_admin)
        #     user.is_committee = user_info.get('is_committee', user.is_committee)
        db.session.commit()
        return UserSchema().dump(user)
    else:
        return {'error': 'No such user'}

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    stmt = db.select(User).filter_by(user_id=id)
    user = (db.session.scalar(stmt))
    if user:
        authorize()
        db.session.delete(user)
        db.session.commit()
        return {'Success': 'User deleted successfully'}, 200
    else:
        return {'Error':'User not found'}, 404
    
# Returns a list of all qualifications a user has 
@users_bp.route('qualifications/<int:user_id>')
@jwt_required()
def all_qualifications(user_id):
    authorize_committee()
    stmt = db.select(Qualification).join(UserQualification).where(UserQualification.user_id==user_id)
    qualifications = db.session.scalars(stmt).all()
    return QualificationSchema(many=True).dump(qualifications)

# Returns a list of courses that a user has completed
@users_bp.route('courses/<int:user_id>')
@jwt_required()
def all_courses(user_id):
    authorize_committee()
    stmt = db.select(Course).join(UserCourse).where(UserCourse.user_id==user_id)
    courses = db.session.scalars(stmt).all()
    return CourseSchema(many=True).dump(courses)

