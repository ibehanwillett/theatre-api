from flask import Blueprint, request
from models.user import User, UserSchema
from config import bcrypt, db
from sqlalchemy.exc import IntegrityError




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

