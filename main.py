from config import *
from blueprints.cli_bp import db_commands
from blueprints.course_bp import courses_bp

app.register_blueprint(db_commands)
app.register_blueprint(courses_bp)