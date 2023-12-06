from flask import Blueprint
from config import db, bcrypt
from models.user import User
from models.course import Course
from models.user_course import UserCourse
from models.qualification import Qualification
from models.user_qualification import UserQualification



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
            first_name="Johnny",
            last_name="Garage",
            email="johnny@bigforktheatre.com",
            password=bcrypt.generate_password_hash("vroom vroom").decode("utf8"),
            is_committee=True,
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
            description = 'Covers the basics of improv'
        ),

        Course(
            name = 'The Scene',
            description = 'Covers techniques for a two person scene'
        ),

        Course(
            name = 'Characters',
            description = 'Teaches how to develop characters'
        ), 

        Course(
            name = 'Group Mind',
            description = 'Teaches group game skills and openings for shows'
        ), 

        Course(
            name = 'Finding the Funny',
            description = 'The basics of game improv'
        ), 
    ]

    db.session.add_all(courses)
    db.session.commit()

    # Creating the qualifications
    qualifications = [
        Qualification(
            name = 'RSA',
            description = 'Responsible Service of Alchol. You need it to bartend in Queensland.'
        ), 

        Qualification(
            name = 'Venue Manager',
            description = 'Responsibities include opening and closing the venue, open and closing till and orgainising performers and volenteers on the night'
        )
    ]

    db.session.add_all(qualifications)
    db.session.commit()

    # Creating course enrollement
    graduated = [
        UserCourse(
            user_id=users[0].id,
            course_id=courses[0].id,
        )
    ]

    db.session.add_all(graduated)
    db.session.commit()

    # Assigning qualifications
    qualifications = [
        UserQualification(
            user_id=users[0].id,
            qualification_id=qualifications[0].id,
        )
    ]

    db.session.add_all(qualifications)
    db.session.commit()



    print("Database seeded")