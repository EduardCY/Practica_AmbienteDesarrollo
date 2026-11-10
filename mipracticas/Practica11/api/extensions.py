"""
Instancia compartida del ORM SQLAlchemy.

Por qué se desacopla en este módulo:
Permite a los modelos (products.models) y a los controladores (products.controllers)
acceder al objeto db sin incurrir en importaciones circulares contra la factoría
principal de la aplicación (app.py).
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
