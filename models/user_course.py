from config import db, ma
from marshmallow import fields
import datetime

class UserCourse(db.Model):
    __tablename__ = 'user_courses'
    id= db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    

    equivalent = db.Column(db.Boolean(), default=False)
    date_of_completion = db.Column(db.Date, default=datetime.datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="user_courses")

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    course = db.relationship("Course", back_populates="user_courses")

class UserCourseSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'course_id', 'equivalent', 'date_of_completion')
