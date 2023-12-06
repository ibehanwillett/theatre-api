from flask import Blueprint, request
from models.user import User, UserSchema
from config import bcrypt, db
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required
from datetime import timedelta




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
        token = create_access_token(identity=user.first_name, expires_delta=timedelta(hours=2))
        return {'token': token, 'user': UserSchema(exclude=["password", "is_admin", "is_committee"]).dump(user)}
    else:
        return {"error": "Invalid email or password"}, 401

