from datetime import datetime
import pandas as pd
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import pytz
from app.utils import role_required
from app.employee import employee
from app.db_setup import db
from app.models.repair import Repair
from app.models.consumable import Consumable
from app.models.elevator import Elevator
from app.models.employee import Employee


# -----------------------------
# Employee Dashboards
# -----------------------------

@employee.route("/manager_dashboard")
@login_required                # Must be logged in
@role_required("Manager")      # Must have role = Manager
def manager_dashboard():
    """
    🏢 Manager dashboard showing quick links to manager functions:
    - Manage Employees
    - Block Elevators
    - Revenue Reports
    """
    return render_template("manager_dashboard.html")

@employee.route("/mechanic_dashboard")
@login_required                # Must be logged in
@role_required("Mechanic")     # Must have role = Mechanic
def mechanic_dashboard():
    """
    🔧 Mechanic Dashboard
    ---------------------
    Displays a list of repairs that are assigned to this mechanic
    (employee_id = current_user.id) and have status 'Approved'
    (or 'In Progress'), depending on your workflow.
    """
    # Only show repairs assigned to the *current_user*
    assigned_repairs = Repair.query.filter_by(
        employee_id=current_user.id
    ).all()

    # You might filter further, e.g. status='Approved' or 'In Progress':
    # assigned_repairs = Repair.query.filter(
    #     Repair.employee_id == current_user.id,
    #     Repair.status.in_(["Approved", "In Progress"])
    # ).all()

    return render_template(
        "mechanic_dashboard.html",
        repairs=assigned_repairs
    )

@employee.route("/receptionist_dashboard")
@login_required                # Must be logged in
@role_required("Receptionist") # Must have role = Receptionist
def receptionist_dashboard():
    """
    📞 Receptionist Dashboard
    -------------------------
    - Displays a list of all 'Pending' repairs which need approval.
    - Receptionist can either approve these repairs or reschedule them.
      via different buttons.

    Returns:
        - A template that shows pending repairs with 'Approve' and 'Reschedule' options.
    """
    # Query all repairs that are currently in 'Pending' status.
    pending_repairs = Repair.query.filter_by(status="Pending").all()

    # Render a template listing these pending repairs.
    return render_template("receptionist_dashboard.html", repairs=pending_repairs)

@employee.route("/stockkeeper_dashboard")
@login_required                # Must be logged in
@role_required("StockKeeper")  # Must have role = StockKeeper
def stockkeeper_dashboard():
    """
    📦 StockKeeper Dashboard
    ------------------------
    Displays an overview of the consumables stock. Provides links to check low stock
    or manually replenish items.
    """
    # For a simple approach, list all consumables so the user can see the entire inventory.
    consumables = Consumable.query.all()

    # Render a template that shows the current stock
    return render_template("stockkeeper_dashboard.html", consumables=consumables)

@employee.route('/dashboard')
@login_required
def dashboard():
    """Employee dashboard displaying role-based functionalities."""
    return render_template('employee_dashboard.html')

# -----------------------------
# Revenue Report (Manager Only)
# -----------------------------

@employee.route("/revenue_report")
@login_required
@role_required("Manager")
def revenue_report():
    """
    💰 Manager route to generate a basic revenue report using pandas + numpy.
    - Summation of 'cost' from completed repairs.
    """
    repairs = Repair.query.filter(Repair.cost != None).all()
    if not repairs:
        flash("No completed repairs yet. No revenue data.", "info")
        return redirect(url_for("employee.manager_dashboard"))

    # Convert repairs to a DataFrame
    data = [
        {
            "repair_id": r.id,
            "cost": r.cost,
            "status": r.status,
            "date": r.scheduled_date
        }
        for r in repairs
    ]
    df = pd.DataFrame(data)

    # Example revenue calculation
    total_revenue = df["cost"].sum()  # sum of all costs

    # Group by status for demonstration
    group_status = df.groupby("status")["cost"].sum().to_dict()

    return render_template(
        "revenue_report.html",
        total_revenue=total_revenue,
        group_status=group_status
    )

# -----------------------------
# Repair Management (Receptionist & Mechanic)
# -----------------------------

@employee.route("/approve_repair/<int:repair_id>", methods=["POST"])
@login_required
@role_required("Receptionist")
def approve_repair(repair_id):
    """✅ Approve a Pending Repair
    ---------------------------
    - Route for Receptionist to approve a repair, changing status from 'Pending' to 'Approved'.
    - Expects a POST request with no additional data except the route param.

    Args:
        repair_id (int): The unique ID of the repair in the database.

    Returns:
        Redirect back to 'receptionist_dashboard' with a success message,
        or an error if something goes wrong."""
    # Fetch the repair to be approved
    repair = Repair.query.get_or_404(repair_id)

    # Update the status
    repair.status = "Approved"
    db.session.commit()

    flash(f"Repair #{repair_id} has been approved successfully!", "success")
    return redirect(url_for("employee.receptionist_dashboard"))

@employee.route("/reschedule_repair/<int:repair_id>", methods=["GET", "POST"])
@login_required
@role_required("Receptionist")
def reschedule_repair(repair_id):
    """
    🗓️ Reschedule a Repair
    ----------------------
    - Allows the Receptionist to change the date/time and elevator assignment of a given repair.
    - GET request: Show a form with current repair details and available elevators.
    - POST request: Saves new date/elevator, updates the old elevator to 'Available'.

    Args:
        repair_id (int): The unique ID of the repair in the database.

    Returns:
        If GET: Renders 'reschedule_repair.html' with a form.
        If POST: Updates DB, redirects to 'receptionist_dashboard'.
    """
    # Attempt to find the repair by ID, or 404 if not found
    repair = Repair.query.get_or_404(repair_id)

    if request.method == "POST":
        # Retrieve new date and elevator ID from form
        new_date_str = request.form.get("new_date")
        new_elevator_id = request.form.get("elevator_id")

        # Validate the input
        if not new_date_str or not new_elevator_id:
            flash("Both new date and elevator selection are required.", "error")
            return redirect(url_for("employee.reschedule_repair", repair_id=repair_id))

        # Convert the new date from string (YYYY-MM-DD) to a datetime object
        # using Europe's Bucharest timezone for example
        eet = pytz.timezone("Europe/Bucharest")
        try:
            dt_obj = datetime.strptime(new_date_str, "%Y-%m-%d")
            dt_obj = eet.localize(dt_obj)
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "error")
            return redirect(url_for("employee.reschedule_repair", repair_id=repair_id))

        # Free up the old elevator (set status back to 'Available') if needed
        old_elevator = Elevator.query.get(repair.elevator_id)
        if old_elevator:
            old_elevator.status = "Available"

        # Mark the new elevator as 'Occupied'
        new_elevator = Elevator.query.get(new_elevator_id)
        if not new_elevator:
            flash("Selected elevator not found.", "error")
            return redirect(url_for("employee.reschedule_repair", repair_id=repair_id))

        # If the new elevator is not 'Available', we cannot assign it
        if new_elevator.status != "Available":
            flash(f"Elevator #{new_elevator.id} is not available!", "error")
            # Revert the old elevator status if needed
            if old_elevator:
                old_elevator.status = "Occupied"  # or whatever it was
            return redirect(url_for("employee.reschedule_repair", repair_id=repair_id))

        # Occupy the new elevator
        new_elevator.status = "Occupied"

        # Update the repair's date and elevator
        repair.scheduled_date = dt_obj
        repair.elevator_id = new_elevator.id

        # Optionally reset the status if you'd like to mark it 'Pending' again,
        # or keep it 'Approved' if it was already approved. Up to your business logic.
        if repair.status in ["Pending", "Approved"]:
            repair.status = "Pending"  # or keep 'Approved' if you prefer

        # Commit all changes
        db.session.commit()

        flash(f"Repair #{repair_id} rescheduled successfully!", "success")
        return redirect(url_for("employee.receptionist_dashboard"))

    # If GET request, fetch all available elevators for the user to choose from
    available_elevators = Elevator.query.filter_by(status="Available").all()

    # Render a template with a form to pick the new date and elevator
    return render_template(
        "reschedule_repair.html",
        repair=repair,
        elevators=available_elevators
    )

@employee.route("/assign_mechanic/<int:repair_id>", methods=["GET", "POST"])
@login_required
@role_required("Receptionist")
def assign_mechanic(repair_id):
    """
    🔧 Assign Mechanic to a Repair
    -----------------------------
    Receptionist picks which mechanic will handle the repair.
    That sets repair.employee_id = chosen mechanic's id,
    so it appears on that mechanic's dashboard.

    GET:
      - Show a form listing all Mechanic employees + repair info.
    POST:
      - Set repair.employee_id to the chosen mechanic, status => 'In Progress' or 'Approved'.
    """
    from app.models.repair import Repair
    from app.models.employee import Employee

    repair = Repair.query.get_or_404(repair_id)

    if request.method == "POST":
        mechanic_id = request.form.get("mechanic_id")
        if not mechanic_id:
            flash("Mechanic is required!", "error")
            return redirect(url_for("employee.assign_mechanic", repair_id=repair.id))

        # Make sure the chosen employee is actually a Mechanic role
        mechanic = Employee.query.filter_by(id=mechanic_id, role="Mechanic").first()
        if not mechanic:
            flash("Selected user is not a mechanic!", "error")
            return redirect(url_for("employee.assign_mechanic", repair_id=repair.id))

        # Assign repair to this mechanic
        repair.employee_id = mechanic.id
        # Optionally set status to 'In Progress' or keep 'Approved'
        if repair.status == "Pending":
            repair.status = "Approved"  # or "In Progress"
        db.session.commit()

        flash(f"Repair #{repair.id} is now assigned to mechanic {mechanic.name}.", "success")
        return redirect(url_for("employee.receptionist_dashboard"))

    # GET request: show a list of mechanics
    mechanics = Employee.query.filter_by(role="Mechanic").all()

    return render_template("assign_mechanic.html", repair=repair, mechanics=mechanics)


@employee.route("/assign_to_mechanic/<int:repair_id>", methods=["POST"])
@login_required
@role_required("Mechanic")
def assign_to_mechanic(repair_id):
    """
    🚀 Assign Repair to Mechanic
    ---------------------------
    If your flow doesn't automatically set employee_id,
    you might let the Mechanic 'claim' a repair to themselves.
    This route sets employee_id = current_user.id for that repair
    if it's unassigned, then sets 'In Progress' or 'Approved'.

    Args:
        repair_id (int): The ID of the repair to claim.

    Returns:
        Redirects back to mechanic_dashboard with success or error message.
    """
    repair = Repair.query.get_or_404(repair_id)
    if repair.employee_id is not None and repair.employee_id != current_user.id:
        flash("Another mechanic is already assigned to this repair!", "error")
        return redirect(url_for("employee.mechanic_dashboard"))

    # Assign this repair to the current mechanic
    repair.employee_id = current_user.id
    # Optionally mark it 'In Progress'
    repair.status = "In Progress"
    db.session.commit()

    flash(f"Repair #{repair_id} is now assigned to you.", "success")
    return redirect(url_for("employee.mechanic_dashboard"))

@employee.route("/complete_repair/<int:repair_id>", methods=["POST"])
@login_required
@role_required("Mechanic")
def complete_repair(repair_id):
    """
    ✅ Complete a Repair
    --------------------
    Mechanic marks the repair as 'Completed', optionally updating
    cost or billing details if the system requires it.
    Also frees the elevator to 'Available' again (if that is the workflow).

    Args:
        repair_id (int): The repair ID to mark complete.

    Returns:
        Redirect to mechanic_dashboard with success message.
    """
    repair = Repair.query.get_or_404(repair_id)

    # Verify the current mechanic is assigned to this repair
    if repair.employee_id != current_user.id:
        flash("You are not assigned to this repair!", "error")
        return redirect(url_for("employee.mechanic_dashboard"))

    # Mark the repair as 'Completed'
    repair.status = "Completed"
    # Optionally record a completion date or cost
    repair.cost = repair.cost or 100.0  # as an example
    # If you have a 'completion_date' field, set it:
    # repair.completion_date = datetime.utcnow()

    # Free the elevator
    elevator = Elevator.query.get(repair.elevator_id)
    if elevator:
        elevator.status = "Available"

    db.session.commit()
    flash(f"Repair #{repair_id} has been marked Completed.", "success")
    return redirect(url_for("employee.mechanic_dashboard"))

@employee.route("/update_parts_used/<int:repair_id>", methods=["GET", "POST"])
@login_required
@role_required("Mechanic")
def update_parts_used(repair_id):
    """
    📝 Update Parts Used
    --------------------
    Allows the mechanic to record which parts or consumables were used
    during the repair (e.g., 'Oil filter, Spark plugs').

    GET:
      - Show a form with a text field for parts used.
    POST:
      - Save the parts used to 'billing_details' or a dedicated field
        in the 'Repair' model, then commit changes.

    Args:
        repair_id (int): The repair to update.

    Returns:
        On GET: Renders a form.
        On POST: Saves changes, redirect to mechanic dashboard.
    """
    repair = Repair.query.get_or_404(repair_id)

    # Ensure only the assigned mechanic can update
    if repair.employee_id != current_user.id:
        flash("You are not assigned to this repair!", "error")
        return redirect(url_for("employee.mechanic_dashboard"))

    if request.method == "POST":
        parts_used = request.form.get("parts_used")
        if not parts_used:
            flash("Please enter the parts used.", "error")
            return redirect(url_for("employee.update_parts_used", repair_id=repair_id))

        # In this example, we reuse 'billing_details' to store parts used
        # or you can add a new column to your Repair model for 'parts_used'.
        repair.billing_details = f"Parts Used: {parts_used}"
        db.session.commit()

        flash(f"Parts used recorded for repair #{repair.id}.", "success")
        return redirect(url_for("employee.mechanic_dashboard"))

    # If GET, show a form
    return render_template("update_parts_used.html", repair=repair)

# -----------------------------
# Employee Management (Manager)
# -----------------------------

@employee.route("/manage_employee", methods=["GET", "POST"])
@login_required
@role_required("Manager")
def manage_employee():
    """
    👥 Allows the manager to view, create, or delete employees.
    - On GET: Show a list of employees & a form to create a new one.
    - On POST: Create or delete employees based on form submission.
    """
    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            name = request.form.get("name")
            email = request.form.get("email")
            role = request.form.get("role")
            salary = float(request.form.get("salary", 0.0))
            from werkzeug.security import generate_password_hash
            password = generate_password_hash(
                request.form.get("password"), method="scrypt"
            )

            new_emp = Employee(
                name=name,
                email=email,
                role=role,
                salary=salary,
                employment_date=datetime.now(),
                password=password,
                department="Operations"  # or from form
            )
            db.session.add(new_emp)
            db.session.commit()
            flash("✅ New employee created successfully!", "success")
            return redirect(url_for("employee.manage_employee"))

        elif action == "delete":
            emp_id = request.form.get("employee_id")
            emp = Employee.query.get(emp_id)
            if emp:
                db.session.delete(emp)
                db.session.commit()
                flash(f"Employee {emp.name} removed.", "info")
            return redirect(url_for("employee.manage_employee"))

    # If GET request, list all employees
    employees = Employee.query.all()
    return render_template("manage_employee.html", employees=employees)

# -----------------------------
# Elevator Management (Manager)
# -----------------------------

@employee.route("/block_elevator", methods=["GET", "POST"])
@login_required
@role_required("Manager")
def block_elevator():
    """
    🚧 Allows manager to block an elevator for a certain duration,
    marking it as 'Occupied' or 'Maintenance' so no new repairs can use it.
    """
    if request.method == "POST":
        elevator_id = request.form.get("elevator_id")
        duration = request.form.get("duration")  # half_day, full_day, etc.

        elevator = Elevator.query.get(elevator_id)
        if not elevator:
            flash("Elevator not found!", "error")
            return redirect(url_for("employee.block_elevator"))

        if duration == "half_day":
            # Just as an example, we set status = 'Maintenance'
            elevator.status = "Maintenance"
            # Optionally track a time when it becomes available again
        elif duration == "full_day":
            elevator.status = "Maintenance"
        elif duration == "week":
            elevator.status = "Maintenance"
        elif duration == "month":
            elevator.status = "Maintenance"
        else:
            flash("Invalid duration selected.", "error")
            return redirect(url_for("employee.block_elevator"))

        db.session.commit()
        flash(f"Elevator {elevator.id} blocked for {duration}.", "success")
        return redirect(url_for("employee.block_elevator"))

    # GET request: show a form to select an elevator, choose a duration
    elevators = Elevator.query.all()
    return render_template("block_elevator.html", elevators=elevators)

@employee.route("/unblock_elevator", methods=["GET", "POST"])
@login_required
@role_required("Manager")
def unblock_elevator():
    """
    🔓 Unblock Elevator
    ------------------
    Allows the Manager to set an elevator's status back to 'Available'.
    This can be used after it was blocked for maintenance or a set duration.

    GET:
      - List all elevators that are not 'Available'.
    POST:
      - Sets the chosen elevator's status to 'Available'.
    """
    from app.models.elevator import Elevator

    if request.method == "POST":
        elevator_id = request.form.get("elevator_id")
        elevator = Elevator.query.get(elevator_id)

        if not elevator:
            flash("Elevator not found!", "error")
            return redirect(url_for("employee.unblock_elevator"))

        # Set status back to 'Available'
        elevator.status = "Available"
        db.session.commit()

        flash(f"Elevator {elevator.id} is now unblocked (Available).", "success")
        return redirect(url_for("employee.unblock_elevator"))

    # If GET, fetch all elevators that are not 'Available'
    blocked_elevators = Elevator.query.filter(Elevator.status != "Available").all()
    return render_template("unblock_elevator.html", elevators=blocked_elevators)

# -----------------------------
# Stock Management (StockKeeper)
# -----------------------------

@employee.route("/check_stock")
@login_required
@role_required("StockKeeper")
def check_stock():
    """
    🔎 Check Stock for Low Items
    ----------------------------
    Finds consumables below their threshold, prompting the StockKeeper
    to replenish them.
    """
    # Query all consumables whose quantity <= threshold
    low_stock_items = Consumable.query.filter(Consumable.quantity <= Consumable.threshold).all()

    return render_template("low_stock_alerts.html", low_stock_items=low_stock_items)


@employee.route("/replenish_stock/<int:consumable_id>", methods=["POST"])
@login_required
@role_required("StockKeeper")
def replenish_stock(consumable_id):
    """
    🔄 Replenish a Specific Consumable
    ----------------------------------
    Increases the quantity of a consumable by a fixed reorder amount,
    or a user-specified amount.
    This route expects a POST with 'reorder_amount' or uses a default.

    Args:
        consumable_id (int): The ID of the consumable to replenish.
    """
    consumable = Consumable.query.get_or_404(consumable_id)

    # Let’s assume we have a hidden field or a standard reorder increment
    reorder_str = request.form.get("reorder_amount", "10")  # default 10
    try:
        reorder_amount = int(reorder_str)
    except ValueError:
        reorder_amount = 10

    # Increase the quantity
    consumable.quantity += reorder_amount
    db.session.commit()

    flash(f"{consumable.name} stock replenished by {reorder_amount} units.", "success")
    return redirect(url_for("employee.stockkeeper_dashboard"))

@employee.route("/mass_replenish", methods=["POST"])
@login_required
@role_required("StockKeeper")
def mass_replenish():
    """
    🚚 Mass Replenish All Low-Stock Items
    -------------------------------------
    Example route: Finds all low-stock consumables and replenishes
    each by a default reorder amount or the 'reorder_amount' column
    in the Consumable model.
    """
    low_stock_items = Consumable.query.filter(Consumable.quantity <= Consumable.threshold).all()

    for item in low_stock_items:
        # Suppose each item has a reorder_amount field
        item.quantity +=  item.threshold  # or item.reorder_amount
    db.session.commit()

    flash(f"All low-stock items have been replenished!", "success")
    return redirect(url_for("employee.stockkeeper_dashboard"))