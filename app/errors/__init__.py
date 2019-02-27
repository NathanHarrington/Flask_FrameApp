''' Blueprint for displaying more pleasing error messages. '''
from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers
