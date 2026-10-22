import os
import json
from flask import Flask, render_template, redirect, url_for, request
from database.config import init_db
from authentication.auth import login_manager
from routes.auth_routes import auth_bp, bcrypt
from routes.prediction_routes import prediction_bp
from flask_login import current_user, login_required

app = Flask(__name__)

# Config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey123')

# Init DB and Auth
init_db()
bcrypt.init_app(app)
login_manager.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(prediction_bp, url_prefix='/api/predictions')

# Register custom Jinja filter (keep for backward compatibility if needed)
@app.template_filter('fromjson')
def fromjson_filter(value):
    try:
        return json.loads(value)
    except:
        return {}

# Vercel Serverless ephemeral file serving (/tmp)
if os.environ.get('VERCEL'):
    from flask import send_from_directory
    @app.route('/static/shap/<path:filename>')
    def serve_tmp_shap(filename):
        return send_from_directory('/tmp/shap', filename)

    @app.route('/static/lime/<path:filename>')
    def serve_tmp_lime(filename):
        return send_from_directory('/tmp/lime', filename)

    @app.route('/static/reports/<path:filename>')
    def serve_tmp_reports(filename):
        return send_from_directory('/tmp/reports', filename)

# ----------------- UI ROUTES -----------------
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html', title='Login')

@app.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('register.html', title='Register')

@app.route('/login')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html', title='Login')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@app.route('/predict')
@login_required
def predict_page():
    return render_template('predict.html', title='New Prediction')

@app.route('/results')
@login_required
def results_page():
    return render_template('results.html', title='Results')

@app.route('/forgot-password')
def forgot_password_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('forgot_password.html', title='Forgot Password')

@app.route('/reset-password')
def reset_password_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('reset_password.html', title='Reset Password')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
