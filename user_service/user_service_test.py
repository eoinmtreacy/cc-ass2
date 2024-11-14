import pytest
from user_service.main import app, db
import dotenv
import os

dotenv.load_dotenv()

db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

# FILE: user-service/test_main.py


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

### /users/all TEST ###

def test_get_users_empty(client):
    response = client.get('/users/all')
    assert response.status_code == 200
    assert response.json == []

def test_get_users(client):
    client.post('/users/add', json={
        'studentid': '1',
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    response = client.get('/users/all')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['studentid'] == '1'

### /users/add ###

def test_create_user(client):
    response = client.post('/users/add', json={
        'studentid': '1',
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    assert response.status_code == 201
    assert response.json['studentid'] == '1'
    assert response.json['firstname'] == 'John'
    assert response.json['lastname'] == 'Doe'
    assert response.json['email'] == 'john.doe@example.com'

def test_create_user_duplicate_email(client):
    client.post('/users/add', json={
        'studentid': '1',
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    response = client.post('/users/add', json={
        'studentid': '2',
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': 'john.doe@example.com'
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Email already exists'

def test_create_user_duplicate_studentid(client):
    client.post('/users/add', json={
        'studentid': '1',
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    response = client.post('/users/add', json={
        'studentid': '1',
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': 'jane.smith@example.com'
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Student ID already exists'

### /users/<studentid> TESTS ###
    ### GET METHODS

def test_get_user(client):
    client.post('/users/add', json={
        'studentid': '1',
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    response = client.get('/users/1')
    assert response.status_code == 200
    assert response.json['studentid'] == '1'

def test_get_user_not_found(client):
    response = client.get('/users/1')
    assert response.status_code == 404
    assert response.json['error'] == 'User not found'

    ### PUT METHODS

def test_update_user(client):
    client.post('/users/add', json={
        'studentid': '1',
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    response = client.put('/users/1', json={
        'firstname': 'Jane'
    })
    assert response.status_code == 200
    assert response.json['firstname'] == 'Jane'

def test_update_user_not_found(client):
    response = client.put('/users/1', json={
        'firstname': 'Jane'
    })
    assert response.status_code == 404
    assert response.json['error'] == 'User not found'

def test_create_user_duplicate_email(client):
    client.post('/users/add', json={
        'studentid': '1',
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    client.post('/users/add', json={
        'studentid': '2',
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': 'jane.smith@example.com'
    })
    response = client.put('/users/2', json={
        'email': 'john.doe@example.com'
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Email already exists'

def test_update_user_duplicate_studentid(client):
    client.post('/users/add', json={
        'studentid': '1',
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    client.post('/users/add', json={
        'studentid': '2',
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': 'jane.smith@example.com'
    })
    response = client.put('/users/2', json={
        'studentid': '1'
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Student ID already exists'

    ### DELETE METHODS

def test_delete_user(client):
    client.post('/users/add', json={
        'studentid': '1',
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    response = client.delete('/users/1')
    assert response.status_code == 200
    assert response.json['message'] == 'User deleted successfully'

def test_delete_user_not_found(client):
    response = client.delete('/users/1')
    assert response.status_code == 404
    assert response.json['error'] == 'User not found'
