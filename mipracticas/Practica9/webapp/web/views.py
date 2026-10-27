"""
Módulo principal de vistas web e inicialización de la aplicación Flask.

Integra:
1. Configuración de base de datos SQLAlchemy (db.init_app(app)).
2. Registro de Blueprints RESTful:
   - user_controller (/api/users) — Ejercicios 2 y 3.
   - product_controller (/api/products) — Ejercicio 5.b.
3. Renderizado de plantillas HTML Jinja2 (index.html, edit.html, products.html, edit_product.html)
   — Ejercicios 2 y 5.c.
"""

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from products.controllers.product_controller import product_controller
from users.controllers.user_controller import user_controller
from users.models.db import db

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app)
db.init_app(app)

# Registro de Blueprints para los controladores REST de Usuarios y Productos
app.register_blueprint(user_controller)
app.register_blueprint(product_controller)


# =============================================================================
# RUTAS DE VISTAS HTML (GESTIÓN DE USUARIOS Y GESTIÓN DE PRODUCTOS)
# =============================================================================

@app.route('/')
def index():
    """Renderiza la interfaz principal de gestión de usuarios (index.html)."""
    return render_template('index.html')


@app.route('/edit/<string:id>')
def edit_user(id: str):
    """Renderiza el formulario de edición de un usuario específico (edit.html)."""
    return render_template('edit.html', id=id)


@app.route('/products')
def products_page():
    """Renderiza la interfaz web de gestión de productos (products.html - Ejercicio 5.c)."""
    return render_template('products.html')


@app.route('/edit_product/<string:id>')
def edit_product(id: str):
    """Renderiza el formulario de edición de un producto específico (edit_product.html - Ejercicio 5.c)."""
    return render_template('edit_product.html', id=id)


# =============================================================================
# MANEJADORES DE ERRORES HTTP PARA ENDPOINTS API REST
# =============================================================================

@app.errorhandler(400)
def bad_request_error(error):
    """Retorna respuesta JSON estructurada ante errores 400 Bad Request."""
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description)
        }), 400
    return error


@app.errorhandler(404)
def not_found_error(error):
    """Retorna respuesta JSON estructurada ante errores 404 Not Found en /api/."""
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'Not Found',
            'message': 'El recurso solicitado no existe en la base de datos MySQL.'
        }), 404
    return error


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
