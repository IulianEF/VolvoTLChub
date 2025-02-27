#This file defines the Client model, which inherits from UserMixin for Flask-Login compatibility.
#It includes personal information and car details.

from app.models import db
from flask_login import UserMixin


class Client(UserMixin, db.Model):
    """
 🧑‍💼 Client model for customers scheduling car repairs.
    Attributes:
        id (int): Primary key.
        name (str): Full name of the client.
        email (str): Unique email for login.
        phone (str): Phone number of the client.
        address (str): Address of the client.
        vin_number (str): Vehicle Identification Number.
        car_model (str): Model of the client's car.
        password (str): Hashed password for authentication.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    vin_number = db.Column(db.String(50))
    car_model = db.Column(db.String(50))

    def __repr__(self):
        return f"<Client {self.name} - {self.email}>"


