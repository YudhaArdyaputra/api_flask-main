from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

protected_endpoints = Blueprint('data_protected', __name__)

@protected_endpoints.route('/data', methods=['GET'])
@jwt_required()
def get_data():
    """
    Routes for demonstrating protected data endpoints,
    needs JWT to visit this endpoint.
    """
    current_user = get_jwt_identity()
    claims = get_jwt()
    roles = claims.get('roles', 'umum')

    return jsonify({"message": "OK",
                    "user_logged": current_user['id_user'],
                    "roles": roles}), 200