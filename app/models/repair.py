# This file defines the Repair model, responsible for managing repair appointments,
# elevator assignments, and tracking statuses.

from app.models import db
from datetime import datetime


class Repair(db.Model):
    """
    🔧 Repair model linking client, elevator, and (optionally) employee.

    Attributes:
        id (int): Primary key.
        client_id (int): Foreign key linking to the Client.
        employee_id (int): Foreign key linking to the assigned mechanic.
        elevator_id (int): Foreign key linking to the used elevator.
        description (str): Description of the repair service.
        scheduled_date (datetime): Scheduled date for the repair.
        status (str): Repair status (Pending, Approved, Completed).
        cost (float): Total repair cost.
        billing_details (str): Billing information for the repair.
    """

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False)
    elevator_id = db.Column(db.Integer, db.ForeignKey("elevator.id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee.id"), nullable=True)
    description = db.Column(db.String(200), nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(20), default="Pending")
    cost = db.Column(db.Float, nullable=True)
    billing_details = db.Column(db.String(200))

    def __repr__(self):
        return f"<Repair {self.description} - Status: {self.status}>"