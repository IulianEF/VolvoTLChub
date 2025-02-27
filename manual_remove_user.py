from app.db_setup import create_app, db
from app.models.client import Client
from app.models.employee import Employee

app = create_app()

with app.app_context():
    # Remove from Client table
    client_user = Client.query.filter_by(email="client1@client1.com").first()
    if client_user:
        db.session.delete(client_user)
        db.session.commit()
        print("✅ Removed user from Client table.")

    # Optionally remove from Employee if you suspect a duplicate there
    # employee_user = Employee.query.filter_by(email="manager@volvo.com").first()
    # if employee_user:
    #     db.session.delete(employee_user)
    #     db.session.commit()
    #     print("✅ Removed manager@volvo.com from Employee table.")
