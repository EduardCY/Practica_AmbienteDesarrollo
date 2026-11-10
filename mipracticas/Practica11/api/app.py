"""
Factoría de aplicación y punto de entrada para el microservicio RESTful en Flask.

Por qué se utiliza el patrón Application Factory (create_app):
Permite instanciar múltiples aplicaciones con configuraciones distintas (por ejemplo,
una base de datos SQLite en memoria para tests automatizados y otra en disco para producción),
eliminando el estado global mutable y facilitando el testing unitario y de integración.
"""

import os
import socket
import urllib.error
import urllib.request
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from config import Config
from extensions import db
from products.controllers.product_controller import product_controller
from products.models.product_model import Products


def _fetch_imds_metadata() -> dict:
    """
    Consulta metadatos de la instancia EC2 mediante IMDSv2 (Instance Metadata Service v2).

    Por qué IMDSv2:
    AWS exige el uso de IMDSv2 (orientado a sesión con token de cabecera) en las AMIs
    recientes para mitigar ataques de falsificación de peticiones del lado del servidor (SSRF).
    Si el microservicio se ejecuta fuera de AWS (como en pruebas locales o Vagrant),
    el timeout estricto de 1 segundo evita cualquier bloqueo y asigna valores de contingencia.
    """
    token_url = "http://169.254.169.254/latest/api/token"
    meta_base = "http://169.254.169.254/latest/meta-data"
    token_headers = {"X-aws-ec2-metadata-token-ttl-seconds": "60"}

    metadata = {
        "provider": "local",
        "instance_id": "i-local-dev",
        "availability_zone": "local-az",
        "private_ipv4": "127.0.0.1",
        "public_ipv4": "127.0.0.1"
    }

    try:
        # Paso 1: Solicitar token de sesión IMDSv2
        req = urllib.request.Request(token_url, headers=token_headers, method="PUT")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            token = resp.read().decode("utf-8").strip()

        # Paso 2: Consultar metadatos individuales usando el token
        auth_headers = {"X-aws-ec2-metadata-token": token}

        def _get_field(path: str) -> str:
            r = urllib.request.Request(f"{meta_base}/{path}", headers=auth_headers)
            with urllib.request.urlopen(r, timeout=1.0) as res:
                return res.read().decode("utf-8").strip()

        metadata["provider"] = "aws-ec2"
        metadata["instance_id"] = _get_field("instance-id")
        metadata["availability_zone"] = _get_field("placement/availability-zone")
        metadata["private_ipv4"] = _get_field("local-ipv4")
        try:
            metadata["public_ipv4"] = _get_field("public-ipv4")
        except urllib.error.URLError:
            metadata["public_ipv4"] = "n/a"

    except Exception:
        # En entorno local, Docker o Vagrant, IMDSv2 no responde: mantenemos valores por defecto
        pass

    return metadata


def _seed_database_if_empty() -> None:
    """
    Inserta registros de demostración si la tabla de productos no tiene datos.

    Por qué es idempotente:
    Verifica primero el conteo de registros antes de insertar. Esto evita
    duplicados ante reinicios del servicio systemd o de la instancia EC2.
    """
    if Products.query.count() == 0:
        demo_products = [
            Products(
                name="Servidor EC2 t2.micro",
                description="Instancia virtual con 1 vCPU y 1 GiB de memoria en AWS us-east-1",
                price=8.50,
                stock=50
            ),
            Products(
                name="Volumen EBS gp3 20GB",
                description="Almacenamiento en bloque persistente SSD de alto rendimiento",
                price=1.60,
                stock=100
            ),
            Products(
                name="Dirección IP Elástica (EIP)",
                description="IPv4 estática reservada para servicios en la nube pública",
                price=3.65,
                stock=5
            )
        ]
        db.session.bulk_save_objects(demo_products)
        db.session.commit()


def _register_error_handlers(app: Flask) -> None:
    """
    Registra manejadores para devolver siempre respuestas en formato JSON estandarizado.

    Por qué es mandatorio:
    Evita que excepciones 400, 404, 405 o 500 retornen páginas HTML de Apache/Werkzeug
    que rompen clientes programáticos y scripts como cURL o Invoke-RestMethod.
    """
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = jsonify({
            "error": e.name,
            "message": e.description,
            "code": e.code
        })
        response.status_code = e.code
        return response

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        response = jsonify({
            "error": "Internal Server Error",
            "message": "Ha ocurrido un error no controlado en el microservicio.",
            "code": 500
        })
        response.status_code = 500
        return response


def create_app(config_class: type = Config) -> Flask:
    """
    Crea, configura y devuelve la instancia de la aplicación Flask.

    :param config_class: Clase con las directivas de configuración a cargar.
    :return: Instancia lista de Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Asegurar que el directorio de la base de datos SQLite exista en disco
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:////"):
        db_path = db_uri.replace("sqlite:////", "/")
        dir_name = os.path.dirname(db_path)
        if dir_name and not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)
            except OSError:
                pass

    db.init_app(app)
    app.register_blueprint(product_controller)
    _register_error_handlers(app)

    # Precargar metadatos una sola vez durante el inicio
    cached_metadata = _fetch_imds_metadata()

    with app.app_context():
        db.create_all()
        if app.config.get("SEED_ON_START", True):
            _seed_database_if_empty()

    @app.route("/", methods=["GET"])
    def root():
        """Página de inicio informativa de la API."""
        return jsonify({
            "title": "Práctica 11 - API REST Flask en AWS EC2",
            "author": "Eduard Criollo Yule",
            "endpoints": {
                "health": "/api/health",
                "products": "/api/products"
            },
            "status": "online"
        }), 200

    @app.route("/api/health", methods=["GET"])
    def health():
        """Endpoint de auditoría y health-check con información de la instancia."""
        return jsonify({
            "status": "ok",
            "hostname": socket.gethostname(),
            "ec2_metadata": cached_metadata
        }), 200

    return app


if __name__ == "__main__":
    # Servidor de desarrollo integrado para pruebas directas
    application = create_app()
    application.run(host="0.0.0.0", port=5000)
