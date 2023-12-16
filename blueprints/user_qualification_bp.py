from flask import Blueprint, request
from config import db
from models.user_qualification import UserQualification, UserQualificationSchema
from auth import *
import datetime
from flask_jwt_extended import jwt_required
userqualifications_bp = Blueprint('userqualification', __name__, url_prefix='/users/qualifications')


#Give a user a new qualification
@userqualifications_bp.route("/", methods=["POST"])
@jwt_required()
def register_qualification():
    admin_or_committee_only()
    # Deserialises the information from the request's body into the an object defined by UserQualification Schema.
    userqualification_info = UserQualificationSchema().load(request.json)
    # The database is checked to ensure this UserQualification isn't a duplicate.
    check = check_preexisting_qualification(userqualification_info["user_id"], userqualification_info["qualification_id"])
    if check:
        # If it is, an exception is raised
        abort(406, description='Record already exists.')
    # If not, a new UserQualification object is created seeded with data from userqualification_info
    userqualification = UserQualification(
        user_id=userqualification_info["user_id"],
        qualification_id=userqualification_info["qualification_id"],
    )
    # The new UserQualification object is added to the database.
    db.session.add(userqualification)
    # The session is committed
    db.session.commit()
    return UserQualificationSchema().dump(userqualification), 201

# Update the last refresher for a qualification
@userqualifications_bp.route('/<int:user_id>/<int:qualification_id>', methods=['PUT','PATCH'])
@jwt_required()
def update_userqualification(user_id,qualification_id):
    # Deserialises the information from the request's body into an object defined by the UserQualification Schema.
    userqualification_info = UserQualificationSchema().load(request.json)
     # The database is searched for a pre-existing UserQualification with the same qualification id and user id..
    userqualification = check_preexisting_qualification(user_id, qualification_id)
    if userqualification: 
        admin_or_committee_only()
        # The matching userqualification entity's last_refresher date is updated to the current date.
        userqualification.last_refresher = userqualification_info.get('last_refresher', datetime.datetime.now())
        # The database session is committed.
        db.session.commit()
        return UserQualificationSchema().dump(userqualification)
    else:
        return {'Error': 'Qualification cannot be found for that user'}

# Return a list of all users with specific qualification
@userqualifications_bp.route('/<int:qualification_id>')
@jwt_required()
def all_users_qualified(qualification_id):
    admin_or_committee_only()
    # Create a statement selecting all UserQualifications where the id of the qualification matches the qualification id specifed in the route
    stmt = db.select(UserQualification).where(UserQualification.qualification_id==qualification_id)
    # Excutes the statment and saves in in a variable called qualified_users
    qualified_users = db.session.scalars(stmt).all()
    if qualified_users:
        # Deserialise the qualifed_users into a JSON defined by UserQualification schema and returns that to the client
        return UserQualificationSchema(many=True).dump(qualified_users), 200
    else:
        return {'Error': 'No records found.'},404


#Delete a user's qualifications
@userqualifications_bp.route('/<int:user_id>/<int:qualification_id>', methods=['DELETE'])
@jwt_required()
def delete_userqualification(user_id,qualification_id):
    # Selects all UserQualifications where the id of the qualification matches the qualification id & user id specifed in the route from the database
    userqualification = check_preexisting_qualification(user_id,qualification_id)
    # If a matching UserQualification is found...
    if userqualification:
        admin_or_committee_only()
        # The UserQualification is deleted
        db.session.delete(userqualification)
        # The session is committed
        db.session.commit()
        return {'Success': 'Qualification deleted successfully'}, 200
    else:
        return {'Error':'User/Qualification combo not found'}, 404
    

def check_preexisting_qualification(user_id, qualification_id):
    # Creates a database query to select the UserQualification that has the user id and the course_id specifed in the function
    stmt = db.select(UserQualification).where(UserQualification.user_id==user_id,UserQualification.qualification_id==qualification_id)
    # Executes the query and stored the result in the record variable.
    record = db.session.scalar(stmt)
     # Returns the record variable
    return record
