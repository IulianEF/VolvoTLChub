# app/main/routes.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.main import main
from app.db_setup import db
from app.models.repair import Repair
from app.models.elevator import Elevator
from datetime import datetime
import pytz

@main.route("/")
def index():
    """
    🏠 Home page: If user is logged in and a client, show repair history;
    otherwise, show a general welcome page.
    """
    if current_user.is_authenticated and not getattr(current_user, "role", None):
        # Assume a client
        repairs = Repair.query.filter_by(client_id=current_user.id).all()
        return render_template("index.html", repairs=repairs)
    return render_template("index.html", repairs=None)

@main.route("/schedule_repair", methods=["GET", "POST"])
@login_required
def schedule_repair():
    """
    📅 Allows a logged-in client to schedule a repair by selecting an elevator.
    """
    if getattr(current_user, "role", None):
        # If the user is an employee, not a client
        flash("Clients only: Employees cannot schedule repairs here.", "error")
        return redirect(url_for("main.index"))

    # Elevator availability
    available_elevators = Elevator.query.filter_by(status="Available").all()
    if request.method == "POST":
        description = request.form.get("description")
        scheduled_date = request.form.get("scheduled_date")
        elevator_id = request.form.get("elevator_id")
        if not all([description, scheduled_date, elevator_id]):
            flash("All fields are required.", "error")
            return redirect(url_for("main.schedule_repair"))

        # Convert date string to datetime
        eet = pytz.timezone("Europe/Bucharest")
        dt_obj = datetime.strptime(scheduled_date, "%Y-%m-%d")
        dt_obj = eet.localize(dt_obj)

        elevator = Elevator.query.get(elevator_id)
        if elevator.status != "Available":
            flash("Elevator is not available!", "error")
            return redirect(url_for("main.schedule_repair"))

        # Reserve elevator
        elevator.status = "Occupied"
        new_repair = Repair(
            client_id=current_user.id,
            elevator_id=elevator.id,
            description=description,
            scheduled_date=dt_obj,
            status="Pending"
        )
        db.session.add(new_repair)
        db.session.commit()
        flash("Repair scheduled successfully!", "success")
        return redirect(url_for("main.index"))

    return render_template("schedule_repair.html", elevators=available_elevators)


@main.route('/home_redirect')
def home_redirect():
    """
    👀 Decides where to send the user when the brand is clicked:
        - If not logged in, go to the home page.
        - If logged in (employee), go to role-based dashboard.
        - If logged in (client), go to index or repair history.
    """
    if not current_user.is_authenticated:
        # Not logged in → show the default home page
        return redirect(url_for('main.index'))

    # If user is logged in, check if they have a 'role' attribute
    user_role = getattr(current_user, 'role', None)
    if user_role == 'Manager':
        return redirect(url_for('employee.manager_dashboard'))
    elif user_role == 'Receptionist':
        return redirect(url_for('employee.receptionist_dashboard'))
    elif user_role == 'Mechanic':
        return redirect(url_for('employee.mechanic_dashboard'))
    elif user_role == 'StockKeeper':
        return redirect(url_for('employee.stockkeeper_dashboard'))
    else:
        # If it's a client (no 'role' attribute), just go to index
        return redirect(url_for('main.index'))

@main.route('/client_dashboard')
@login_required
def client_dashboard():
    """
    🏠 Client Dashboard:
    - Shows client's profile info.
    - Lists repair history.
    - Allows quick link to schedule a repair.
    """
    # If the user is an employee, redirect them away.
    user_role = getattr(current_user, 'role', None)
    if user_role:
        flash("This dashboard is for clients only!", "error")
        return redirect(url_for('main.index'))

    # The current_user is a client: gather repair history
    repairs = Repair.query.filter_by(client_id=current_user.id).all()
    return render_template('client_dashboard.html', repairs=repairs)