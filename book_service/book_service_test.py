import pytest
from book_service.main import app, db
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

### /books/all TEST ###

def test_get_books_empty(client):
    response = client.get('/books/all')
    assert response.status_code == 200
    assert response.json == []

def test_get_books(client):
    client.post('/books/add', json={
        'bookid': '1',
        'title': 'Book Title',
        'author': 'Book Author'
    })
    response = client.get('/books/all')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['bookid'] == '1'

### /books/add ###

def test_create_book(client):
    response = client.post('/books/add', json={
        'bookid': '1',
        'title': 'Book Title',
        'author': 'Book Author'
        })
    assert response.status_code == 201
    assert response.json['bookid'] == '1'
    assert response.json['title'] == 'Book Title'
    assert response.json['author'] == 'Book Author'
    assert response.json['checked_out'] == False

def test_create_book_duplicate_bookid(client):
    client.post('/books/add', json={
        'bookid': '1',
        'title': 'Book Title',
        'author': 'Book Author'
    })
    response = client.post('/books/add', json={
        'bookid': '1',
        'title': 'Book Title',
        'author': 'Book Author'
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Book ID already exists'

### /books/<bookid> TESTS ###
    ### GET METHODS

def test_get_book(client):
    client.post('/books/add', json={
        'bookid': '1',
        'title': 'Book Title',
        'author': 'Book Author'
    })
    response = client.get('/books/1')
    assert response.status_code == 200
    assert response.json['bookid'] == '1'

def test_get_book_not_found(client):
    response = client.get('/books/1')
    assert response.status_code == 404
    assert response.json['error'] == 'Book not found'

    ### PUT METHODS

def test_update_book(client):
    client.post('/books/add', json={
        'bookid': '1',
        'title': 'Book Title',
        'author': 'Book Author'
    })
    response = client.put('/books/1', json={
        'title': 'Something weird and wonderful'
    })
    assert response.status_code == 200
    assert response.json['title'] == 'Something weird and wonderful'

def test_update_book_not_found(client):
    response = client.put('/books/1', json={
        'title': 'Something weird and wonderful'
    })
    assert response.status_code == 404
    assert response.json['error'] == 'Book not found'

def test_create_duplicate_bookid(client):
    client.post('/books/add', json={
        'bookid': '1',
        'title': 'Book Title',
        'author': 'Book Author'
    })
    client.post('/books/add', json={
        'bookid': '2',
        'title': 'Another Book Title',
        'author': 'Another Book Author'
    })
    response = client.put('/books/2', json={
        'bookid': '1'
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Book ID already exists'

    ### DELETE METHODS

def test_delete_book(client):
    client.post('/books/add', json={
        'bookid': '1',
        'title': 'Book Title',
        'author': 'Book Author'
    })
    response = client.delete('/books/1')
    assert response.status_code == 200
    assert response.json['message'] == 'Book deleted successfully'

def test_delete_book_not_found(client):
    response = client.delete('/books/1')
    assert response.status_code == 404
    assert response.json['error'] == 'Book not found'
