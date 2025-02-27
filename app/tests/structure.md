1. Project Presentation
Project Name:
Volvo TLC Hub – A car repair management system built with Flask.

Objective:
Provide an online platform where clients can register, log in, and schedule car repairs based on elevator availability.
Enable role-based employees (Manager, Receptionist, Mechanics, StockKeeper) to handle operations, stock, and repairs from their respective dashboards.
Key Features:
Registration & Authentication

Clients register with personal and vehicle info (VIN number, car model).
Employees are seeded (Manager, Receptionist, Mechanics, StockKeeper) and log in with credentials.
Passwords are hashed using werkzeug.security.
Role-Based Access

Manager: Oversees employees, can view high-level operations, potentially generate revenue reports.
Receptionist: Manages repair scheduling, approves client appointments.
Mechanics: View assigned repairs, update statuses.
StockKeeper: Manages consumables, orders parts if below threshold.
Car Repair Scheduling

Clients can choose a repair description and date, then select an available elevator.
The elevator’s status changes to Occupied to prevent overlap.
Database & Models

Client model: Captures personal details, VIN, car model.
Employee model: Polymorphic roles (Manager, Receptionist, Mechanic, StockKeeper).
Elevator model: Tracks elevator type and status.
Repair model: Links client, elevator, (optionally) an employee, stores cost, status, etc.
Consumable model: Handles parts/consumables stock (quantity, price, reorder threshold).
OOP Principles

Employee is a base class, with specialized roles as subclasses inheriting from it.
Decorators (in utils.py) for role checks with @role_required.
Project Structure

php
Copy
Edit
Car_app/
├── app/
│   ├── auth/              # login/register routes
│   ├── employee/          # employees' dashboards
│   ├── main/              # core client scheduling routes
│   ├── models/            # all database models
│   ├── static/            # images/css (if any)
│   ├── templates/         # HTML files
│   ├── utils.py           # role-based decorators
│   └── db_setup.py        # app & db init
├── manual_db_create.py    # seeds elevators if not present
├── manual_add_employee.py # seeds employees if not present
└── run.py                 # runs the Flask app
Numpy & Pandas Integration

Potentially used in generating consumption or revenue reports. (Code placeholders or expansions can be made for actual data analysis.)
Regex & Filepath Usage

Regex could be used in validation for phone numbers, VIN, or emails.
Filepath used in db_setup.py for database creation path, exporting any CSV reports (if implemented).
