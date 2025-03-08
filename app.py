from flask import Flask, jsonify, request, render_template
import psycopg2
from flask_bcrypt import Bcrypt
import jwt
import datetime

app = Flask(__name__)

# Database connection configuration
DB_HOST = 'localhost'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = '2525'
SECRET_KEY = "this is a secret key this is a secret keyyyy!!!!"

def get_db_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return connection

def create_users_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()

create_users_table_if_not_exists()

bcrypt = Bcrypt(app)

def encode_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(hashed_password, password):
    return bcrypt.check_password_hash(hashed_password, password)

def decode_token(jwt_token):
    try:
        decoded_token_payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token_payload
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token!"}), 401

@app.route('/sign-up', methods=['POST'])
def register_user():
    username = request.json['username']
    password = request.json['password']
    hashed_password = encode_password(password)
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            INSERT INTO users (username, password) VALUES (%s, %s);
        """, (username, hashed_password))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "User registered successfully."}), 201

@app.route('/login', methods=['POST'])
def login_user():
    username = request.json['username']
    password = request.json['password']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
    user = cursor.fetchone()
    if user is None or not check_password(user[2], password):
        cursor.close()
        connection.close()
        return jsonify({"message": "Invalid username or password."}), 401
    payload = {
        'username': username,
        'user_id': user[0],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    cursor.close()
    connection.close()
    return jsonify({"message": "Login successful.", "token": token}), 200

# Updated course data with providers
COURSES = {
    "AI provided by WIPRO": {
        "title": "Artificial Intelligence",
        "description": "provided by WIPRO.",
        "texts": "Artificial Intelligence (AI) is the simulation of human intelligence in machines.",
        "blogs": [
            {"title": "AI Basics", "content": "An introduction to AI concepts and techniques."},
            {"title": "Machine Learning", "content": "Exploring supervised and unsupervised learning."}
        ]
    },
    "PYTHON provided by IBM": {
        "title": "Python Programming",
        "description": "provided by IBM.",
        "texts": "Python is a versatile, high-level programming language.",
        "blogs": [
            {"title": "Python Syntax", "content": "Understanding Python's simple syntax."},
            {"title": "Python Libraries", "content": "Top libraries for Python developers."}
        ]
    },
    "JAVA provided by TCS": {
        "title": "Java Development",
        "description": "provided by TCS.",
        "texts": "Java is a robust, object-oriented programming language.",
        "blogs": [
            {"title": "Java OOP", "content": "Object-Oriented Programming in Java."},
            {"title": "Java Performance", "content": "Optimizing Java applications."}
        ]
    },
    "C provided by INFOSYS": {
        "title": "C Programming",
        "description": "provided by INFOSYS.",
        "texts": "C is a powerful, low-level programming language.",
        "blogs": [
            {"title": "C Pointers", "content": "Mastering pointers in C."},
            {"title": "C Memory Management", "content": "Managing memory in C programs."}
        ]
    }
}

@app.route('/categories', methods=['GET'])
def get_categories():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Token is missing!"}), 401
    token = token.split(" ")[1]
    decoded = decode_token(token)
    if isinstance(decoded, tuple):
        return decoded
    return jsonify({"categories": list(COURSES.keys())}), 200

@app.route('/category/<category>', methods=['GET'])
def get_category_data(category):
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({"message": "Token is missing!"}), 401
    token = token.split(" ")[1]
    decoded = decode_token(token)
    if isinstance(decoded, tuple):
        return decoded
    # Handle category as is (with provider name included)
    if category in COURSES:
        return jsonify(COURSES[category]), 200
    return jsonify({"message": "Category not found!"}), 404

# Routes for rendering templates
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/category-details/<path:category>')
def category_details(category):
    return render_template('category_details.html', category=category)

if __name__ == '__main__':
    app.run(debug=True)