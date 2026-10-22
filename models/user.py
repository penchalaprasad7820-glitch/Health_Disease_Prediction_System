from mongoengine import Document, StringField, EmailField, DateTimeField
import datetime
from flask_login import UserMixin

class User(Document, UserMixin):
    username = StringField(required=True, unique=True, max_length=150)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(required=True, default='User', choices=('User', 'Doctor', 'Admin'))
    date_created = DateTimeField(default=datetime.datetime.utcnow)
    reset_otp = StringField(null=True)
    reset_otp_expiry = DateTimeField(null=True)
    
    meta = {'collection': 'users'}
    
    def get_id(self):
        return str(self.id)
