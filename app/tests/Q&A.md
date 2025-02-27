2. Potential Q&A
Below are some common questions you might face when presenting the code, alongside short, direct answers:

Q: How does Flask handle user authentication here?
A: We use Flask-Login. Each user (client or employee) has a database record. On login, we verify the hashed password using check_password_hash. Once authenticated, Flask-Login sets a session cookie. We define @login_required to protect routes.

Q: What is @role_required in utils.py?
A: It's a decorator that checks if current_user.role matches the required role (e.g., “Manager,” “Mechanic,” etc.). If the user doesn’t match, it redirects to the login page with an error message.

Q: How do you ensure that each employee type is treated differently?
A: We use polymorphic inheritance in employee.py. The base Employee model has a role field, and each subclass (Manager, Mechanic, etc.) sets polymorphic_identity accordingly.

Q: Where is the database stored?
A: It’s located in the instance/ folder as volvo_tlc_hub.db, created by SQLAlchemy. The path is configured in db_setup.py.

Q: What happens if a client schedules a repair on an occupied elevator?
A: In schedule_repair logic (main/routes.py), we check the elevator’s status. If it’s not “Available,” we flash an error and stop the process.

Q: How do you seed initial data?
A: Two scripts handle seeding:

manual_db_create.py: Seeds elevators if none exist.
manual_add_employee.py: Seeds employees if none exist.
Q: Where do we see usage of OOP?
A: OOP is visible in the employee inheritance structure, the decorator approach, and the general blueprint pattern for routes. We also have a separate utils.py for decorators, ensuring modular code.

Q: Why do we use a blueprint for employee routes?
A: Blueprints keep code modular. We separate concerns: auth for authentication, main for client-facing routes, employee for staff dashboards. This improves readability and maintainability.

Q: Where could we integrate Numpy/Pandas further?
A: For report generation. For instance, the Manager might generate a monthly revenue or stock usage report by reading data from the DB, using pandas to create DataFrames, and possibly exporting to CSV. Currently, placeholders or partial code can illustrate this.

Q: How is password hashing implemented?
A: We use werkzeug.security’s generate_password_hash and check_password_hash functions. On registration, the password is stored in hashed form. On login, we compare the hash with the input.

