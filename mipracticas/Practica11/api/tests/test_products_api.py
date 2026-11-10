"""
Pruebas unitarias y de integración para la API REST de Productos.

Por qué se utiliza SQLite en memoria (:memory:):
Aísla completamente la suite de pruebas del sistema de archivos y del entorno
de ejecución de AWS, permitiendo validar la lógica de negocio y los códigos HTTP en milisegundos.
"""

import os
import tempfile
import pytest
from app import create_app
from config import Config, TestConfig
from extensions import db
from products.models.product_model import Products


@pytest.fixture
def app():
    """Configura una instancia limpia de la aplicación con base de datos en memoria."""
    app_instance = create_app(TestConfig)
    with app_instance.app_context():
        db.create_all()
        yield app_instance
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Provee un cliente HTTP de pruebas para simular peticiones."""
    return app.test_client()


def test_root_endpoint(client):
    """Verifica que la raíz entregue información de la API con estado 200."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "online"
    assert "endpoints" in data


def test_health_check_endpoint(client):
    """Verifica que /api/health responda con estado ok y metadatos."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "hostname" in data
    assert "ec2_metadata" in data


def test_get_products_initially_empty(client):
    """Verifica que la colección inicial esté vacía bajo TestConfig."""
    response = client.get("/api/products")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_product_success(client):
    """Verifica la creación exitosa de un producto con código 201."""
    payload = {
        "name": "Instancia EC2 Ubuntu 22.04",
        "description": "Servidor virtual en us-east-1",
        "price": 12.50,
        "stock": 10
    }
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["product"]["name"] == payload["name"]
    assert data["product"]["price"] == 12.50
    assert data["product"]["stock"] == 10


def test_create_product_missing_name(client):
    """Verifica que enviar un payload sin el campo 'name' retorne 400 Bad Request."""
    response = client.post("/api/products", json={"price": 10.0})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Bad Request"


def test_create_product_invalid_numeric_fields(client):
    """Verifica que enviar campos numéricos no convertibles retorne 400."""
    response = client.post("/api/products", json={"name": "Test", "price": "no-es-numero"})
    assert response.status_code == 400


def test_get_product_by_id(client):
    """Verifica la consulta de un producto individual existente."""
    create_res = client.post("/api/products", json={"name": "Disco SSD", "price": 50.0, "stock": 5})
    product_id = create_res.get_json()["id"]

    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == product_id
    assert data["name"] == "Disco SSD"


def test_get_product_not_found(client):
    """Verifica que consultar un ID inexistente retorne 404 JSON."""
    response = client.get("/api/products/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Not Found"


def test_update_product_success(client):
    """Verifica la actualización parcial y total de un producto existente."""
    create_res = client.post("/api/products", json={"name": "Original", "price": 10.0, "stock": 2})
    product_id = create_res.get_json()["id"]

    update_payload = {"name": "Modificado", "price": 15.75, "stock": 8}
    response = client.put(f"/api/products/{product_id}", json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["product"]["name"] == "Modificado"
    assert data["product"]["price"] == 15.75
    assert data["product"]["stock"] == 8


def test_update_product_empty_name(client):
    """Verifica que intentar actualizar con nombre vacío retorne 400."""
    create_res = client.post("/api/products", json={"name": "Original"})
    product_id = create_res.get_json()["id"]

    response = client.put(f"/api/products/{product_id}", json={"name": "   "})
    assert response.status_code == 400


def test_delete_product_success(client):
    """Verifica la eliminación física de un producto existente."""
    create_res = client.post("/api/products", json={"name": "Para Borrar"})
    product_id = create_res.get_json()["id"]

    delete_res = client.delete(f"/api/products/{product_id}")
    assert delete_res.status_code == 200
    assert delete_res.get_json()["deleted_id"] == product_id

    # Confirmar que ya no existe
    get_res = client.get(f"/api/products/{product_id}")
    assert get_res.status_code == 404


def test_method_not_allowed(client):
    """Verifica que un método HTTP no soportado sobre un endpoint retorne 405 en JSON."""
    response = client.post("/api/products/1", json={"data": 123})
    assert response.status_code == 405
    data = response.get_json()
    assert data["error"] == "Method Not Allowed"


def test_seed_is_idempotent():
    """
    Verifica que la inicialización con datos semilla no duplique registros si se llama repetidamente
    sobre la misma base de datos (idempotencia crucial para reinicios y workers múltiples).
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test_seed.db")

        class DiskConfig(Config):
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
            SEED_ON_START = True

        # Primera inicialización: debe crear exactamente 3 productos semilla
        app1 = create_app(DiskConfig)
        with app1.app_context():
            count1 = Products.query.count()
            assert count1 == 3

        # Segunda inicialización sobre el mismo archivo: debe mantener exactamente 3 productos
        app2 = create_app(DiskConfig)
        with app2.app_context():
            count2 = Products.query.count()
            assert count2 == 3
