#!/usr/bin/env python3
"""
Adaptador WSGI (PEP 3333) para despliegue productivo en Apache2 con mod_wsgi.

Referencia: 2024-01 Practica REST_MYSQL.pdf — Ejercicio 6:
'6. Despliegue el sitio web en Apache (Ver diapositivas de clase)'
'# sudo apt-get install libapache2-mod-wsgi-py3'

Por qué es necesario:
Apache HTTP Server en modo mod_wsgi busca un objeto invocable llamado 'application'
dentro del script apuntado por la directiva WSGIScriptAlias. Este archivo inserta
la ruta del proyecto en sys.path e importa la instancia 'app' de Flask bajo el
alias estándar 'application'.
"""

import os
import sys

# Insertar el directorio raíz de la aplicación en la ruta de búsqueda de módulos de Python
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from web.views import app as application  # noqa: E402
