#This file defines the Employee base class and role-specific subclasses
# (Manager, Receptionist, Mechanic, StockKeeper) using inheritance.

from app.models import db
from flask_login import UserMixin
from datetime import date


class Employee(UserMixin, db.Model):
    """
     🏭 Base Employee model with polymorphic roles (Manager, Mechanic, etc.).

    Attributes:
        id (int): Primary key.
        name (str): Employee's full name.
        email (str): Unique email for login.
        role (str): Employee's role in the company.
        employment_date (date): Date of employment.
        salary (float): Monthly salary.
        password (str): Hashed password.
        department (str): Department the employee belongs to.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    employment_date = db.Column(db.Date, default=date.today)
    salary = db.Column(db.Float, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100))

    __mapper_args__ = {
        "polymorphic_identity": "employee",
        "polymorphic_on": role
    }

    def __repr__(self):
        return f"<Employee {self.name} - {self.role}>"


class Manager(Employee):
    __mapper_args__ = {"polymorphic_identity": "Manager"}

    def __init__(self, **kwargs):
        super().__init__(role="Manager", **kwargs)


class Receptionist(Employee):
    __mapper_args__ = {"polymorphic_identity": "Receptionist"}

    def __init__(self, **kwargs):
        super().__init__(role="Receptionist", **kwargs)


class Mechanic(Employee):
    __mapper_args__ = {"polymorphic_identity": "Mechanic"}

    def __init__(self, **kwargs):
        super().__init__(role="Mechanic", **kwargs)


class StockKeeper(Employee):
    __mapper_args__ = {"polymorphic_identity": "StockKeeper"}

    def __init__(self, **kwargs):
        super().__init__(role="StockKeeper", **kwargs)
