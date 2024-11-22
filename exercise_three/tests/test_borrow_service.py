import pytest
import random
import requests

base_url = 'http://localhost:5002'

@pytest.fixture
def random_studentid():
    return str(random.randint(1000, 999999999999))


### /users/borrow/request TEST ###

def test_borrow_book_success(random_studentid):
    student_id = random_studentid
    requests.post(f'{base_url}/users/add', json={
        'studentid': student_id,
        'firstname': f'John{student_id}',
        'lastname': 'Doe',
        'email': f"{student_id}@gmail.com"
    })
    print(f"Student ID: {student_id}")

    response = requests.post(f'{base_url}/users/borrow/request', json={
        'studentid': student_id,
        'bookid': '101',
        'date_returned': '2023-12-31'
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