from app.db_setup import db, create_app
from app.models.employee import Manager, Receptionist, Mechanic, StockKeeper
from werkzeug.security import generate_password_hash
from datetime import date

app = create_app()

with app.app_context():
    """
    Adds predefined employees if they don't exist.
    Does not drop any existing table or data.
    """
    # Check if Manager already exists
    manager_exists = Manager.query.first()
    if manager_exists:
        print("ℹ️ Employees already exist. No changes made.")
    else:
        # Create sample employees
        m = Manager(
            name="Manager One",
            email="manager@volvo.com",
            password=generate_password_hash("manager123", method="scrypt"),
            employment_date=date.today(),
            salary=7000.0,
            department="Operations"
        )
        r = Receptionist(
            name="Receptionist One",
            email="reception@volvo.com",
            password=generate_password_hash("reception123", method="scrypt"),
            employment_date=date.today(),
            salary=3000.0,
            department="Front Desk"
        )
        mech1 = Mechanic(
            name="Mechanic One",
            email="mechanic1@volvo.com",
            password=generate_password_hash("mechanic123", method="scrypt"),
            employment_date=date.today(),
            salary=4000.0,
            department="Repairs"
        )
        mech2 = Mechanic(
            name="Mechanic Two",
            email="mechanic2@volvo.com",
            password=generate_password_hash("mechanic456", method="scrypt"),
            employment_date=date.today(),
            salary=4000.0,
            department="Repairs"
        )
        sk = StockKeeper(
            name="Stock Keeper One",
            email="stockkeeper@volvo.com",
            password=generate_password_hash("stock123", method="scrypt"),
            employment_date=date.today(),
            salary=3500.0,
            department="Inventory"
        )
        db.session.add_all([m, r, mech1, mech2, sk])
        db.session.commit()
        print("✅ Employees seeded successfully.")
