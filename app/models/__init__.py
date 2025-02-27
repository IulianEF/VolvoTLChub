from app.db_setup import db

# Import each model so they're recognized by SQLAlchemy
from .client import Client
from .employee import Employee
from .elevator import Elevator
from .repair import Repair
from .consumable import Consumable

__all__ = [
    "db",
    "Client",
    "Employee",
    "Elevator",
    "Repair",
    "Consumable"
]

