from functools import wraps
from flask import session, jsonify
from .models import Role, User # Assuming User might be needed for more complex checks later, Role is essential now

def roles_required(required_role_names):
    """
    Decorator to ensure a user is logged in and has one of the required roles.
    Args:
        required_role_names (list): A list of role names that are allowed to access the endpoint.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or 'role_id' not in session:
                return jsonify({'error': 'Authentication required.'}), 401

            role_id = session['role_id']
            role = Role.query.get(role_id)

            if not role:
                # This case should ideally not happen if session data is consistent with DB
                return jsonify({'error': 'Invalid role ID in session.'}), 401

            if role.RoleName not in required_role_names:
                return jsonify({'error': f"Forbidden: Access requires one of the following roles: {', '.join(required_role_names)}."}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
