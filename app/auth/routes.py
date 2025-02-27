from flask import render_template, request, redirect, url_for, flash, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app.db_setup import db
from app.models.client import Client
from app.auth import auth
# import pytz # East European Timezone support

# Blueprint for authentication
# auth = Blueprint('auth', __name__)
# eet = pytz.timezone('Europe/Bucharest')  # East European Time (Winter)

# Regex patterns
# PHONE_REGEX = r'^\\+?1?\\d{9,15}$'
# VIN_REGEX = r'^[A-HJ-NPR-Z0-9]{17}$'

# Client Registration Route


@auth.route("/register", methods=["GET", "POST"])
def register():
    """📝 Handles client registration with hashed passwords."""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")
        address = request.form.get("address")
        vin_number = request.form.get("vin_number")
        car_model = request.form.get("car_model")

        # Check if user already exists
        existing_user = Client.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.", "error")
            return redirect(url_for("auth.register"))

        hashed_pw = generate_password_hash(password, method="scrypt")
        new_client = Client(
            name=name,
            email=email,
            password=hashed_pw,
            phone_number=phone,
            address=address,
            vin_number=vin_number,
            car_model=car_model
        )
        db.session.add(new_client)
        db.session.commit()

        flash("Account created successfully! ✅", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """🔐 Authenticates clients or employees with hashed password check."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        from app.models.employee import Employee
        user = Client.query.filter_by(email=email).first() or Employee.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            #print(f"DEBUG: Logged in user = {user}, role={getattr(user, 'role', None)}")

            flash("Logged in successfully!", "success")

            # If user is an employee, redirect by role
            role = getattr(user, "role", None)
            if role == "Manager":
                return redirect(url_for("employee.manager_dashboard"))
            elif role == "Receptionist":
                return redirect(url_for("employee.receptionist_dashboard"))
            elif role == "Mechanic":
                return redirect(url_for("employee.mechanic_dashboard"))
            elif role == "StockKeeper":
                return redirect(url_for("employee.stockkeeper_dashboard"))
            else:
                # Default: assume it's a client
                return redirect(url_for("main.index"))
        else:
            flash("Invalid credentials. Please try again.", "error")

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    """🚪 Logs out the current user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))