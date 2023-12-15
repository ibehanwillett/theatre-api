from config import db, ma
from marshmallow import fields
import datetime
from sqlalchemy import PrimaryKeyConstraint

class UserCourse(db.Model):
    __tablename__ = 'user_courses'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    

    equivalent = db.Column(db.Boolean(), default=False)
    date_of_completion = db.Column(db.Date, default=datetime.datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="user_courses")

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    course = db.relationship("Course", back_populates="user_courses")

    __table_args__ = (
    db.PrimaryKeyConstraint(
        user_id, course_id,
        ),
    )

class UserCourseSchema(ma.Schema):
    date_of_completion = fields.Date()
    equivalent_to = fields.Bool(default=False)
    class Meta:
        fields = ('equivalent', 'date_of_completion', 'user', 'course')
    user =  fields.Nested("UserSchema", only=("first_name","last_name"))
    course = fields.Nested("CourseSchema", only=["name"])
