"""
Instancia compartida del ORM SQLAlchemy para persistencia relacional en MySQL.

Por qué se desacopla en un módulo independiente:
Evita importaciones circulares entre la inicialización de la aplicación Flask (views.py)
y las definiciones de modelos de dominio (Users y Products).
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
