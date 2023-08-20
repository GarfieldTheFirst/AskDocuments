from flask import Blueprint

bp = Blueprint('home', __name__, template_folder="templates/home")

from app.home import routes
