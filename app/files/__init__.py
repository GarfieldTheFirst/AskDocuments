from flask import Blueprint

bp = Blueprint('files', __name__, template_folder="templates/files")

from app.files import routes
