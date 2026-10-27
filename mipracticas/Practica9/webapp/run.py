#!/usr/bin/env python3
"""
Punto de entrada principal para ejecutar el servidor de desarrollo Flask / systemd.

Escucha en todas las interfaces de red (0.0.0.0) sobre el puerto 5000 para permitir
el acceso tanto desde la red privada Host-Only (192.168.60.3:5000) como desde el
anfitrión Windows vía redirección de puertos (localhost:5000).
"""

from web.views import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
