from config import *
from blueprints.cli_bp import db_commands
from blueprints.course_bp import courses_bp
from blueprints.qualification_bp import qualifications_bp
from blueprints.user_bp import users_bp
from blueprints.user_qualification_bp import userqualifications_bp

app.register_blueprint(db_commands)
app.register_blueprint(courses_bp)
app.register_blueprint(qualifications_bp)
app.register_blueprint(users_bp)
app.register_blueprint(userqualifications_bp)