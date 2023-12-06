from flask import Blueprint, request
from config import db
from models.qualification import Qualification, QualificationSchema

qualifications_bp = Blueprint('qualification', __name__, url_prefix='/qualifications')

# Return a list of all Qualifications
@qualifications_bp.route('/')
def all_qualifications():
    stmt = db.select(Qualification)
    qualifications = db.session.scalars(stmt).all()
    return QualificationSchema(many=True).dump(qualifications)

# Create a new Qualification
@qualifications_bp.route('/', methods=['POST'])
def create_qualification():
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
def update_qualification(id):
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
def delete_qualification(id):
    stmt = db.select(Qualification).filter_by(id=id)
    qualification = db.session.scalar(stmt)
    if qualification: 
        db.session.delete(qualification)
        db.session.commit()
        return {'sucess': 'Qualification successfully deleted'},200
    else:
        return {'error':'Qualification not found'}, 404
    
