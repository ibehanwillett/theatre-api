from flask import Blueprint, request
from models.user import User, UserSchema
from config import bcrypt, db
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required
from datetime import timedelta
from models.user_qualification import UserQualification, UserQualificationSchema
from models.qualification import Qualification
from models.user_course import UserCourse, UserCourseSchema
from models.course import Course
from auth import *

users_bp = Blueprint('users', __name__, url_prefix='/users')

# Create a new user
@users_bp.route("/register", methods=["POST"])
def register():
    try:
        # Desezialises the data from the body of the request into object defined by the User Schema
        user_info = UserSchema(exclude=["id", "is_admin", "is_committee"]).load(request.json)
        # Creates a new User object with infomation from the user_info variable.
        user = User(
            email=user_info["email"],
            password=bcrypt.generate_password_hash(user_info["password"]).decode(
                "utf8"
            ),
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            phone_number=user_info.get("phone_number"),
        )
        # Adds the user to the database
        db.session.add(user)
        # Commits the session
        db.session.commit()
        return UserSchema(exclude=["password"]).dump(user), 201
    except IntegrityError:
        return {"error": "Email address already in use"}, 409
    
@users_bp.route("/login", methods=["POST"])
def login():
    # Deserialize the information in the body of the request into an object defined by the UserSchema
    user_info = UserSchema(only=["email", "password"]).load(request.json)
    # Creates a query to select the user in the user table in the database that matches the email address in user_info
    stmt = db.select(User).where(User.email == user_info["email"])
    # Executes that query and returns a scalar result
    user = db.session.scalar(stmt)
    # Checks to see if the password in the user_info matches the password of the user in the database
    if user and bcrypt.check_password_hash(user.password, user_info["password"]):
        # If so, returns a JWT token
        token = create_access_token(identity=user.id, expires_delta=timedelta(hours=2))
        
        return {'token': token, 'user': UserSchema(exclude=["password", "is_admin", "is_committee"]).dump(user)}
    else:
        # If not, returns a error
        return {"error": "Invalid email or password"}, 401

# Returns list of all users
@users_bp.route("/", methods=["GET"])
@jwt_required()
def all_users():
    # Creates a query to get all users in the user table of the database, and to order them by their last name
    stmt = db.select(User).order_by('last_name')
    # Executes the query and return the result as scalars
    users = db.session.scalars(stmt).all()
    # Serizalises the result into JSON defined by the UserSchema
    return UserSchema(many=True, only=["first_name","last_name"]).dump(users)

# Returns list of all committee members
@users_bp.route("/committee")
@jwt_required()
def all_committee():
    # Creates a query to get all users in the user table of the database that have is_committee equal True 
    stmt = db.select(User).where(User.is_committee == True).order_by('last_name')
    # Executes the query and return the result as scalars
    users = db.session.scalars(stmt).all()
    # Serizalises the result into JSON defined by the UserSchema
    return UserSchema(many=True, only=["first_name","last_name"]).dump(users)

# Updates single user
@users_bp.route('/<int:user_id>', methods=['PUT','PATCH'])
@jwt_required()
def update_user(user_id):
    # Desezialises the data from the body of the request into object defined by the User Schema
    user_info = UserSchema(partial=True).load(request.json)
    # Creates a query to select the user in the user table in the database that matches the id specificed in the route
    stmt = db.select(User).filter_by(id=user_id)
    # Executes the query and returns the result as a scalar
    user = db.session.scalar(stmt)
    # If/then regarding if there is a user with that name in the database.
    if user: 
        # Authorise if the user that's logged on the same user that being updated OR if the user that's logged on is a admin
        authorize(user.id)
        # Updates the user from information in the user_info object
        user.email = user_info.get('email', user.email)
        user.password = user_info.get('password', user.password)
        user.first_name = user_info.get('first_name', user.first_name)
        user.last_name = user_info.get('last_name', user.last_name)
        user.phone_number = user_info.get('phone_number', user.phone_number)
        # If the user is an administrator, they can update the user's status as being an administrator or as a committee member
        if user_info.get('is_admin') == "True":
            admin_only()
            user.is_admin = True
        if user_info.get('is_committee') == "True":
            admin_only()
            user.is_committee = True
            # Commits the session
        db.session.commit()
        # Serializes and returns a JSON containing the updated user's information
        return UserSchema(exclude=["password"]).dump(user)
    else:
        return {'error': 'No such user'}

# Deletes a user from the database
@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    # Creates a query to select the user in the user table in the database that matches the id specificed in the route
    stmt = db.select(User).filter_by(id=user_id)
    # Executes that query and returns a scalar result
    user = (db.session.scalar(stmt))
    if user:
        # Authorise if the user that's logged on the same user that being updated OR if the user that's logged on is a admin
        authorize(user_id)
        # Deletes the user from the database
        db.session.delete(user)
        # Commits the session
        db.session.commit()
        return {'Success': 'User deleted successfully'}, 200
    else:
        return {'Error':'User not found'}, 404
    
# Returns a list of all qualifications a user has 
@users_bp.route('qualified/<int:user_id>')
@jwt_required()
def all_qualifications(user_id):
    # Authorise the current user is either a adminstrator or and committee member
    authorize_committee(user_id)
    # Create a database query selecting all UserQualification entities where the user id matched the id specified in the route
    stmt = db.select(UserQualification).where(UserQualification.user_id==user_id)
    # Executes the query and return the result as scalars
    qualifications = db.session.scalars(stmt).all()
    # Serizalises and returns the result as a JSON object defined by the User Qualification Schema
    return UserQualificationSchema(many=True).dump(qualifications)

# Returns a list of courses that a user has completed
@users_bp.route('graduated/<int:user_id>')
@jwt_required()
def all_courses(user_id):
     # Authorise the current user is either a adminstrator or and committee member
    authorize_committee(user_id)
    # Create a database query selecting all UserCourse entities where the user id matched the id specified in the route
    stmt = db.select(UserCourse).where(UserCourse.user_id==user_id)
     # Executes the query and return the result as scalars
    courses = db.session.scalars(stmt).all()
    # Serizalises and returns the result as a JSON object defined by the User Course Schema
    return UserCourseSchema(many=True).dump(courses)





