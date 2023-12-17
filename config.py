from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from os import environ
from werkzeug.exceptions import BadRequest
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import DataError, IntegrityError



app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = environ.get('JWT_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URI')


db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt= Bcrypt(app)
jwt = JWTManager(app)

@app.errorhandler(BadRequest)
def handle_bad_request(e):
    return {'Bad Request!': e.description}, 400

@app.errorhandler(KeyError)
def handle_key_error(e):
    return ({'Error': f'Value must be supplied for field {e}'}), 400

@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return {'error': str(e)}, 400

@app.errorhandler(DataError)
def handle_data_error(e):
    return {'error': str(e)}, 400

@app.errorhandler(IntegrityError)
def handle_integrity_error(e):
    return {'Error': str(e)}, 400

@app.errorhandler(401)
def handle_401(e):
    return {'Error': e.description}, 401

@app.errorhandler(403)
def handle_403(e):
    return {'Error': e.description}, 403

@app.errorhandler(404)
def handle_404(e):
    return {'Not Found': e.description}, 404

@app.errorhandler(405)
def handle_404(e):
    return {'Not Found': e.description}, 405

@app.errorhandler(406)
def handle_406(e):
    return {'Error': e.description}, 406

@app.errorhandler(415)
def handle_415(e):
    return {'Error': e.description}, 415