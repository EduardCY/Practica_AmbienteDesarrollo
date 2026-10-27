"""
Modelo ORM para la entidad 'Products' mapeada a la tabla MySQL 'myflaskapp.products'.

Referencia: 2024-01 Practica REST_MYSQL.pdf — Ejercicio 5.a y 5.b:
'5. Complemente la aplicación con la funcionalidad necesaria para gestionar productos
 a. Cree la tabla productos en la base de datos
 b. Cree la API Rest Correspondiente'
"""

from users.models.db import db


class Products(db.Model):
    """Representa un producto de inventario almacenado en la tabla 'products'."""

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True, default='')
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    stock = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, name: str, description: str, price: float, stock: int) -> None:
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock

    def to_dict(self) -> dict:
        """Serializa el modelo de producto a diccionario con conversión numérica explícita."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'price': float(self.price) if self.price is not None else 0.0,
            'stock': int(self.stock) if self.stock is not None else 0
        }
