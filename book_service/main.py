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
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
        )).scalar()
        if result:
            return jsonify({"message": "Healthy"}), 200
        else:
            return jsonify({"message": "Unhealthy: 'users' table does not exist"}), 500
    except Exception as e:
        return jsonify({"message": "Unhealthy: " + str(e)}), 500


# CREATE users
@app.route('/users/add', methods=['POST'])
def create_user():
    data = request.json
    if User.query.get(data['studentid']):
        return jsonify({"error": "Student ID already exists"}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400
    try:
        user = User(
            studentid=data['studentid'], 
            firstname=data['firstname'],
            lastname=data['lastname'], 
            email=data['email']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# READ all users
@app.route('/users/all', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


# READ a single user by ID
@app.route('/users/<studentid>', methods=['GET'])
def get_user(studentid:str):
    user = User.query.get(studentid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200


# UPDATE a user by student_id
@app.route('/users/<studentid>', methods=['PUT'])
def update_user(studentid:str):
    user = User.query.get(studentid)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.json
    if 'firstname' in data:
        user.firstname = data['firstname']
    if 'lastname' in data:
        user.lastname = data['lastname']
    if 'email' in data:
        # Check if new email already exists for another user
        if User.query.filter(User.email == data['email'], User.studentid != studentid).first():
            return jsonify({"error": "Email already exists"}), 400
        user.email = data['email']
    if 'studentid' in data:
        # Check if new studentid already exists for another user
        if User.query.get(data['studentid']):
            return jsonify({"error": "Student ID already exists"}), 400
        user.studentid = data['studentid']
    db.session.commit()
    return jsonify(user.to_dict()), 200


# DELETE a user by student_id
@app.route('/users/<studentid>', methods=['DELETE'])
def delete_user(studentid:str):
    user = User.query.get(studentid)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200


if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0", port=5006)
