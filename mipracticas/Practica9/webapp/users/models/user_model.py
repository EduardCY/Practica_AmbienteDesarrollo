"""
Modelo ORM para la entidad 'Users' mapeada a la tabla MySQL 'myflaskapp.users'.

Referencia: 2024-01 Practica REST_MYSQL.pdf — Ejercicios 1 y 2.
"""

from users.models.db import db


class Users(db.Model):
    """Representa un usuario registrado en la base de datos relacional."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name: str, email: str, username: str, password: str) -> None:
        self.name = name
        self.email = email
        self.username = username
        self.password = password

    def to_dict(self) -> dict:
        """Serializa los atributos públicos del modelo a un diccionario nativo."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'username': self.username
        }
