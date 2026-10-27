"""
Controlador RESTful (Blueprint) para la gestión CRUD de Usuarios (/api/users).

Referencia: 2024-01 Practica REST_MYSQL.pdf — Ejercicios 2 y 3.
Expone los endpoints:
- GET    /api/users             -> Lista todos los usuarios (200 OK)
- GET    /api/users/<int:id>    -> Consulta un usuario por ID (200 OK / 404 Not Found)
- POST   /api/users             -> Crea un nuevo usuario en MySQL (201 Created / 400 Bad Request)
- PUT    /api/users/<int:id>    -> Actualiza un usuario existente (200 OK / 404 Not Found)
- DELETE /api/users/<int:id>    -> Elimina un usuario de MySQL (200 OK / 404 Not Found)
"""

from flask import Blueprint, abort, jsonify, request
from users.models.db import db
from users.models.user_model import Users

user_controller = Blueprint('user_controller', __name__)


@user_controller.route('/api/users', methods=['GET'])
def get_users():
    """Recupera la lista completa de usuarios almacenados en la tabla 'users'."""
    users = Users.query.all()
    result = [
        {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'username': user.username
        }
        for user in users
    ]
    return jsonify(result), 200


@user_controller.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    """Obtiene un usuario específico por su clave primaria o retorna 404 Not Found."""
    user = Users.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'username': user.username
    }), 200


@user_controller.route('/api/users', methods=['POST'])
def create_user():
    """Registra un nuevo usuario en la base de datos MySQL y confirma la transacción."""
    data = request.get_json(silent=True)
    if not data or not all(k in data for k in ('name', 'email', 'username', 'password')):
        abort(400, description="Payload JSON inválido: se requieren 'name', 'email', 'username' y 'password'.")

    new_user = Users(
        name=str(data['name']).strip(),
        email=str(data['email']).strip(),
        username=str(data['username']).strip(),
        password=str(data['password'])
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully', 'id': new_user.id}), 201


@user_controller.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id: int):
    """Actualiza los atributos de un usuario existente en MySQL."""
    user = Users.query.get_or_404(user_id)
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Payload JSON inválido para actualización.")

    user.name = str(data.get('name', user.name)).strip()
    user.email = str(data.get('email', user.email)).strip()
    user.username = str(data.get('username', user.username)).strip()
    if 'password' in data and str(data['password']).strip():
        user.password = str(data['password'])

    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200


@user_controller.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id: int):
    """Elimina físicamente el registro del usuario en la base de datos MySQL."""
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200
