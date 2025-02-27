#This file handles the Flask app creation, SQLAlchemy initialization, login manager, and blueprint registration.
#It also ensures the database and instance folder are correctly set up.

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 🔗 Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    """
    ⚙️ Initializes the Flask app, database, and login manager.
    - Registers blueprints for modular routing.
    - Ensures the instance folder exists and database is created.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Database path in instance folder
    db_path = os.path.join(os.getcwd(), "instance", "volvo_tlc_hub.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # 🗂️ Ensure instance folder exists
    os.makedirs(os.path.join(os.getcwd(), "instance"), exist_ok=True)

    # 🔌 Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # ⚡ Import models here to avoid circular imports
    from app.models.client import Client
    from app.models.employee import Employee

    @login_manager.user_loader
    def load_user(user_id):
        """
        🔐 Loads a user from the database by ID for session handling.
        Checks both Client and Employee tables.
        """
        return Client.query.get(int(user_id)) or Employee.query.get(int(user_id))

    # Register blueprints
    from app.auth.routes import auth as auth_blueprint
    from app.employee.routes import employee as employee_blueprint
    from app.main.routes import main as main_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(employee_blueprint, url_prefix="/employee")
    app.register_blueprint(main_blueprint)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
