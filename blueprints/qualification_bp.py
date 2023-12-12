from flask import Blueprint, request
from config import db
from flask_jwt_extended import jwt_required
from auth import *
from models.qualification import Qualification, QualificationSchema

qualifications_bp = Blueprint('qualification', __name__, url_prefix='/qualifications')

# Return a list of all Qualifications
@qualifications_bp.route('/')
@jwt_required()
def all_qualifications():
    stmt = db.select(Qualification)
    qualifications = db.session.scalars(stmt).all()
    return QualificationSchema(many=True).dump(qualifications)

# Create a new Qualification
@qualifications_bp.route('/', methods=['POST'])
@jwt_required()
def create_qualification():
    admin_only()
    qualification_info = QualificationSchema(exclude=['id']).load(request.json)
    qualification = Qualification(
        name=qualification_info['name'],
        description=qualification_info.get('description','')
    )
    db.session.add(qualification)
    db.session.commit()
    return QualificationSchema().dump(qualification),201

# Updating a Qualification
@qualifications_bp.route('/<int:id>', methods=['PUT','PATCH'])
@jwt_required()
def update_qualification(id):
    admin_or_committee_only()
    qualification_info = QualificationSchema(exclude=['id']).load(request.json)
    stmt = db.select(Qualification).filter_by(id=id)
    qualification = db.session.scalar(stmt)
    if qualification: 
        qualification.name = qualification_info.get('name', qualification.name)
        qualification.description = qualification_info.get('description', qualification.description)
        db.session.commit()
        return QualificationSchema().dump(qualification)
    else:
        return {'error':'Qualification not found'}, 404
    
# Deleting a Qualification
@qualifications_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_qualification(id):
    admin_only()
    stmt = db.select(Qualification).filter_by(id=id)
    qualification = db.session.scalar(stmt)
    if qualification: 
        db.session.delete(qualification)
        db.session.commit()
        return {'Sucess': 'Qualification successfully deleted'},200
    else:
        return {'Error':'Qualification not found'}, 404
    
