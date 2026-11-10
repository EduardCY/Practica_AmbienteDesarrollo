"""
Controlador RESTful (Blueprint) para la gestión CRUD de Productos.

Referencia: 2024-03 Practica AWS EC2.pdf — Punto 4 (Ejercicio):
'Instale y pruebe un API Rest. Puede ser cualquiera de los construidos en prácticas anteriores
 Instálelo en una máquina virtual y pruébelo desde la otra.
 Pruébelo desde cualquier otro dispositivo usando la IP real de la máquina donde desplegó el servicio'

Expone los endpoints canónicos:
- GET    /api/products             -> Retorna la colección completa (200 OK)
- GET    /api/products/<int:id>    -> Retorna un producto por ID (200 OK / 404 Not Found)
- POST   /api/products             -> Registra un nuevo producto (201 Created / 400 Bad Request)
- PUT    /api/products/<int:id>    -> Actualiza atributos de un producto (200 OK / 400 Bad Request / 404 Not Found)
- DELETE /api/products/<int:id>    -> Elimina un producto del catálogo (200 OK / 404 Not Found)
"""

from flask import Blueprint, abort, jsonify, request
from extensions import db
from products.models.product_model import Products

product_controller = Blueprint("product_controller", __name__)


@product_controller.route("/api/products", methods=["GET"])
def get_products():
    """
    Recupera el inventario completo de productos registrados.

    :return: Respuesta JSON con la lista de productos y código de estado 200.
    """
    products = Products.query.order_by(Products.id.asc()).all()
    return jsonify([p.to_dict() for p in products]), 200


@product_controller.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id: int):
    """
    Obtiene los detalles de un producto específico mediante su identificador numérico.

    Por qué db.get_or_404:
    Reemplaza la sintaxis heredada de Flask-SQLAlchemy 2.x (Model.query.get)
    asegurando compatibilidad nativa con SQLAlchemy 2.0 y Flask 3.x.

    :param product_id: Clave primaria del producto.
    :return: Representación JSON del producto encontrado.
    """
    product = db.get_or_404(Products, product_id, description=f"Producto con id={product_id} no encontrado.")
    return jsonify(product.to_dict()), 200


@product_controller.route("/api/products", methods=["POST"])
def create_product():
    """
    Crea y persiste un nuevo producto en la base de datos a partir de un cuerpo JSON.

    Por qué silent=True en get_json:
    Evita excepciones no controladas cuando un cliente cURL omite el encabezado
    Content-Type: application/json o envía una carga malformada.

    :return: Confirmación con id asignado y código 201 Created.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "name" not in data or not str(data["name"]).strip():
        abort(400, description="Payload JSON inválido: se requiere el campo 'name' como cadena no vacía.")

    try:
        price_val = float(data.get("price", 0.0))
        stock_val = int(data.get("stock", 0))
    except (ValueError, TypeError):
        abort(400, description="Los campos 'price' y 'stock' deben ser valores numéricos válidos.")

    new_product = Products(
        name=str(data["name"]).strip(),
        description=str(data.get("description", "")).strip(),
        price=price_val,
        stock=stock_val
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "message": "Product created successfully",
        "id": new_product.id,
        "product": new_product.to_dict()
    }), 201


@product_controller.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id: int):
    """
    Actualiza parcialmente o totalmente los atributos de un producto existente.

    :param product_id: Clave primaria del producto a modificar.
    :return: Confirmación y representación actualizada del producto.
    """
    product = db.get_or_404(Products, product_id, description=f"Producto con id={product_id} no encontrado.")
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, description="Payload JSON inválido para actualización de producto.")

    if "name" in data:
        name_val = str(data["name"]).strip()
        if not name_val:
            abort(400, description="El campo 'name' no puede ser una cadena vacía.")
        product.name = name_val

    if "description" in data:
        product.description = str(data.get("description", "")).strip()

    if "price" in data:
        try:
            product.price = float(data["price"])
        except (ValueError, TypeError):
            abort(400, description="El campo 'price' debe ser un número válido.")

    if "stock" in data:
        try:
            product.stock = int(data["stock"])
        except (ValueError, TypeError):
            abort(400, description="El campo 'stock' debe ser un entero válido.")

    db.session.commit()

    return jsonify({
        "message": "Product updated successfully",
        "product": product.to_dict()
    }), 200


@product_controller.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int):
    """
    Elimina permanentemente un producto del catálogo.

    :param product_id: Clave primaria del producto a eliminar.
    :return: Mensaje de confirmación de eliminación con estado 200 OK.
    """
    product = db.get_or_404(Products, product_id, description=f"Producto con id={product_id} no encontrado.")
    db.session.delete(product)
    db.session.commit()

    return jsonify({
        "message": "Product deleted successfully",
        "deleted_id": product_id
    }), 200
