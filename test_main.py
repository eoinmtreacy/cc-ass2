import pytest
from user_service.main import app, db, User

# FILE: user-service/test_main.py


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

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