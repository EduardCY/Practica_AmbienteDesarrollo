"""
Controlador RESTful (Blueprint) para la gestión CRUD de Productos (/api/products).

Referencia: 2024-01 Practica REST_MYSQL.pdf — Ejercicio 5.b:
'5.b. Cree la API Rest Correspondiente'

Expone los endpoints:
- GET    /api/products             -> Lista todos los productos del inventario (200 OK)
- GET    /api/products/<int:id>    -> Consulta un producto por ID (200 OK / 404 Not Found)
- POST   /api/products             -> Registra un nuevo producto en MySQL (201 Created / 400 Bad Request)
- PUT    /api/products/<int:id>    -> Actualiza un producto existente (200 OK / 404 Not Found)
- DELETE /api/products/<int:id>    -> Elimina un producto de MySQL (200 OK / 404 Not Found)
"""

from flask import Blueprint, abort, jsonify, request
from products.models.product_model import Products
from users.models.db import db

product_controller = Blueprint('product_controller', __name__)


@product_controller.route('/api/products', methods=['GET'])
def get_products():
    """Recupera el catálogo completo de productos desde la tabla MySQL 'products'."""
    products = Products.query.all()
    result = [product.to_dict() for product in products]
    return jsonify(result), 200


@product_controller.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id: int):
    """Obtiene los detalles de un producto específico por su ID numérico."""
    product = Products.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200


@product_controller.route('/api/products', methods=['POST'])
def create_product():
    """Crea y persiste un nuevo producto en la tabla 'products' de MySQL."""
    data = request.get_json(silent=True)
    if not data or 'name' not in data or not str(data['name']).strip():
        abort(400, description="Payload JSON inválido: se requiere al menos el campo 'name' no vacío.")

    try:
        price_val = float(data.get('price', 0.0))
        stock_val = int(data.get('stock', 0))
    except (ValueError, TypeError):
        abort(400, description="Los campos 'price' y 'stock' deben ser valores numéricos válidos.")

    new_product = Products(
        name=str(data['name']).strip(),
        description=str(data.get('description', '')).strip(),
        price=price_val,
        stock=stock_val
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({
        'message': 'Product created successfully',
        'id': new_product.id,
        'product': new_product.to_dict()
    }), 201


@product_controller.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id: int):
    """Actualiza los atributos (nombre, descripción, precio, stock) de un producto existente."""
    product = Products.query.get_or_404(product_id)
    data = request.get_json(silent=True)
    if not data:
        abort(400, description="Payload JSON inválido para actualizar el producto.")

    if 'name' in data and str(data['name']).strip():
        product.name = str(data['name']).strip()
    if 'description' in data:
        product.description = str(data['description']).strip()
    if 'price' in data:
        try:
            product.price = float(data['price'])
        except (ValueError, TypeError):
            abort(400, description="El campo 'price' debe ser un número válido.")
    if 'stock' in data:
        try:
            product.stock = int(data['stock'])
        except (ValueError, TypeError):
            abort(400, description="El campo 'stock' debe ser un entero válido.")

    db.session.commit()
    return jsonify({
        'message': 'Product updated successfully',
        'product': product.to_dict()
    }), 200


@product_controller.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id: int):
    """Elimina físicamente un producto del catálogo en MySQL."""
    product = Products.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200
