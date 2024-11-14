from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import dotenv
import os

dotenv.load_dotenv()

db_user = os.getenv('POSTGRES_USER')
db_password = os.getenv('POSTGRES_PASSWORD')
db_host = os.getenv('POSTGRES_HOST')
db_port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Book(db.Model):
    __tablename__ = 'books'

    bookid = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    checked_out = db.Column(db.Boolean(), default=False, nullable=False)
    
    def to_dict(self):
        return {
            "bookid": self.bookid,
            "title": self.title,
            "author": self.author,
            "checked_out": self.checked_out
        }
with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def health_check():
    try:
        result = db.session.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'books')"
        )).scalar()
        if result:
            return jsonify({"message": "Healthy"}), 200
        else:
            return jsonify({"message": "Unhealthy: 'books' table does not exist"}), 500
    except Exception as e:
        return jsonify({"message": "Unhealthy: " + str(e)}), 500


# CREATE books
@app.route('/books/add', methods=['POST'])
def create_book():
    data = request.json
    if Book.query.get(data['bookid']):
        return jsonify({"error": "Book ID already exists"}), 400
    try:
        book = Book(
            bookid=data['bookid'],
            title=data['title'],
            author=data['author']
        )
        db.session.add(book)
        db.session.commit()
        return jsonify(book.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# READ all books
@app.route('/books/all', methods=['GET'])
def get_users():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200


# READ a single book by ID
@app.route('/books/<bookid>', methods=['GET'])
def get_book(bookid: str):
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict()), 200


# UPDATE a book by bookid
@app.route('/books/<bookid>', methods=['PUT'])
def update_book(bookid: str):
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.json
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'bookid' in data:
        # Check if new email already exists for another book
        if Book.query.filter(Book.bookid == data['bookid'], Book.bookid != bookid).first():
            return jsonify({"error": "Book ID already exists"}), 400
        book.bookid = data['bookid']
    db.session.commit()
    return jsonify(book.to_dict()), 200


# DELETE a book by bookid
@app.route('/books/<bookid>', methods=['DELETE'])
def delete_book(bookid: str):
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 200


if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0", port=5006)