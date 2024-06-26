from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, decode_token, JWTManager
from flask_bcrypt import Bcrypt
from helper.db_helper import get_connection

bcrypt = Bcrypt()
auth_endpoints = Blueprint('auth', __name__)
jwt = JWTManager()  # Pastikan untuk menginisialisasi JWTManager dengan aplikasi Flask Anda

@auth_endpoints.route('/login', methods=['POST'])
def login():
    """Routes for authentication"""
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM user WHERE username = %s"
    request_query = (username,)
    cursor.execute(query, request_query)
    user = cursor.fetchone()
    cursor.close()

    if not user or not bcrypt.check_password_hash(user.get('password'), password):
        return jsonify({"msg": "Bad username or password"}), 401

    roles = user.get('roles', 'user')  # Ambil roles dari database, default 'user'


    access_token = create_access_token(
        identity={'id_user': user['id_user']},
        additional_claims={'roles': roles}
    )
    decoded_token = decode_token(access_token)
    expires = decoded_token['exp']
    return jsonify({"access_token": access_token, "expires_in": expires, "type": "Bearer"})

@auth_endpoints.route('/register', methods=['POST'])
def register():
    """Route untuk registrasi"""
    try:
        username = request.form['username']
        password = request.form['password']
        nama_lengkap = request.form['nama_lengkap']
        alamat = request.form['alamat']
        nohp = request.form['nohp']
        roles = request.form.get('roles', 'umum')  # Ambil roles dari form, default 'umum'

        if not username or not password:
            return jsonify({"msg": "Username dan password diperlukan"}), 400

        if roles not in ['admin', 'umum']:
            return jsonify({"msg": "Roles harus 'admin' atau 'umum'"}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        connection = get_connection()
        cursor = connection.cursor()
        insert_query = "INSERT INTO user (username, password, roles, nama_lengkap, alamat, nohp) VALUES (%s, %s, %s, %s, %s, %s)"
        request_insert = (username, hashed_password, roles, nama_lengkap, alamat, nohp)
        cursor.execute(insert_query, request_insert)
        new_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        connection.close()

        if new_id:
            return jsonify({"message": "OK", "description": "User created", "username": username}), 201
        return jsonify({"message": "Failed, can't register user"}), 501
    except Exception as e:
        return jsonify({"message": "Gagal registrasi!", "error": str(e)}), 500