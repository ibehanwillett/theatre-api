from flask import Blueprint, request
from config import db
from flask_jwt_extended import jwt_required
from auth import *
from models.qualification import Qualification, QualificationSchema

qualifications_bp = Blueprint('qualification', __name__, url_prefix='/qualifications')

# Return a list of all qualifications
@qualifications_bp.route('/')
@jwt_required()
def all_qualifications():
    # Creates a statement to return all qualifications in database
    stmt = db.select(Qualification)
    # Executes that query and returns the result in scalars
    qualifications = db.session.scalars(stmt).all()
    # Seralizes the scalars into a JSON object defined by the UserQualification Schema
    return QualificationSchema(many=True).dump(qualifications)

# Create a new qualification
@qualifications_bp.route('/', methods=['POST'])
@jwt_required()
def create_qualification():
    admin_only()
    # Deserializes the information in the body of the request into a object defined by the Qualification Schema
    qualification_info = QualificationSchema(exclude=['id']).load(request.json)
    # Creates a new qualification object using data from qualification_info
    qualification = Qualification(
        name=qualification_info['name'],
        description=qualification_info.get('description','')
    )
    # Add the new Qualification object as a new entry in the qualifications table in the database
    db.session.add(qualification)
    # Commits the session
    db.session.commit()
    return QualificationSchema().dump(qualification),201

# Updating a qualification
@qualifications_bp.route('/<int:id>', methods=['PUT','PATCH'])
@jwt_required()
def update_qualification(id):
    admin_or_committee_only()
     # Deserialises the data from the body of the request into a Python object defined by the QualificationSchema.
    # Some things are excluded from the Schema and partial is set to True.
    qualification_info = QualificationSchema(exclude=['id'], partial=True).load(request.json)
     # A database query is created selecting the qualification in the database that matches the id in the qualification_info
    stmt = db.select(Qualification).filter_by(id=id)
    # Statement is executed. The course found is stored in the qualification variable.
    qualification = db.session.scalar(stmt)
     # If a qualification is found to match, then the qualification is updated with other information from qualification_info
    if qualification: 
        qualification.name = qualification_info.get('name', qualification.name)
        qualification.description = qualification_info.get('description', qualification.description)
        # The session is commited
        db.session.commit()
        # Serialises the updated qualification into a JSON defined by QualificationSchema and returns it to the client
        return QualificationSchema().dump(qualification)
    else:
        return {'error':'Qualification not found'}, 404
    
# Deleting a Qualification
@qualifications_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_qualification(id):
    admin_only()
    # A database query is created selecting the qualification in the database that matches the id specified in the route
    stmt = db.select(Qualification).filter_by(id=id)
    # The query is executed and stored in the qualifcation variable
    qualification = db.session.scalar(stmt)
    if qualification: 
        # If a qualification is found it is deleted from the database
        db.session.delete(qualification)
        # The session is committed
        db.session.commit()
        return {'Success': 'Qualification successfully deleted'},200
    else:
        return {'Error':'Qualification not found'}, 404
    
