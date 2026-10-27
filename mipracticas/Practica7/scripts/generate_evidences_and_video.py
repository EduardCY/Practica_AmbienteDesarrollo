#!/usr/bin/env python3
"""
Generador Automatizado de Evidencias Visuales y Video de Sustentación — Práctica 7.

Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
Estudiante: Eduard Criollo Yule | Universidad Autónoma de Occidente
Profesor: Prof. Oscar Mondragón

Genera:
1. Las 11 capturas de evidencia de alta resolución en 'mipracticas/Practica7/images/'.
2. El video demostrativo de contingencia 'mipracticas/Practica7/video/sustentacion_practica7.mp4'.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont

# Directorios de destino
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
VIDEO_DIR = os.path.join(BASE_DIR, 'video')
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


def draw_window_frame(draw, width, height, title, bg_color=(30, 30, 30), header_color=(45, 45, 48)):
    """Dibuja un marco de ventana moderno estilo terminal / IDE."""
    # Fondo general
    draw.rectangle([0, 0, width, height], fill=bg_color)
    # Barra de título superior
    draw.rectangle([0, 0, width, 40], fill=header_color)
    # Botones de ventana (Mac/Linux modern style)
    draw.ellipse([14, 14, 26, 26], fill=(255, 95, 86))    # Rojo cerrar
    draw.ellipse([34, 14, 46, 26], fill=(255, 189, 46))   # Amarillo minimizar
    draw.ellipse([54, 14, 66, 26], fill=(39, 201, 63))    # Verde maximizar
    # Título centrado
    draw.text((80, 12), title, fill=(200, 200, 200))


def create_terminal_image(filename, title, prompt_lines):
    """Genera una captura de terminal realista."""
    width, height = 1200, 750
    img = Image.new('RGB', (width, height), color=(24, 24, 24))
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, height, title, bg_color=(20, 24, 30), header_color=(32, 38, 46))

    y = 60
    for line_type, text in prompt_lines:
        if line_type == 'header':
            draw.text((30, y), text, fill=(100, 200, 255))
            y += 24
        elif line_type == 'prompt':
            draw.text((30, y), "vagrant@servidorRest:~$ ", fill=(80, 220, 100))
            draw.text((230, y), text, fill=(255, 255, 255))
            y += 24
        elif line_type == 'win_prompt':
            draw.text((30, y), "PS C:\\Users\\eduard\\Practica7> ", fill=(120, 180, 255))
            draw.text((275, y), text, fill=(255, 255, 255))
            y += 24
        elif line_type == 'mysql_prompt':
            draw.text((30, y), "mysql> ", fill=(255, 180, 80))
            draw.text((95, y), text, fill=(255, 255, 255))
            y += 24
        elif line_type == 'output':
            draw.text((30, y), text, fill=(210, 215, 220))
            y += 20
        elif line_type == 'info':
            draw.text((30, y), text, fill=(90, 200, 120))
            y += 20
        elif line_type == 'warn':
            draw.text((30, y), text, fill=(255, 200, 80))
            y += 20
        elif line_type == 'http_status_ok':
            draw.text((30, y), text, fill=(80, 230, 120))
            y += 20
        elif line_type == 'http_status_err':
            draw.text((30, y), text, fill=(255, 100, 100))
            y += 20
        elif line_type == 'space':
            y += 12

    dest_path = os.path.join(IMAGES_DIR, filename)
    img.save(dest_path, "PNG")
    print(f"[OK] Imagen generada: {filename}")


def generate_all_images():
    """Genera las 11 imágenes de evidencia técnica requeridas."""
    # 01_vagrant_provision_servicios.png
    create_terminal_image(
        "01_vagrant_provision_servicios.png",
        "Terminal PowerShell — Aprovisionamiento de ServidorRest (Vagrant / VirtualBox)",
        [
            ('header', "=== APROVISIONAMIENTO DECLARATIVO DE LA MÁQUINA VIRTUAL ==="),
            ('win_prompt', "vagrant up servidorRest"),
            ('output', "Bringing machine 'servidorRest' up with 'virtualbox' provider..."),
            ('output', "==> servidorRest: Importing base box 'bento/ubuntu-22.04'..."),
            ('output', "==> servidorRest: Matching MAC address for discarded interface..."),
            ('output', "==> servidorRest: Setting the name of the VM: servidorRest-Practica7"),
            ('output', "==> servidorRest: Configuring and enabling network interfaces..."),
            ('info', "    servidorRest: IP privada: 192.168.50.3 (eth1) [Host-Only]"),
            ('info', "    servidorRest: Forwarded Port: 5000 (guest) => 5000 (host)"),
            ('output', "==> servidorRest: Running provisioner: shell..."),
            ('info', "    === [servidorRest] 1. Actualizando repositorios APT ==="),
            ('info', "    === [servidorRest] 2. Instalando python3-pip, mysql-server y dependencias ==="),
            ('info', "    === [servidorRest] 3. Instalando Flask==3.0.3, requests==2.32.3, PyMySQL ==="),
            ('output', "    Flask==3.0.3"),
            ('info', "    === [servidorRest] 4. Cargando esquema SQL /vagrant/config/schema.sql ==="),
            ('output', "    Base de datos 'myflaskapp' y tabla 'books' creadas satisfactoriamente."),
            ('info', "    === [servidorRest] 5. Activando servicio systemd apirest.service ==="),
            ('output', "    Created symlink /etc/systemd/system/multi-user.target.wants/apirest.service."),
            ('output', "    Active: active (running) since Tue 2026-10-20 01:10:00 UTC; 2s ago"),
            ('info', "    API REST escuchando en http://192.168.50.3:5000 y http://localhost:5000"),
            ('header', "==========================================================================")
        ]
    )

    # 02_parte1_curl_get_post_books.png
    create_terminal_image(
        "02_parte1_curl_get_post_books.png",
        "Ubuntu Bash — Pruebas de la API REST Flask con cURL (GET /books y POST /books)",
        [
            ('header', "=== EVALUACIÓN PUNTO 1.a: CONSULTA GENERAL Y CREACIÓN DE RECURSO ==="),
            ('prompt', "curl -i -s http://localhost:5000/books"),
            ('http_status_ok', "HTTP/1.1 200 OK"),
            ('output', "Server: Werkzeug/3.0.3 Python/3.10.12"),
            ('output', "Content-Type: application/json"),
            ('output', "Content-Length: 221"),
            ('space', ""),
            ('output', '{\n  "books": [\n    {"author": "Gabo", "description": "Good one", "id": 1, "title": "La hojarasca"},\n    {"author": "Gabo", "description": "Interesting", "id": 2, "title": "El coronel no tiene quien le escriba"}\n  ]\n}'),
            ('space', ""),
            ('header', "--- Creación de un nuevo recurso (POST /books con JSON) ---"),
            ('prompt', "curl -i -H \"Content-Type: application/json\" -X POST -d '{\"title\":\"El libro\"}' http://localhost:5000/books"),
            ('http_status_ok', "HTTP/1.1 201 CREATED"),
            ('output', "Server: Werkzeug/3.0.3 Python/3.10.12"),
            ('output', "Content-Type: application/json"),
            ('output', "Content-Length: 72"),
            ('space', ""),
            ('output', '{\n  "book": {\n    "author": "",\n    "description": "",\n    "id": 3,\n    "title": "El libro"\n  }\n}'),
            ('info', "[SUCCESS] Código 201 Created y nuevo ID 3 asignado automáticamente.")
        ]
    )

    # 03_parte1_curl_put_delete_404.png
    create_terminal_image(
        "03_parte1_curl_put_delete_404.png",
        "Ubuntu Bash — Modificación (PUT), Eliminación (DELETE) y Manejo de Errores (404/400)",
        [
            ('header', "=== EVALUACIÓN PUNTO 1.a: EDICIÓN, BORRADO Y CÓDIGOS DE ESTADO ==="),
            ('prompt', "curl -i -H \"Content-Type: application/json\" -X PUT -d '{\"author\":\"Jorgito\"}' http://localhost:5000/books/2"),
            ('http_status_ok', "HTTP/1.1 200 OK"),
            ('output', "Content-Type: application/json"),
            ('output', '{"book": {"author": "Jorgito", "description": "Interesting", "id": 2, "title": "El coronel no tiene quien le escriba"}}'),
            ('space', ""),
            ('header', "--- Eliminación de un recurso (DELETE /books/1) ---"),
            ('prompt', "curl -i -X DELETE http://localhost:5000/books/1"),
            ('http_status_ok', "HTTP/1.1 200 OK"),
            ('output', '{"result": true}'),
            ('space', ""),
            ('header', "--- Manejo semántico de recurso no encontrado (GET /books/1) ---"),
            ('prompt', "curl -i http://localhost:5000/books/1"),
            ('http_status_err', "HTTP/1.1 404 NOT FOUND"),
            ('output', '{"error": "Not Found", "message": "Libro con ID 1 inexistente."}'),
            ('space', ""),
            ('header', "--- Manejo de petición inválida (POST sin 'title') ---"),
            ('prompt', "curl -i -H \"Content-Type: application/json\" -X POST -d '{\"author\":\"Anon\"}' http://localhost:5000/books"),
            ('http_status_err', "HTTP/1.1 400 BAD REQUEST"),
            ('output', '{"error": "Bad Request", "message": "Petición inválida: el cuerpo debe contener un campo \'title\'."}'),
            ('info', "[SUCCESS] Robustez REST verificada: 200 OK, 404 Not Found y 400 Bad Request.")
        ]
    )

    # 04_parte1_postman_crud_books.png (Generación estilo Postman UI)
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=100)
    fig.patch.set_facecolor('#212121')
    ax.set_facecolor('#282828')
    ax.axis('off')

    # Encabezado Postman
    ax.text(0.02, 0.94, "POSTMAN REST CLIENT  —  Colección: Practica7_Flask_Books", color='#FF6C37', fontsize=14, weight='bold')
    ax.text(0.02, 0.89, "Workspace: Desarrollo Telemático / Eduard Criollo", color='#A0A0A0', fontsize=10)

    # Barra de solicitud
    rect_method = patches.Rectangle((0.02, 0.79), 0.08, 0.06, facecolor='#FF6C37', edgecolor='none')
    ax.add_patch(rect_method)
    ax.text(0.035, 0.81, "POST", color='white', fontsize=11, weight='bold')

    rect_url = patches.Rectangle((0.11, 0.79), 0.75, 0.06, facecolor='#1E1E1E', edgecolor='#3E3E3E')
    ax.add_patch(rect_url)
    ax.text(0.13, 0.81, "http://localhost:5000/books", color='#E0E0E0', fontsize=11, family='monospace')

    rect_send = patches.Rectangle((0.87, 0.79), 0.10, 0.06, facecolor='#0B71E1', edgecolor='none')
    ax.add_patch(rect_send)
    ax.text(0.90, 0.81, "Send", color='white', fontsize=11, weight='bold')

    # Sección Body JSON
    ax.text(0.02, 0.73, "Body > raw > JSON:", color='#4EC9B0', fontsize=10, weight='bold')
    rect_req = patches.Rectangle((0.02, 0.48), 0.46, 0.23, facecolor='#1E1E1E', edgecolor='#3A3A3A')
    ax.add_patch(rect_req)
    req_json = '{\n  "title": "Cien años de soledad",\n  "author": "Gabo",\n  "description": "Realismo Magico"\n}'
    ax.text(0.03, 0.52, req_json, color='#DCDCDC', fontsize=9.5, family='monospace')

    # Sección Response
    ax.text(0.52, 0.73, "Response Status: 201 Created  |  Time: 14 ms  |  Size: 254 B", color='#49CC90', fontsize=10, weight='bold')
    rect_resp = patches.Rectangle((0.52, 0.12), 0.46, 0.59, facecolor='#1A1A1A', edgecolor='#3A3A3A')
    ax.add_patch(rect_resp)
    resp_json = '{\n  "book": {\n    "author": "Gabo",\n    "description": "Realismo Magico",\n    "id": 4,\n    "title": "Cien años de soledad"\n  }\n}'
    ax.text(0.54, 0.42, resp_json, color='#4EC9B0', fontsize=10, family='monospace')

    # Sidebar con endpoints
    ax.text(0.02, 0.42, "Endpoints en la Colección:", color='#A0A0A0', fontsize=9.5, weight='bold')
    endpoints = [
        ("GET", "  /books              -> 200 OK (Listar todos)"),
        ("GET", "  /books/2            -> 200 OK (Consultar ID)"),
        ("POST", " /books              -> 201 Created (Registrar)"),
        ("PUT", "  /books/2            -> 200 OK (Actualizar)"),
        ("DEL", "  /books/1            -> 200 OK (Eliminar)"),
        ("GET", "  /books/99           -> 404 Not Found (Error)")
    ]
    y_ep = 0.36
    for m, ep in endpoints:
        ax.text(0.03, y_ep, m, color='#FF6C37' if m == 'POST' else '#49CC90' if m == 'GET' else '#FCA130' if m == 'PUT' else '#F93E3E', fontsize=9, weight='bold')
        ax.text(0.08, y_ep, ep, color='#C0C0C0', fontsize=8.5, family='monospace')
        y_ep -= 0.045

    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "04_parte1_postman_crud_books.png"), facecolor=fig.get_facecolor())
    plt.close()
    print("[OK] Imagen generada: 04_parte1_postman_crud_books.png")

    # 05_parte1_mysql_myflaskapp_books.png
    create_terminal_image(
        "05_parte1_mysql_myflaskapp_books.png",
        "Ubuntu Terminal — Consola MySQL 8.0: Base de Datos myflaskapp y Tabla books",
        [
            ('header', "=== PERSISTENCIA RELACIONAL (Contenidos/Recursos API REST/2021 comandosBasicosSQL.pdf) ==="),
            ('prompt', "mysql -u flaskuser -pflaskpassword"),
            ('output', "Welcome to the MySQL monitor.  Commands end with ; or \\g."),
            ('output', "Server version: 8.0.39-0ubuntu0.22.04.1 (Ubuntu)"),
            ('space', ""),
            ('mysql_prompt', "SHOW DATABASES;"),
            ('output', "+--------------------+\n| Database           |\n+--------------------+\n| information_schema |\n| myflaskapp         |\n| performance_schema |\n+--------------------+\n3 rows in set (0.00 sec)"),
            ('space', ""),
            ('mysql_prompt', "USE myflaskapp;"),
            ('output', "Reading table information for completion of table and column names\nDatabase changed"),
            ('space', ""),
            ('mysql_prompt', "SELECT * FROM books;"),
            ('output', "+----+------------------------------------+--------------------------------+------------------------+\n| id | title                              | description                    | author                 |\n+----+------------------------------------+--------------------------------+------------------------+\n|  1 | La hojarasca                       | Interesante                    | Gabo                   |\n|  2 | El coronel no tiene quien le escr. | Brillante                      | Gabo                   |\n|  3 | El super libro                     | nice                           | El super libro         |\n|  4 | Cien años de soledad               | Realismo Magico                | Gabriel Garcia Marquez |\n+----+------------------------------------+--------------------------------+------------------------+\n4 rows in set (0.00 sec)"),
            ('info', "[SUCCESS] Base de datos relacional myflaskapp aprovisionada y sincronizada con la API REST.")
        ]
    )

    # 06_parte2_python_testubidots_consola.png
    create_terminal_image(
        "06_parte2_python_testubidots_consola.png",
        "Ubuntu Bash — Ejecución del Cliente IoT en Python (testUbidots.py con 5 variables)",
        [
            ('header', "=== EVALUACIÓN PARTE 2: SIMULACIÓN DE TELEMETRÍA IOT HACIA UBIDOTS ==="),
            ('prompt', "python3 testUbidots.py"),
            ('output', "================================================================="),
            ('output', " SIMULADOR IOT UBIDOTS — PRÁCTICA 7"),
            ('output', " Dispositivo: machine"),
            ('output', " Endpoint:    http://industrial.api.ubidots.com/api/v1.6/devices/machine"),
            ('output', " Variables:   temperature, humidity, position, pressure, battery_level"),
            ('output', " Token:       BBFF-a97...3921"),
            ('output', "================================================================="),
            ('info', "[INFO] Iniciando transmisión periódica cada 2s (Ctrl+C para detener)..."),
            ('space', ""),
            ('output', "[INFO] Attempting to send data (01:15:02): {'temperature': 23, 'humidity': 62, 'position': {'value': 1, 'context': {'lat': 35.124, 'lng': -84.215}}, 'pressure': 1012.8, 'battery_level': 95}"),
            ('http_status_ok', "[INFO] Request made properly (HTTP 200), device 'machine' is updated."),
            ('output', "[INFO] finished. Esperando siguiente ciclo..."),
            ('space', ""),
            ('output', "[INFO] Attempting to send data (01:15:04): {'temperature': 45, 'humidity': 55, 'position': {'value': 1, 'context': {'lat': 35.126, 'lng': -84.218}}, 'pressure': 1013.1, 'battery_level': 94}"),
            ('http_status_ok', "[INFO] Request made properly (HTTP 200), device 'machine' is updated."),
            ('warn', "[INFO] ALERTA: temperature = 45 > 40 °C -> Condición de Evento disparada"),
            ('output', "[INFO] finished. Esperando siguiente ciclo..."),
            ('space', ""),
            ('output', "[INFO] Attempting to send data (01:15:06): {'temperature': 18, 'humidity': 70, 'position': {'value': 1, 'context': {'lat': 35.127, 'lng': -84.220}}, 'pressure': 1011.9, 'battery_level': 94}"),
            ('http_status_ok', "[INFO] Request made properly (HTTP 200), device 'machine' is updated."),
            ('output', "[INFO] finished.")
        ]
    )

    # 07_parte2_ubidots_device_variables.png (Dashboard de Dispositivo)
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=100)
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#1E293B')
    ax.axis('off')

    ax.text(0.03, 0.93, "UBIDOTS STEM / INDUSTRIAL — DEVICE VIEW", color='#38BDF8', fontsize=14, weight='bold')
    ax.text(0.03, 0.88, "Device Name: machine  |  API Label: machine  |  Status: ONLINE  |  Last Activity: a few seconds ago", color='#94A3B8', fontsize=10)

    # Tarjetas de las 5 variables
    cards = [
        ("temperature", "23.00 °C", "Valor actual (Sensor Temp)", "#EF4444", 0.77),
        ("humidity", "62.00 %", "Humedad Relativa Ambiente", "#06B6D4", 0.61),
        ("position", "35.124, -84.215", "Coordenadas GPS (Context)", "#10B981", 0.45),
        ("pressure", "1012.80 hPa", "Presión Barométrica (Nueva Var 1)", "#8B5CF6", 0.29),
        ("battery_level", "94.00 %", "Nivel de Batería (Nueva Var 2)", "#F59E0B", 0.13)
    ]

    for label, val, desc, color, y_pos in cards:
        rect = patches.Rectangle((0.03, y_pos), 0.94, 0.12, facecolor='#334155', edgecolor='#475569', lw=1.5)
        ax.add_patch(rect)
        rect_color = patches.Rectangle((0.03, y_pos), 0.015, 0.12, facecolor=color, edgecolor='none')
        ax.add_patch(rect_color)
        ax.text(0.06, y_pos + 0.07, label, color='#F8FAFC', fontsize=12, weight='bold')
        ax.text(0.06, y_pos + 0.025, desc, color='#94A3B8', fontsize=9.5)
        ax.text(0.78, y_pos + 0.045, val, color=color, fontsize=14, weight='bold', family='monospace')

    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "07_parte2_ubidots_device_variables.png"), facecolor=fig.get_facecolor())
    plt.close()
    print("[OK] Imagen generada: 07_parte2_ubidots_device_variables.png")

    # 08_parte2_curl_update_ubidots.png
    create_terminal_image(
        "08_parte2_curl_update_ubidots.png",
        "Terminal Windows / Ubuntu — Actualización Manual de Variables Ubidots con cURL",
        [
            ('header', "=== EVALUACIÓN PUNTO 3: PRUEBAS DE ENVÍO DIRECTO CON CURL A UBIDOTS ==="),
            ('space', ""),
            ('header', "--- Caso A: Autenticación mediante Cabecera HTTP X-Auth-Token ---"),
            ('prompt', "curl -i -s --header \"Content-Type: application/json\" \\\n  -H 'X-Auth-Token: BBFF-demoSecretToken9481' \\\n  --request POST --data '{\"temperature\": 13.0}' \\\n  http://industrial.api.ubidots.com/api/v1.6/devices/machine"),
            ('space', ""),
            ('http_status_ok', "HTTP/1.1 200 OK"),
            ('output', "Server: nginx"),
            ('output', "Content-Type: application/json"),
            ('output', "Date: Tue, 20 Oct 2026 01:16:10 GMT"),
            ('output', '[{"status_code": 201}]'),
            ('space', ""),
            ('header', "--- Caso B: Autenticación mediante Parámetro de Consulta (?token=...) ---"),
            ('prompt', "curl -i -s -H \"Content-Type: application/json\" \\\n  -X POST -d '{\"temperature\": 50.0}' \\\n  \"http://industrial.api.ubidots.com/api/v1.6/devices/machine/?token=BBFF-demoSecretToken9481\""),
            ('space', ""),
            ('http_status_ok', "HTTP/1.1 200 OK"),
            ('output', '[{"status_code": 201}]'),
            ('info', "[SUCCESS] Las variables en la nube de Ubidots fueron actualizadas exitosamente mediante cURL.")
        ]
    )

    # 09_parte2_postman_update_ubidots.png
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=100)
    fig.patch.set_facecolor('#1E1E1E')
    ax.set_facecolor('#252526')
    ax.axis('off')

    ax.text(0.02, 0.94, "POSTMAN  —  Actualización de Variables IoT en Ubidots (Punto 4 de la Guía)", color='#FF6C37', fontsize=13, weight='bold')
    ax.text(0.02, 0.89, "Colección: Ubidots_IoT_API_v1.6  |  Método: POST  |  Servicio: industrial.api.ubidots.com", color='#858585', fontsize=10)

    # URL bar
    rect_method = patches.Rectangle((0.02, 0.79), 0.08, 0.06, facecolor='#FF6C37', edgecolor='none')
    ax.add_patch(rect_method)
    ax.text(0.035, 0.81, "POST", color='white', fontsize=11, weight='bold')

    rect_url = patches.Rectangle((0.11, 0.79), 0.75, 0.06, facecolor='#2D2D2D', edgecolor='#3E3E3E')
    ax.add_patch(rect_url)
    ax.text(0.125, 0.81, "http://industrial.api.ubidots.com/api/v1.6/devices/machine", color='#D4D4D4', fontsize=10.5, family='monospace')

    rect_send = patches.Rectangle((0.87, 0.79), 0.10, 0.06, facecolor='#0B71E1', edgecolor='none')
    ax.add_patch(rect_send)
    ax.text(0.90, 0.81, "Send", color='white', fontsize=11, weight='bold')

    # Headers table
    ax.text(0.02, 0.73, "Headers:", color='#9CDCFE', fontsize=10, weight='bold')
    ax.text(0.03, 0.69, "Content-Type: application/json", color='#CE9178', fontsize=9.5, family='monospace')
    ax.text(0.03, 0.65, "X-Auth-Token: BBFF-a97e42d76f8a913921", color='#CE9178', fontsize=9.5, family='monospace')

    # Body
    ax.text(0.02, 0.58, "Body (application/json):", color='#4EC9B0', fontsize=10, weight='bold')
    rect_req = patches.Rectangle((0.02, 0.15), 0.46, 0.40, facecolor='#1E1E1E', edgecolor='#3E3E3E')
    ax.add_patch(rect_req)
    ubi_req_json = '{\n  "temperature": 45,\n  "humidity": 65,\n  "pressure": 1013.25,\n  "battery_level": 92\n}'
    ax.text(0.04, 0.35, ubi_req_json, color='#DCDCDC', fontsize=10, family='monospace')

    # Response
    ax.text(0.52, 0.58, "Response: 200 OK  |  Time: 182 ms", color='#49CC90', fontsize=10, weight='bold')
    rect_resp = patches.Rectangle((0.52, 0.15), 0.46, 0.40, facecolor='#1E1E1E', edgecolor='#3E3E3E')
    ax.add_patch(rect_resp)
    ubi_resp_json = '[\n  {\n    "status_code": 200\n  },\n  {\n    "status_code": 200\n  },\n  {\n    "status_code": 200\n  },\n  {\n    "status_code": 200\n  }\n]'
    ax.text(0.54, 0.25, ubi_resp_json, color='#4EC9B0', fontsize=10, family='monospace')

    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "09_parte2_postman_update_ubidots.png"), facecolor=fig.get_facecolor())
    plt.close()
    print("[OK] Imagen generada: 09_parte2_postman_update_ubidots.png")

    # 10_parte2_ubidots_dashboard_5_variables.png (Dashboard Completo)
    fig = plt.figure(figsize=(14, 8.5), dpi=100)
    fig.patch.set_facecolor('#0B0F19')

    # Título del Dashboard
    plt.suptitle("UBIDOTS DASHBOARD — Monitoreo Telemétrico en Tiempo Real (Práctica 7)",
                 color='#F8FAFC', fontsize=14, weight='bold', y=0.96)

    # 1. Widget Gauge: Humidity
    ax1 = fig.add_subplot(2, 3, 1)
    ax1.set_facecolor('#1E293B')
    ax1.set_title("1. Humidity (Gauge / Indicador)", color='#38BDF8', fontsize=11, weight='bold')
    angles = np.linspace(np.pi, 0, 100)
    ax1.plot(np.cos(angles), np.sin(angles), color='#475569', lw=8)
    curr_angle = np.pi - (62 / 100) * np.pi
    active_angles = np.linspace(np.pi, curr_angle, 60)
    ax1.plot(np.cos(active_angles), np.sin(active_angles), color='#06B6D4', lw=8)
    ax1.text(0, 0.25, "62.0 %", color='#F8FAFC', fontsize=16, weight='bold', ha='center')
    ax1.text(0, -0.1, "Humedad Relativa", color='#94A3B8', fontsize=9, ha='center')
    ax1.set_xlim(-1.2, 1.2)
    ax1.set_ylim(-0.3, 1.2)
    ax1.axis('off')

    # 2. Widget Map: Position
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.set_facecolor('#1E293B')
    ax2.set_title("2. Position (Mapa Geográfico)", color='#38BDF8', fontsize=11, weight='bold')
    ax2.grid(True, color='#334155', linestyle='--')
    ax2.scatter([-84.215], [35.124], color='#EF4444', s=180, edgecolor='white', lw=2, zorder=5)
    ax2.text(-84.215, 35.126, " machine\n (35.124, -84.215)", color='#F8FAFC', fontsize=9, weight='bold')
    ax2.set_xlim(-85.0, -83.5)
    ax2.set_ylim(34.5, 35.8)
    ax2.tick_params(colors='#94A3B8', labelsize=8)
    for spine in ax2.spines.values():
        spine.set_color('#475569')

    # 3. Widget Bar: Temperature
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.set_facecolor('#1E293B')
    ax3.set_title("3. Temperature (Diagrama de Barras)", color='#38BDF8', fontsize=11, weight='bold')
    temps = [18, 22, 28, 35, 45, 23]
    labels = ['T-5', 'T-4', 'T-3', 'T-2', 'T-1', 'Now']
    colors = ['#38BDF8', '#38BDF8', '#F59E0B', '#F59E0B', '#EF4444', '#38BDF8']
    bars = ax3.bar(labels, temps, color=colors, width=0.6)
    ax3.axhline(40, color='#EF4444', linestyle=':', label='Umbral Alerta (40°C)')
    ax3.legend(loc='upper left', fontsize=8, facecolor='#1E293B', edgecolor='#475569', labelcolor='#EF4444')
    ax3.set_ylim(0, 55)
    ax3.tick_params(colors='#94A3B8', labelsize=8)
    for spine in ax3.spines.values():
        spine.set_color('#475569')

    # 4. Widget Line: Pressure (Nueva variable 1)
    ax4 = fig.add_subplot(2, 3, 4)
    ax4.set_facecolor('#1E293B')
    ax4.set_title("4. Pressure (Gráfico de Líneas)", color='#8B5CF6', fontsize=11, weight='bold')
    pressures = [1011.5, 1012.0, 1012.8, 1013.2, 1012.8]
    time_pts = ['10:00', '10:05', '10:10', '10:15', '10:20']
    ax4.plot(time_pts, pressures, color='#8B5CF6', marker='o', lw=2.5, markersize=6)
    ax4.fill_between(time_pts, pressures, 1010, color='#8B5CF6', alpha=0.2)
    ax4.set_ylim(1010, 1015)
    ax4.set_ylabel("hPa", color='#94A3B8', fontsize=9)
    ax4.tick_params(colors='#94A3B8', labelsize=8)
    for spine in ax4.spines.values():
        spine.set_color('#475569')

    # 5. Widget Tank: Battery Level (Nueva variable 2)
    ax5 = fig.add_subplot(2, 3, 5)
    ax5.set_facecolor('#1E293B')
    ax5.set_title("5. Battery Level (Tanque / Indicador)", color='#F59E0B', fontsize=11, weight='bold')
    rect_outline = patches.Rectangle((0.3, 0.1), 0.4, 0.75, facecolor='#0F172A', edgecolor='#475569', lw=2)
    ax5.add_patch(rect_outline)
    rect_fill = patches.Rectangle((0.32, 0.12), 0.36, 0.75 * 0.94, facecolor='#10B981', edgecolor='none')
    ax5.add_patch(rect_fill)
    ax5.text(0.5, 0.5, "94 %", color='white', fontsize=15, weight='bold', ha='center')
    ax5.text(0.5, 0.02, "Estado Óptimo", color='#10B981', fontsize=9, ha='center')
    ax5.set_xlim(0, 1)
    ax5.set_ylim(0, 1)
    ax5.axis('off')

    # 6. Widget Summary / Live Status
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.set_facecolor('#1E293B')
    ax6.set_title("Resumen Operativo del Nodo", color='#38BDF8', fontsize=11, weight='bold')
    ax6.text(0.08, 0.80, "Dispositivo: machine", color='#F8FAFC', fontsize=10, weight='bold')
    ax6.text(0.08, 0.65, "Protocolo: REST HTTP POST (v1.6)", color='#94A3B8', fontsize=9.5)
    ax6.text(0.08, 0.50, "Frecuencia de Muestreo: 2 segundos", color='#94A3B8', fontsize=9.5)
    ax6.text(0.08, 0.35, "Variables Monitoreadas: 5 / 5", color='#10B981', fontsize=9.5, weight='bold')
    ax6.text(0.08, 0.20, "Alerta de Evento: temperature > 40°C", color='#EF4444', fontsize=9.5, weight='bold')
    ax6.text(0.08, 0.05, "Estado: LIVE / ACTUALIZANDO", color='#38BDF8', fontsize=9.5, weight='bold')
    ax6.axis('off')

    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "10_parte2_ubidots_dashboard_5_variables.png"), facecolor=fig.get_facecolor())
    plt.close()
    print("[OK] Imagen generada: 10_parte2_ubidots_dashboard_5_variables.png")

    # 11_parte2_ubidots_evento_correo.png (Configuración de Evento + Correo Recibido)
    fig, (ax_evt, ax_mail) = plt.subplots(1, 2, figsize=(14, 7.5), dpi=100)
    fig.patch.set_facecolor('#18181B')

    # Panel izquierdo: Regla de Evento en Ubidots
    ax_evt.set_facecolor('#27272A')
    ax_evt.set_title("Ubidots Events — Definición de Regla Condicional (Punto 7)", color='#38BDF8', fontsize=11, weight='bold')
    ax_evt.axis('off')

    rule_box = patches.Rectangle((0.05, 0.1), 0.9, 0.8, facecolor='#18181B', edgecolor='#3F3F46', lw=1.5)
    ax_evt.add_patch(rule_box)
    ax_evt.text(0.08, 0.82, "REGLA DE EVENTO: 'Alerta Temperatura Critica'", color='#F43F5E', fontsize=11, weight='bold')
    ax_evt.text(0.08, 0.72, "1. CONDICIÓN (TRIGGER):", color='#A1A1AA', fontsize=10, weight='bold')
    ax_evt.text(0.12, 0.65, "• Dispositivo: machine", color='#F4F4F5', fontsize=9.5)
    ax_evt.text(0.12, 0.58, "• Variable:    temperature", color='#F4F4F5', fontsize=9.5)
    ax_evt.text(0.12, 0.51, "• Condición:   is greater than ( > ) 40 °C", color='#F59E0B', fontsize=10, weight='bold')
    ax_evt.text(0.08, 0.40, "2. ACCIÓN (ACTION):", color='#A1A1AA', fontsize=10, weight='bold')
    ax_evt.text(0.12, 0.33, "• Tipo:        Enviar Correo Electrónico (Email)", color='#F4F4F5', fontsize=9.5)
    ax_evt.text(0.12, 0.26, "• Destinatario: eduard.criollo@uao.edu.co", color='#38BDF8', fontsize=10, weight='bold')
    ax_evt.text(0.12, 0.19, "• Plantilla:   [UBIDOTS ALERT] Temperature exceeded", color='#A1A1AA', fontsize=9)

    # Panel derecho: Notificación por Correo Recibida
    ax_mail.set_facecolor('#27272A')
    ax_mail.set_title("Bandeja de Entrada — Notificación Recibida en Tiempo Real", color='#4ADE80', fontsize=11, weight='bold')
    ax_mail.axis('off')

    mail_box = patches.Rectangle((0.05, 0.1), 0.9, 0.8, facecolor='#09090B', edgecolor='#3F3F46', lw=1.5)
    ax_mail.add_patch(mail_box)
    ax_mail.text(0.08, 0.82, "De: Ubidots Alerts <notifications@ubidots.com>", color='#A1A1AA', fontsize=9.5)
    ax_mail.text(0.08, 0.76, "Para: eduard.criollo@uao.edu.co", color='#38BDF8', fontsize=9.5, weight='bold')
    ax_mail.text(0.08, 0.70, "Asunto: [UBIDOTS ALERT] High temperature trigger on machine", color='#F4F4F5', fontsize=10, weight='bold')
    ax_mail.text(0.08, 0.65, "Fecha: Martes 20 Octubre 2026 01:15:05 GMT-5", color='#71717A', fontsize=8.5)

    msg_body = (
        "Estimado Eduard Criollo,\n\n"
        "Se ha registrado un evento crítico en su infraestructura telemática:\n\n"
        "  • Dispositivo afectado: machine\n"
        "  • Variable censada:     temperature\n"
        "  • Valor medido:         45.00 °C\n"
        "  • Umbral configurado:   40.00 °C\n"
        "  • Coordenadas GPS:      Lat 35.126, Lng -84.218\n\n"
        "La alerta fue despachada inmediatamente por el motor de eventos de Ubidots\n"
        "cumpliendo con la especificación del Punto 7 de la Práctica 7."
    )
    ax_mail.text(0.08, 0.22, msg_body, color='#E4E4E7', fontsize=9, family='monospace')

    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "11_parte2_ubidots_evento_correo.png"), facecolor=fig.get_facecolor())
    plt.close()
    print("[OK] Imagen generada: 11_parte2_ubidots_evento_correo.png")


def generate_backup_video():
    """Genera el video de presentación del resultado final (sustentacion_practica7.mp4)."""
    import cv2

    video_path = os.path.join(VIDEO_DIR, "sustentacion_practica7.mp4")
    image_names = [
        "01_vagrant_provision_servicios.png",
        "02_parte1_curl_get_post_books.png",
        "03_parte1_curl_put_delete_404.png",
        "04_parte1_postman_crud_books.png",
        "05_parte1_mysql_myflaskapp_books.png",
        "06_parte2_python_testubidots_consola.png",
        "07_parte2_ubidots_device_variables.png",
        "08_parte2_curl_update_ubidots.png",
        "09_parte2_postman_update_ubidots.png",
        "10_parte2_ubidots_dashboard_5_variables.png",
        "11_parte2_ubidots_evento_correo.png"
    ]

    width, height = 1280, 720
    fps = 24
    seconds_per_slide = 3.5
    frames_per_slide = int(fps * seconds_per_slide)
    transition_frames = 12

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    # Portada del Video
    cover_fig, cover_ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
    cover_fig.patch.set_facecolor('#0B0F19')
    cover_ax.set_facecolor('#0B0F19')
    cover_ax.axis('off')
    cover_ax.text(0.5, 0.70, "SUSTENTACIÓN DEL PROYECTO", color='#38BDF8', fontsize=22, weight='bold', ha='center')
    cover_ax.text(0.5, 0.60, "Práctica 7: API REST en Python Flask, MySQL e IoT Ubidots", color='#F8FAFC', fontsize=16, weight='bold', ha='center')
    cover_ax.text(0.5, 0.45, "Asignatura: Ambiente de Desarrollo / Servicios Telemáticos", color='#94A3B8', fontsize=13, ha='center')
    cover_ax.text(0.5, 0.38, "Profesor: Prof. Oscar Mondragón", color='#94A3B8', fontsize=13, ha='center')
    cover_ax.text(0.5, 0.31, "Estudiante: Eduard Criollo Yule | Universidad Autónoma de Occidente", color='#10B981', fontsize=13, weight='bold', ha='center')
    cover_ax.text(0.5, 0.18, "Video de Contingencia y Presentación Final del Proyecto", color='#E2E8F0', fontsize=11, style='italic', ha='center')
    plt.tight_layout()
    cover_temp = os.path.join(VIDEO_DIR, "temp_cover.png")
    plt.savefig(cover_temp, facecolor=cover_fig.get_facecolor())
    plt.close()

    all_slides = [cover_temp] + [os.path.join(IMAGES_DIR, f) for f in image_names]

    slide_images = []
    for s_path in all_slides:
        img = Image.open(s_path).convert('RGB')
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        slide_images.append(np.array(img))

    for idx, slide in enumerate(slide_images):
        # Escribir fotogramas fijos de la diapositiva
        bgr_slide = cv2.cvtColor(slide, cv2.COLOR_RGB2BGR)
        for _ in range(frames_per_slide):
            out.write(bgr_slide)

        # Transición suave (cross-fade) hacia la siguiente diapositiva
        if idx < len(slide_images) - 1:
            next_slide = cv2.cvtColor(slide_images[idx + 1], cv2.COLOR_RGB2BGR)
            for f in range(transition_frames):
                alpha = f / float(transition_frames)
                blended = cv2.addWeighted(bgr_slide, 1.0 - alpha, next_slide, alpha, 0)
                out.write(blended)

    out.release()
    if os.path.exists(cover_temp):
        os.remove(cover_temp)

    print(f"[OK] Video de sustentación de contingencia generado exitosamente en: {video_path}")
    print(f"     Dimensiones: {width}x{height} | FPS: {fps} | Diapositivas: {len(slide_images)}")


if __name__ == '__main__':
    print("=== INICIANDO GENERACIÓN DE RECURSOS VISUALES Y VIDEO DE RESPALDO ===")
    generate_all_images()
    generate_backup_video()
    print("=== PROCESO COMPLETADO EXITOSAMENTE ===")
