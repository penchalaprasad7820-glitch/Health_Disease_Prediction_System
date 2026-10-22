from flask import Blueprint, request, jsonify, redirect, current_app
from itsdangerous import URLSafeTimedSerializer
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
import mongoengine
from database.config import dump_mock_db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def is_valid_email(email_str):
    if not email_str or not isinstance(email_str, str):
        return False
    email_str = email_str.strip()
    if len(email_str) > 254:
        return False
    return bool(EMAIL_REGEX.match(email_str))

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    role = data.get('role', 'User')
    
    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400
        
    if not is_valid_email(email):
        return jsonify({"error": "Please enter a valid email address (e.g., name@example.com)"}), 400
        
    try:
        if User.objects(email=email).first():
            return jsonify({"error": "An account with that email already exists"}), 400
            
        if User.objects(username=username).first():
            return jsonify({"error": "An account with that username already exists"}), 400
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password, role=role)
        user.save()
        dump_mock_db()
        
        return jsonify({"message": "User registered successfully"}), 201
    except mongoengine.errors.ValidationError:
        return jsonify({"error": "Invalid email address format"}), 400
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
        
    if not is_valid_email(email):
        return jsonify({"error": "Please enter a valid email address format"}), 400
        
    try:
        user = User.objects(email=email).first()
        
        if not user:
            return jsonify({"error": "No account found with that email address"}), 404
            
        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({"error": "Incorrect password. Please try again."}), 401
            
        login_user(user, remember=data.get('remember', False))
        return jsonify({
            "message": "Logged in successfully",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }), 200
        
        return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": "Database connection failed. Please check your MongoDB Atlas setup in .env"}), 500

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/')

@auth_bp.route('/user', methods=['GET'])
@login_required
def get_user():
    return jsonify({
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }), 200

import random
import datetime

def generate_otp():
    return str(random.randint(100000, 999999))

def send_real_email(to_email, otp, base_url='http://localhost:5000'):
    sender_email = os.environ.get('MAIL_USERNAME')
    sender_password = os.environ.get('MAIL_PASSWORD')
    
    if not sender_email or not sender_password:
        return False # No credentials configured
        
    try:
        reset_link = f"{base_url}/reset-password?email={to_email}&otp={otp}"
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"Disease Prediction System <{sender_email}>"
        msg['To'] = to_email
        msg['Subject'] = "Direct Password Recovery - Disease Prediction System"
        
        text_body = f"""Hello,

You requested a password reset for your Disease Prediction System account.

Click the direct recovery link below to reset your password:
{reset_link}

Or enter your 6-digit OTP code manually:
OTP: {otp}

This link and code will expire in 15 minutes.
If you did not request this, please ignore this email.
"""
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 25px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #0d6efd; margin: 0;">Disease Prediction System</h2>
                <p style="color: #64748b; font-size: 14px;">Secure Account Password Recovery</p>
            </div>
            <p style="color: #334155; font-size: 16px;">Hello,</p>
            <p style="color: #334155; font-size: 15px; line-height: 1.5;">
                We received a request to recover the password for your account. You can directly reset your password by clicking the button below:
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" style="background-color: #0d6efd; color: #ffffff; padding: 14px 28px; text-decoration: none; font-size: 16px; font-weight: bold; border-radius: 8px; display: inline-block;">Reset Password Now</a>
            </div>
            <div style="background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                <p style="margin: 0; color: #64748b; font-size: 13px;">Or use this 6-digit OTP code manually:</p>
                <p style="margin: 5px 0 0; font-size: 26px; font-weight: bold; letter-spacing: 4px; color: #0f172a;">{otp}</p>
            </div>
            <p style="color: #94a3b8; font-size: 12px; line-height: 1.4;">
                This recovery link and OTP are valid for <strong>15 minutes</strong>. If you did not request this password reset, no action is required and you can safely ignore this email.
            </p>
        </div>
        """
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Please enter a valid email address (e.g. name@example.com)"}), 400
        
    user = User.objects(email=email).first()
    if not user:
        return jsonify({"error": "No account found with that email address"}), 404
        
    email_sent = False
    otp = None
    
    if user:
        otp = generate_otp()
        user.reset_otp = otp
        user.reset_otp_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        user.save()
        dump_mock_db()
        
        # Try to send a real email first with the direct recovery link
        base_url = request.host_url.rstrip('/')
        email_sent = send_real_email(email, otp, base_url=base_url)
        
        # If it failed or credentials are missing, fallback to console mock
        if not email_sent:
            print(f"\n\n--- MOCK EMAIL ---", flush=True)
            print(f"To: {email}", flush=True)
            print(f"Subject: Your Password Reset OTP", flush=True)
            print(f"Your OTP is: {otp}", flush=True)
            print(f"------------------\n\n", flush=True)
            
    if email_sent:
        return jsonify({
            "message": "If an account with that email exists, an OTP has been sent to your email inbox."
        }), 200
    else:
        return jsonify({
            "message": "If an account with that email exists, an OTP has been generated.",
            "dev_otp": otp
        }), 200

@auth_bp.route('/verify-reset-otp', methods=['POST'])
def verify_reset_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    password = data.get('password')
    
    if not email or not otp or not password:
        return jsonify({"error": "Email, OTP, and Password are required"}), 400
        
    user = User.objects(email=email).first()
    if not user:
        return jsonify({"error": "Invalid email or OTP"}), 400
        
    if user.reset_otp != otp:
        return jsonify({"error": "Invalid OTP"}), 400
        
    if user.reset_otp_expiry and datetime.datetime.utcnow() > user.reset_otp_expiry:
        return jsonify({"error": "OTP has expired"}), 400
        
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user.password = hashed_password
    user.reset_otp = None
    user.reset_otp_expiry = None
    user.save()
    dump_mock_db()
    
    return jsonify({"message": "Your password has been updated! You are now able to log in"}), 200
