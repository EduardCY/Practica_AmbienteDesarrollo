"""
Punto de entrada WSGI para servidores de aplicaciones de producción (Gunicorn).

Por qué se separa de app.py:
Permite a Gunicorn importar directamente la variable 'app' sin ejecutar
el bloque if __name__ == '__main__', cumpliendo estrictamente con la especificación PEP 3333.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
