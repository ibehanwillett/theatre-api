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
            phone_number= '0423537563',
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
            phone_number= "32456411",
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
            description = 'Responsible Service of Alcohol. You need it to bartend in Queensland.'
        ), 

        Qualification(
            name = 'Venue Manager',
            description = 'Responsibities include opening and closing the venue, open and closing till and orgainising performers and volenteers on the night'
        ), 

        Qualification(
            name = 'Door Person', 
            description = 'Greets audience members as they enter the venue. Once the show begins, helps restock the bar.'
        ),

        Qualification(
            name = 'Tech Desk', 
            description = 'Greets audience members as they enter the venue. Once the show begins, helps restock the bar.'
        ),
        
    ]

    db.session.add_all(qualifications)
    db.session.commit()

    # Creating course enrollement
    graduated = [
        # Admin completed Fundies
        UserCourse(
            user_id=users[0].id,
            course_id=courses[0].id,
            equivalent = True,
        ),
        # Admin completed The Scene
        UserCourse(
            user_id=users[0].id,
            course_id=courses[1].id,
        ),
        # Admin completed Charaters
        UserCourse(
            user_id=users[0].id,
            course_id=courses[2].id,
        ),
        # Admin completed Group Mind
        UserCourse(
            user_id=users[0].id,
            course_id=courses[3].id,
        ),
        # Admin completed Finding the Funny
        UserCourse(
            user_id=users[0].id,
            course_id=courses[4].id,
        ),
         # Johnny completed Fundies
        UserCourse(
            user_id=users[1].id,
            course_id=courses[0].id,
            equivalent = True,
        ),
        # Johnny completed The Scene
        UserCourse(
            user_id=users[1].id,
            course_id=courses[1].id,
        ),
        # Johnny completed Charaters
        UserCourse(
            user_id=users[1].id,
            course_id=courses[2].id,
        ),
        # Johnny completed Group Mind
        UserCourse(
            user_id=users[1].id,
            course_id=courses[3].id,
        ),
         # Horse completed Fundies
        UserCourse(
            user_id=users[2].id,
            course_id=courses[0].id,
            equivalent = True,
        ),
        # Horse completed The Scene
        UserCourse(
            user_id=users[2].id,
            course_id=courses[1].id,
            equivalent = True,
        ),
        # Horse completed Charaters
        UserCourse(
            user_id=users[2].id,
            course_id=courses[2].id,
            equivalent= True,
        ),

    ]

    db.session.add_all(graduated)
    db.session.commit()

    # Assigning qualifications
    qualifications = [
        # Admin has a RSA
        UserQualification(
            user_id=users[0].id,
            qualification_id=qualifications[0].id,
        ),
        # Johnny is a venue manager
        UserQualification(
            user_id=users[1].id,
            qualification_id=qualifications[1].id,
        ),
        # Johnny can do door
        UserQualification(
            user_id=users[1].id,
            qualification_id=qualifications[2].id,
        ),
        # Horse Jorsington has a RSA
        UserQualification(
            user_id=users[2].id,
            qualification_id=qualifications[0].id,
            last_refresher= "08/08/2021"
        ),
        # Horse Jorsington can operate the tech desk
        UserQualification(
            user_id=users[2].id,
            qualification_id=qualifications[3].id,
            last_refresher= "08/08/2021"
        )
    ]

    db.session.add_all(qualifications)
    db.session.commit()



    print("Database seeded")