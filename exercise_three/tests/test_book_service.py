import pytest
import requests
import random
import os

def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default="http://localhost:5006", help="Base URL for the API")

@pytest.fixture
def base_url(request):
    return request.config.getoption("--base-url")

@pytest.fixture
def random_bookid():
    return str(random.randint(1000, 999999999999))

### /books/all TEST ###

def test_get_books(random_bookid, base_url):
    bookid = random_bookid
    requests.post(f'{base_url}/books/add', json={
        'bookid': bookid,
        'title': 'Book Title',
        'author': 'Book Author'
    })
    response = requests.get(f'{base_url}/books/all')
    assert response.status_code == 200
    assert any(book['bookid'] == bookid for book in response.json())

### /books/add ###

def test_create_book(random_bookid, base_url):
    bookid = random_bookid
    response = requests.post(f'{base_url}/books/add', json={
        'bookid': bookid,
        'title': 'Book Title',
        'author': 'Book Author'
    })
    assert response.status_code == 201
    assert response.json()['bookid'] == bookid
    assert response.json()['title'] == 'Book Title'
    assert response.json()['author'] == 'Book Author'
    assert response.json()['checked_out'] == False

def test_create_book_duplicate_bookid(random_bookid, base_url):
    bookid = random_bookid
    requests.post(f'{base_url}/books/add', json={
        'bookid': bookid,
        'title': 'Book Title',
        'author': 'Book Author'
    })
    response = requests.post(f'{base_url}/books/add', json={
        'bookid': bookid,
        'title': 'Book Title',
        'author': 'Book Author'
    })
    assert response.status_code == 400
    assert response.json()['error'] == 'Book ID already exists'

### /books/<bookid> TESTS ###
    ### GET METHODS

def test_get_book(random_bookid, base_url):
    bookid = random_bookid
    requests.post(f'{base_url}/books/add', json={
        'bookid': bookid,
        'title': 'Book Title',
        'author': 'Book Author'
    })
    response = requests.get(f'{base_url}/books/{bookid}')
    assert response.status_code == 200
    assert response.json()['bookid'] == bookid

def test_get_book_not_found(base_url):
    response = requests.get(f'{base_url}/books/nonexistent')
    assert response.status_code == 404
    assert response.json()['error'] == 'Book not found'

    ### PUT METHODS

def test_update_book(random_bookid, base_url):
    bookid = random_bookid
    requests.post(f'{base_url}/books/add', json={
        'bookid': bookid,
        'title': 'Book Title',
        'author': 'Book Author'
    })
    response = requests.put(f'{base_url}/books/{bookid}', json={
        'title': 'Something weird and wonderful'
    })
    assert response.status_code == 200
    assert response.json()['title'] == 'Something weird and wonderful'

def test_update_book_not_found(base_url):
    response = requests.put(f'{base_url}/books/nonexistent', json={
        'title': 'Something weird and wonderful'
    })
    assert response.status_code == 404
    assert response.json()['error'] == 'Book not found'

def test_create_duplicate_bookid(random_bookid, base_url):
    bookid1 = random_bookid
    requests.post(f'{base_url}/books/add', json={
        'bookid': bookid1,
        'title': 'Book Title',
        'author': 'Book Author'
    })
    response = requests.post(f'{base_url}/books/add', json={
        'bookid': bookid1,
        'title': 'Another Book Title',
        'author': 'Another Book Author'
    })

    assert response.status_code == 400
    assert response.json()['error'] == 'Book ID already exists'

    ### DELETE METHODS

def test_delete_book(random_bookid, base_url):
    bookid = random_bookid
    requests.post(f'{base_url}/books/add', json={
        'bookid': bookid,
        'title': 'Book Title',
        'author': 'Book Author'
    })
    response = requests.delete(f'{base_url}/books/{bookid}')
    assert response.status_code == 200
    assert response.json()['message'] == 'Book deleted successfully'

def test_delete_book_not_found(base_url):
    response = requests.delete(f'{base_url}/books/nonexistent')
    assert response.status_code == 404
    assert response.json()['error'] == 'Book not found'
