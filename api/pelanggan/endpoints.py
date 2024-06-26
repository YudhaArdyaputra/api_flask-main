"""Routes for module books"""
import os
from flask import Blueprint, jsonify, request
from helper.db_helper import get_connection
from helper.form_validation import get_form_data

pelanggan_endpoints = Blueprint('pelanggan', __name__)
UPLOAD_FOLDER = "img"


@pelanggan_endpoints.route('/read', methods=['GET'])
def read():
    """Routes for module get list books"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    select_query = "SELECT * FROM pelanggan"
    cursor.execute(select_query)
    results = cursor.fetchall()
    cursor.close()  # Close the cursor after query execution
    return jsonify({"message": "OK", "datas": results}), 200


@pelanggan_endpoints.route('/create', methods=['POST'])
def create():
    try:
        id_user = request.form['id_user']
        nama = request.form['nama']
        alamat = request.form['alamat']
        nohp = request.form['nohp']

        connection = get_connection()
        cursor = connection.cursor()
        insert_query = "INSERT INTO pelanggan (id_user, nama, alamat, nohp) VALUES (%s, %s, %s, %s)"
        insert_request = (id_user, nama, alamat, nohp,)
        cursor.execute(insert_query, insert_request)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({
            "message": "Successfully Create data",
        }), 200
    except Exception as e:
        return jsonify({
            "message": "failed to create data!",
            "error": str(e)
        }), 500

@pelanggan_endpoints.route('/update', methods=['PUT'])
def update():
    connection = None
    cursor = None
    try:
        data = request.json
        id_pelanggan = data['id_pelanggan']
        id_user = data['id_user']
        nama = data['nama']
        alamat = data['alamat']
        nohp = data['nohp']

        connection = get_connection()
        cursor = connection.cursor()

        update_query = """
        UPDATE pelanggan 
        SET id_user = %s, nama = %s, alamat = %s, nohp = %s
        WHERE id_pelanggan = %s
        """
        
        update_request = (id_user, nama, alamat, nohp, id_pelanggan)  # Ensure the order matches the query
        cursor.execute(update_query, update_request)
        connection.commit()

        return jsonify({"message": "Successfully updated data"}), 200

    except Exception as e:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@pelanggan_endpoints.route('/delete/<int:id_pelanggan>', methods=['DELETE'])
def delete(id_pelanggan):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        delete_query = "DELETE FROM pelanggan WHERE id_pelanggan = %s"
        cursor.execute(delete_query, (id_pelanggan,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Data not found"}), 404

        return jsonify({"message": "Successfully deleted data"}), 200

    except Exception as e:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()