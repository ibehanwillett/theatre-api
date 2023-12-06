from flask import Blueprint
from config import db, bcrypt
from models.user import User
from models.course import Course
from models.qualification import Qualification
from datetime import date


db_commands = Blueprint('db', __name__)

@db_commands.cli.command("create")
def db_create():
    db.drop_all()
    db.create_all()
    print("Created tables")


@db_commands.cli.command("seed")
def db_seed():
    # Creating the user table
    users = [
        User(
            first_name= 'Big Fork',
            last_name= 'Admin',
            email="admin@bigforktheatre.com",
            password=bcrypt.generate_password_hash("comedyhero").decode("utf8"),
            is_admin=True,
        ),
        User(
            first_name="Horse",
            last_name="Jorsington",
            email="horse@jorse.com",
            password=bcrypt.generate_password_hash("mayorhorse").decode("utf8"),
        ),
    ]

    db.session.add_all(users)
    db.session.commit()
    # Creating the courses
    courses = [
        Course(
            name = 'Improv Fundamentals',
            description = 'The first class'
        )
    ]

    db.session.add_all(courses)
    db.session.commit()

    # Creating the qualifications
    qualifications = [
        Qualification(
            name = 'RSA',
            description = 'Responsible Service of Alchol. You need it to bartend in Queensland.'
        )
    ]

    db.session.add_all(qualifications)
    db.session.commit()


    print("Database seeded")