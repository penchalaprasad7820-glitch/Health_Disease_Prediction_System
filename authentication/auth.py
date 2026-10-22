from flask_login import LoginManager, UserMixin
from functools import wraps
from flask import jsonify, request, redirect
from flask_login import current_user
from models.user import User

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({"error": "Unauthorized"}), 401
    return redirect('/login')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['Admin', 'Doctor']:
            return jsonify({"error": "Doctor access required"}), 403
        return f(*args, **kwargs)
    return decorated_function
