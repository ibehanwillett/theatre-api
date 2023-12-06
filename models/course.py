from config import db, ma
from marshmallow import fields

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String())

class CourseSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "description")