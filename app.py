from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import bcrypt

app = Flask(__name__)
CORS(app)

# Database connection details
db_config = {
    'host': 'sql12.freesqldatabase.com',
    'user': 'sql12735355',
    'password': 'WE1CeJXLwC',
    'database': 'sql12735355'
}

# Helper function to connect to the database
def connect_db():
    return pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def getmessage():
    return "this is test message"

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        connection = connect_db()
        with connection.cursor() as cursor:
            # Check if email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"message": "Email already registered"}), 409
            
            # Insert new user
            sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (username, email, hashed_password.decode('utf-8')))
            connection.commit()
        return jsonify({"message": "User registered successfully"}), 201

    except pymysql.MySQLError as e:
        print("Error occurred while inserting user: ", str(e))
        return jsonify({"message": "User registration failed", "error": str(e)}), 500
    finally:
        connection.close()


@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    try:
        connection = connect_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                user.pop('password', None)
                return jsonify({"message": "Login successful", "user": user}), 200
            else:
                return jsonify({"message": "Invalid email or password"}), 401

    except pymysql.MySQLError as e:
        return jsonify({"message": "Database error", "error": str(e)}), 500
    finally:
        connection.close()

