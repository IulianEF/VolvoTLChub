# This file defines the Elevator model,
# which represents car elevators essential for scheduling repairs based on availability.

from app.models import db


class Elevator(db.Model):
    """
   🏗️ Elevator model for scheduling repairs based on availability.

    Attributes:
        id (int): Primary key.
        type (str): Type of elevator (e.g., Standard, Heavy-Duty).
        status (str): Current status of the elevator (Available, Occupied, Maintenance).
    """

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="Available", nullable=False)

    def __repr__(self):
        return f"<Elevator {self.id} - {self.type} ({self.status})>"
