from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# ✅ Global instances (Single Source of Truth)
db = SQLAlchemy()
login_manager = LoginManager()
