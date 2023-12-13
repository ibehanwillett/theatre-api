from config import db, ma
from marshmallow import fields

class Qualification(db.Model):
    __tablename__ = 'qualifications'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String())

    user_qualifications = db.relationship('UserQualification', back_populates='qualification')


class QualificationSchema(ma.Schema):
    # name= fields.String(required=True)
    class Meta:
        fields = ("id", "name", "description")