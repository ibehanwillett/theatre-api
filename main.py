from config import *
from blueprints.cli_bp import db_commands

app.register_blueprint(db_commands)