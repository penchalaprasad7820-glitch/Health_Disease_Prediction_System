import pytest
from app import app, db, User
from flask_bcrypt import Bcrypt

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            bcrypt = Bcrypt(app)
            # Create test user
            hashed_pw = bcrypt.generate_password_hash('password').decode('utf-8')
            user = User(username='testuser', email='test@example.com', password=hashed_pw, role='User')
            doctor = User(username='testdoc', email='doc@example.com', password=hashed_pw, role='Doctor')
            db.session.add_all([user, doctor])
            db.session.commit()
            
        yield client
        
        with app.app_context():
            db.drop_all()

def test_index_redirects_to_login(client):
    response = client.get('/')
    assert b'Login' in response.data

def test_login_logout(client):
    # Login
    response = client.post('/login', data=dict(
        email='test@example.com',
        password='password'
    ), follow_redirects=True)
    assert b'Dashboard' in response.data
    
    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert b'Login' in response.data

def test_predict_route_requires_doctor(client):
    # Login as User
    client.post('/login', data=dict(
        email='test@example.com',
        password='password'
    ), follow_redirects=True)
    
    # Try accessing predict route
    response = client.get('/predict', follow_redirects=True)
    assert b'Doctor access required' in response.data
    
    # Logout and login as doctor
    client.get('/logout')
    client.post('/login', data=dict(
        email='doc@example.com',
        password='password'
    ), follow_redirects=True)
    
    response = client.get('/predict')
    assert b'New Prediction' in response.data
