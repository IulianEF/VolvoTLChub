from app.db_setup import db, create_app
from app.models.elevator import Elevator

app = create_app()

with app.app_context():
    """
    Seeds the elevator table if no elevators exist yet.
    Doesn't drop other tables (keeps existing data).
    """
    if not Elevator.query.first():
        # Seed two sample elevators
        elevators = [
            Elevator(type="Standard", status="Available"),
            Elevator(type="Heavy-Duty", status="Available")
        ]
        db.session.add_all(elevators)
        db.session.commit()
        print("✅ Elevators seeded successfully.")
    else:
        print("ℹ️ Elevators already exist. No changes made.")
