"""
Modelo ORM para la entidad Products compatible con la Práctica 9.

Por qué se mantiene el esquema exacto de la Práctica 9:
Garantiza retrocompatibilidad total con las pruebas de cURL y Postman previamente
validadas en el curso, permitiendo la reutilización limpia del contrato de datos.
"""

from extensions import db


class Products(db.Model):
    """Representa un producto de inventario en el catálogo de la tienda."""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True, default="")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    stock = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, name: str, description: str = "", price: float = 0.0, stock: int = 0) -> None:
        """Inicializa una nueva instancia de producto sanitizando cadenas de texto."""
        self.name = name.strip() if name else ""
        self.description = description.strip() if description else ""
        self.price = price
        self.stock = stock

    def to_dict(self) -> dict:
        """
        Serializa la entidad a diccionario nativo de Python para serialización JSON.

        Por qué se fuerza float(self.price):
        Los objetos Decimal retornados por columnas Numeric no son directamente
        serializables por el motor JSON estándar de Flask sin un formateador explícito.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "price": float(self.price) if self.price is not None else 0.0,
            "stock": int(self.stock) if self.stock is not None else 0
        }
