"""Routes for module books"""
import os
from flask import Blueprint, jsonify, request
from helper.db_helper import get_connection
from helper.form_validation import get_form_data
from datetime import datetime

pesanan_endpoints = Blueprint('pesanan', __name__)
UPLOAD_FOLDER = "img"

def calculate_harga(jenis_ps):
    if jenis_ps == 'PS4':
        return 150000
    elif jenis_ps == 'PS5':
        return 250000
    else:
        return 0

def calculate_total_harga(harga_harian, tanggal_sewa, tanggal_kembali):
    tgl_sewa = datetime.strptime(tanggal_sewa, "%Y-%m-%d")
    tgl_kembali = datetime.strptime(tanggal_kembali, "%Y-%m-%d")
    jumlah_hari = (tgl_kembali - tgl_sewa).days
    return harga_harian * jumlah_hari

@pesanan_endpoints.route('/read', methods=['GET'])
def read():
    """Routes for module get list books"""
    order_by = request.args.get('order_by', 'ASC').upper()
    if order_by not in ['ASC', 'DESC']:
        return jsonify({"message": "Invalid order_by value. Use 'ASC' or 'DESC'."}), 400
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    select_query = f"SELECT * FROM pesanan ORDER BY id_pesanan {order_by}"
    cursor.execute(select_query)
    results = cursor.fetchall()
    cursor.close()  # Close the cursor after query execution
    connection.close()  # Close the connection after query execution
    return jsonify({"message": "OK", "datas": results}), 200


@pesanan_endpoints.route('/read_by_user', methods=['GET'])
def read_by_user():
    """Route to get list of pesanan based on id_user"""
    id_user = request.args.get('id_user')
    order_by = request.args.get('order_by', 'ASC').upper()
    
    if not id_user:
        return jsonify({"message": "id_user is required"}), 400

    if order_by not in ['ASC', 'DESC']:
        return jsonify({"message": "Invalid order_by value. Use 'ASC' or 'DESC'."}), 400
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    select_query = f"SELECT * FROM pesanan WHERE id_user = %s ORDER BY id_pesanan {order_by}"
    cursor.execute(select_query, (id_user,))
    results = cursor.fetchall()
    cursor.close()
    connection.close()  # Close the connection after query execution
    return jsonify({"message": "OK", "datas": results}), 200


@pesanan_endpoints.route('/create', methods=['POST'])
def create():
    try:
        id_user = request.form['id_user']
        tanggal_sewa = request.form['tanggal_sewa']
        tanggal_kembali = request.form['tanggal_kembali']
        jenis_ps = request.form['jenis_ps']
        jumlah_stik = request.form['jumlah_stik']

        harga_harian = calculate_harga(jenis_ps)
        total_harga = calculate_total_harga(harga_harian, tanggal_sewa, tanggal_kembali)

        connection = get_connection()
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO pesanan (id_user, tanggal_sewa, tanggal_kembali, jenis_ps, jumlah_stik, harga, total_harga) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        insert_request = (id_user, tanggal_sewa, tanggal_kembali, jenis_ps, jumlah_stik, harga_harian, total_harga)
        cursor.execute(insert_query, insert_request)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({
            "message": "Successfully created data",
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Failed to create data!",
            "error": str(e)
        }), 500

@pesanan_endpoints.route('/update', methods=['PUT'])
def update():
    connection = None
    cursor = None
    try:
        data = request.json
        id_pesanan = data['id_pesanan']
        id_user = data['id_user']
        tanggal_sewa = data['tanggal_sewa']
        tanggal_kembali = data['tanggal_kembali']
        jenis_ps = data['jenis_ps']
        jumlah_stik = data['jumlah_stik']

        harga_harian = calculate_harga(jenis_ps)
        total_harga = calculate_total_harga(harga_harian, tanggal_sewa, tanggal_kembali)

        connection = get_connection()
        cursor = connection.cursor()

        update_query = """
        UPDATE pesanan 
        SET id_user = %s, tanggal_sewa = %s, tanggal_kembali = %s, jenis_ps = %s, jumlah_stik = %s, harga = %s, total_harga = %s
        WHERE id_pesanan = %s
        """
        
        update_request = (id_user, tanggal_sewa, tanggal_kembali, jenis_ps, jumlah_stik, harga_harian, total_harga, id_pesanan)
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

@pesanan_endpoints.route('/delete/<int:id_pesanan>', methods=['DELETE'])
def delete(id_pesanan):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        delete_query = "DELETE FROM pesanan WHERE id_pesanan = %s"
        cursor.execute(delete_query, (id_pesanan,))
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
