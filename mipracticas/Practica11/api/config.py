"""
Módulo de configuración central para el microservicio Flask.

Por qué se diseña bajo 12-Factor App:
Permite aislar la configuración del código fuente mediante variables de entorno.
De este modo, el microservicio puede ejecutarse de forma transparente en entornos de pruebas
locales (SQLite en memoria), en máquinas virtuales Vagrant o en instancias AWS EC2
sin modificar una sola línea de código.
"""

import os


class Config:
    """Configuración estándar de producción y ejecución general."""

    # Por qué SQLite por defecto: Permite un arranque ultrarrápido (< 10 segundos)
    # sin dependencias externas pesadas en AWS EC2, cumpliendo con la cuota de tiempo.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:////var/lib/practica11/products.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    # Controla si se pueblan datos semilla iniciales al arrancar la base de datos
    SEED_ON_START = os.environ.get("SEED_ON_START", "true").lower() in ("true", "1", "yes")


class TestConfig(Config):
    """Configuración ligera para suites de pruebas automatizadas."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SEED_ON_START = False
