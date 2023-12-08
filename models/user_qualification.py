from config import db, ma
from marshmallow import fields
import datetime
from sqlalchemy import PrimaryKeyConstraint

class UserQualification(db.Model):
    __tablename__ = 'user_qualifications'
    # id= db.Column(db.Integer, primary_key=True)
    last_refresher = db.Column(db.Date, default=datetime.datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="user_qualifications")
    
    qualification_id = db.Column(db.Integer, db.ForeignKey('qualifications.id'))
    qualification = db.relationship("Qualification", back_populates="user_qualifications")
    
    __table_args__ = (
    db.PrimaryKeyConstraint(
        user_id, qualification_id,
        ),
    )
    
   

class UserQualificationSchema(ma.Schema):
    class Meta:
        fields = ("user_id", "qualification_id", "last_refresher")
