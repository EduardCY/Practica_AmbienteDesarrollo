"""
Configuración central de la aplicación Flask y conexión al motor MySQL 8.0.

Por qué se diseña así:
- Permite inyectar credenciales desde variables de entorno siguiendo buenas prácticas
  de seguridad (OWASP), manteniendo como valores por defecto los parámetros del
  laboratorio ('localhost', 'root', 'root', 'myflaskapp') para compatibilidad
  inmediata con el repositorio base MiniWebApp.
"""

import os


class Config:
    """Clase de configuración cargada por Flask mediante app.config.from_object."""

    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'myflaskapp')

    # URI de conexión empleada por el ORM Flask-SQLAlchemy sobre el conector MySQLdb
    SQLALCHEMY_DATABASE_URI = (
        f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
