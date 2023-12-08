from config import db, ma
from marshmallow import fields
from marshmallow.validate import Length

class User(db.Model):
    __tablename__= "users"
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    phone_number = db.Column(db.Integer())
    is_admin = db.Column(db.Boolean(), default=False)
    is_committee = db.Column(db.Boolean(), default=False)

    user_courses = db.relationship('UserCourse', back_populates='user', cascade='all, delete')
    user_qualifications = db.relationship('UserQualification', back_populates='user', cascade='all, delete')
                                   
class UserSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=Length(min=8, error="Password must be at least 8 characters"))

    class Meta:
        fields = ("id", "first_name", "last_name", "email", "password", "is_admin", "is_committee")