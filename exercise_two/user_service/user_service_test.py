import pytest
import requests
import os
import random

base_url = 'http://localhost:5002'

@pytest.fixture
def random_studentid():
    return str(random.randint(1000, 999999999999))

### /users/borrow/request TEST ###

def test_borrow_book_success(random_studentid):
    response = requests.post(f'{base_url}/users/borrow/request', json={
        'studentid': random_studentid,
        'bookid': '101',
        'data_returned': '2023-12-31'
    })
    assert response.status_code == 201
    assert response.json()['message'] == 'Borrow request successfully posted'

def test_borrow_book_invalid_data():
    response = requests.post(f'{base_url}/users/borrow/request', json={
        'studentid': '1',
        'bookid': '101'
        # Missing 'data_returned'
    })
    assert response.status_code == 400
    assert response.json()['error'] == 'Invalid data format'

### /users/all TEST ###

def test_get_users(random_studentid):
    studentid = random_studentid
    requests.post(f'{base_url}/users/add', json={
        'studentid': studentid,
        'firstname': f'John{studentid}',
        'lastname': 'Doe',
        'email': f'john{studentid}.doe@example.com'
    })
    response = requests.get(f'{base_url}/users/all')
    assert response.status_code == 200
    assert any(user['studentid'] == studentid for user in response.json())

### /users/add ###

def test_create_user(random_studentid):
    studentid = random_studentid
    response = requests.post(f'{base_url}/users/add', json={
        'studentid': studentid,
        'firstname': f'John{studentid}',
        'lastname': 'Doe',
        'email': f'john{studentid}.doe@example.com'
    })
    assert response.status_code == 201
    assert response.json()['studentid'] == studentid
    assert response.json()['firstname'] == f'John{studentid}'
    assert response.json()['lastname'] == 'Doe'
    assert response.json()['email'] == f'john{studentid}.doe@example.com'

def test_create_user_duplicate_email(random_studentid):
    requests.post(f'{base_url}/users/add', json={
        'studentid': random_studentid,
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    response = requests.post(f'{base_url}/users/add', json={
        'studentid': random_studentid,
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': 'john.doe@example.com'
    })
    assert response.status_code == 400
    assert response.json()['error'] == 'Email already exists'

def test_create_user_duplicate_studentid(random_studentid):
    student_id: str = random_studentid
    requests.post(f'{base_url}/users/add', json={
        'studentid': student_id,
        'firstname': 'John',
        'lastname': 'Doe',
        'email': f'john{student_id}@example.com'
    })
    response = requests.post(f'{base_url}/users/add', json={
        'studentid': student_id,
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': f'jane{student_id}@example.com'
    })
    assert response.status_code == 400
    assert response.json()['error'] == 'Student ID already exists'

### /users/<studentid> TESTS ###
    ### GET METHODS

def test_get_user(random_studentid):
    studentid = random_studentid
    requests.post(f'{base_url}/users/add', json={
        'studentid': studentid,
        'firstname': f'John{studentid}',
        'lastname': 'Doe',
        'email': f'john{studentid}.doe@example.com'
    })
    response = requests.get(f'{base_url}/users/{studentid}')
    assert response.status_code == 200
    assert response.json()['studentid'] == studentid

def test_get_user_not_found():
    response = requests.get(f'{base_url}/users/1')
    assert response.status_code == 404
    assert response.json()['error'] == 'User not found'

    ### PUT METHODS

def test_update_user(random_studentid):
    studentid = random_studentid
    requests.post(f'{base_url}/users/add', json={
        'studentid': studentid,
        'firstname': f'John{studentid}',
        'lastname': 'Doe',
        'email': f'john{studentid}.doe@example.com'
    })
    response = requests.put(f'{base_url}/users/{studentid}', json={
        'firstname': 'Jane'
    })
    assert response.status_code == 200
    assert response.json()['firstname'] == 'Jane'

def test_update_user_not_found():
    response = requests.put(f'{base_url}/users/1', json={
        'firstname': 'Jane'
    })
    assert response.status_code == 404
    assert response.json()['error'] == 'User not found'

def test_update_user_duplicate_email():
    requests.post(f'{base_url}/users/add', json={
        'studentid': '1',
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    requests.post(f'{base_url}/users/add', json={
        'studentid': '2',
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': 'jane.smith@example.com'
    })
    response = requests.put(f'{base_url}/users/2', json={
        'email': 'john.doe@example.com'
    })
    assert response.status_code == 400
    assert response.json()['error'] == 'Email already exists'

def test_update_user_duplicate_studentid():
    requests.post(f'{base_url}/users/add', json={
        'studentid': '1',
        'firstname': 'John',
        'lastname': 'Doe',
        'email': 'john.doe@example.com'
    })
    requests.post(f'{base_url}/users/add', json={
        'studentid': '2',
        'firstname': 'Jane',
        'lastname': 'Smith',
        'email': 'jane.smith@example.com'
    })
    response = requests.put(f'{base_url}/users/2', json={
        'studentid': '1'
    })
    assert response.status_code == 400
    assert response.json()['error'] == 'Student ID already exists'

    ### DELETE METHODS

def test_delete_user(random_studentid):
    studentid = random_studentid
    requests.post(f'{base_url}/users/add', json={
        'studentid': studentid,
        'firstname': f'John{studentid}',
        'lastname': 'Doe',
        'email': f'john{studentid}.doe@example.com'
    })
    response = requests.delete(f'{base_url}/users/{studentid}')
    assert response.status_code == 200
    assert response.json()['message'] == 'User deleted successfully'

def test_delete_user_not_found():
    response = requests.delete(f'{base_url}/users/1')
    print(response.json())
    assert response.status_code == 404
    assert response.json()['error'] == 'User not found'
