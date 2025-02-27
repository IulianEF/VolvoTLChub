#This file includes role-based access decorators and any helper functions required across the app.


from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def role_required(role):
    """
    🎭 Decorator to ensure a user has the required role.
    - Redirects unauthorized users to the login page with an error message.

    Args:
        role (str): Required role name for access.
    """

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            #print("DEBUG in role_required:", current_user, current_user.role)
            if not current_user.is_authenticated or current_user.role != role:
                flash("You do not have permission...", "error")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return wrapped
    return decorator
