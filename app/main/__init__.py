from flask import Blueprint

# Define the main blueprint
main = Blueprint('main', __name__)

# Import routes after defining the blueprint to avoid circular imports
from app.main import routes
