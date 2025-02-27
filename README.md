1. Overview & Purpose
Technologies Used

Python 3.9+
Flask (for web framework and routing)
Flask-Login (for authentication and session management)
SQLAlchemy and Flask-SQLAlchemy (ORM for database interactions)
SQLite (for local development database)
Pandas & Numpy (basic data handling for reports)
pdfkit / wkhtmltopdf (optional, for exporting PDF reports)
Jinja2 (template engine for rendering HTML)
Project Goal
Provide a comprehensive vehicle service management system for Volvo customers, enabling:

Client registration and scheduling repairs.
Role-based employee dashboards for Manager, Receptionist, Mechanic, and StockKeeper.
Elevator management, stock-keeping, revenue reports, and PDF exporting.

            2. Features & Flows
Client Flow

Register / Login as a client.
Schedule repairs on available elevators and see repair history in client_dashboard.
Receptionist Flow

View pending repairs in receptionist_dashboard.
Approve or reschedule repairs.
Assign a repair to a Mechanic, so it appears in that mechanic’s dashboard.
Mechanic Flow

mechanic_dashboard lists assigned repairs (employee_id matches the mechanic).
Mark repairs “Completed” and optionally update parts used.
Frees the elevator once a repair is done.
StockKeeper Flow

stockkeeper_dashboard shows all consumables (oil, filters, etc.).
Check low stock alerts.
Replenish stock items to keep them above threshold.
Manager Flow

manager_dashboard: block/unblock elevators, manage employees, generate revenue reports.
Export revenue to PDF using pdfkit.

            3. Code Flow & Architecture
db_setup.py:

Contains create_app() which configures Flask, database, and login_manager.
Registers blueprints: auth, employee, main.
Defines @login_manager.user_loader to load users from Client or Employee tables.
Blueprints:

app/auth: routes.py for login, register, logout.
app/employee: routes.py with sub-routes for Manager, Receptionist, Mechanic, StockKeeper.
app/main: routes.py for client-facing routes, homepage, scheduling repairs, etc.
Models (in app/models/):

Client: Basic user with no role.
Employee: Inherits from a single table with role = "Manager"/"Receptionist"/"Mechanic"/"StockKeeper".
Elevator: Tracks repair bay availability, status (occupied, available, blocked).
Repair: Represents scheduled or completed repairs, references client_id and optionally employee_id.
Consumable: Stock items for the shop (oil, filters, etc.), with threshold management.
Templates:

base.html: shared layout, includes navbar with brand link and role-based links.
Various dashboard pages (manager_dashboard, receptionist_dashboard, etc.) each presenting role-specific data.
PDF templates (e.g., pdf_report.html) for exporting manager’s revenue reports.
Role Logic:

utils.py has @role_required("Mechanic") (etc.) to ensure a route is accessed only by the correct role.
If a user is not authenticated or lacks the correct role, they’re redirected with an error message.

            4.  Scripts
Manual scripts in the root:

manual_db_create.py: Drop and recreate tables, seed initial elevator data.
manual_add_employee.py: Seeds employees.
manual_seed_consumables.py: Seeds 20 random consumables.
manual_remove_repair.py: Removes specified or all repairs.

            5. Additional Notes
Navigation:
The navbar link “Volvo TLC Hub” calls /home_redirect (or similar) to route the user depending on whether they’re a client or an employee with a particular role.
Styling:
base.html references Bootstrap for consistent layout.
A Volvo-inspired color scheme is used (#003057, etc.), with a custom logo in app/static/images/volvo_tlc_hub_logo.png.
Security:
All actions that need a certain role use @role_required("Manager") or others.
For standard authentication, Flask-Login is used with a hashed password approach (werkzeug.security).
