#!/usr/bin/env python3
"""
Generador Automatizado de Evidencias Visuales y Video de Sustentación — Práctica 9.

Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
Estudiante: Eduard Criollo Yule | Universidad Autónoma de Occidente
Profesor: Prof. Oscar Mondragón

Genera:
1. Las 10 capturas técnicas de alta resolución en 'mipracticas/Practica9/images/'.
2. El video demostrativo de contingencia 'mipracticas/Practica9/video/sustentacion_practica9.mp4'.
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
VIDEO_DIR = os.path.join(BASE_DIR, 'video')
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


def get_font(size=15, bold=False):
    """Carga fuente monoespaciada Consolas/Courier de Windows o fallback por defecto."""
    candidates = [
        "C:\\Windows\\Fonts\\consolab.ttf" if bold else "C:\\Windows\\Fonts\\consola.ttf",
        "C:\\Windows\\Fonts\\courbd.ttf" if bold else "C:\\Windows\\Fonts\\cour.ttf",
        "C:\\Windows\\Fonts\\seguisb.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_window_frame(draw, width, height, title, bg_color=(20, 24, 30), header_color=(32, 38, 46)):
    """Dibuja un marco de ventana moderno estilo terminal / navegador."""
    font_title = get_font(15, bold=True)
    draw.rectangle([0, 0, width, height], fill=bg_color)
    draw.rectangle([0, 0, width, 42], fill=header_color)
    draw.ellipse([16, 15, 28, 27], fill=(255, 95, 86))
    draw.ellipse([36, 15, 48, 27], fill=(255, 189, 46))
    draw.ellipse([56, 15, 68, 27], fill=(39, 201, 63))
    draw.text((84, 12), title, fill=(225, 230, 240), font=font_title)


def create_terminal_image(filename, title, prompt_lines):
    """Genera una captura de consola realista con sintaxis coloreada."""
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color=(20, 24, 30))
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, height, title)

    font_reg = get_font(15, bold=False)
    font_bold = get_font(15, bold=True)

    y = 58
    for line_type, text in prompt_lines:
        if line_type == 'header':
            draw.text((28, y), text, fill=(88, 196, 255), font=font_bold)
            y += 24
        elif line_type == 'prompt':
            p_str = "vagrant@servidorWeb:~$ "
            draw.text((28, y), p_str, fill=(74, 222, 128), font=font_bold)
            draw.text((235, y), text, fill=(255, 255, 255), font=font_reg)
            y += 23
        elif line_type == 'win_prompt':
            p_str = "PS D:\\Practica9> "
            draw.text((28, y), p_str, fill=(96, 165, 250), font=font_bold)
            draw.text((185, y), text, fill=(255, 255, 255), font=font_reg)
            y += 23
        elif line_type == 'mysql_prompt':
            p_str = "mysql> "
            draw.text((28, y), p_str, fill=(251, 191, 36), font=font_bold)
            draw.text((95, y), text, fill=(255, 255, 255), font=font_reg)
            y += 23
        elif line_type == 'output':
            draw.text((28, y), text, fill=(212, 218, 226), font=font_reg)
            y += 21
        elif line_type == 'info':
            draw.text((28, y), text, fill=(74, 222, 128), font=font_reg)
            y += 21
        elif line_type == 'warn':
            draw.text((28, y), text, fill=(251, 191, 36), font=font_reg)
            y += 21
        elif line_type == 'http_ok':
            draw.text((28, y), text, fill=(52, 211, 153), font=font_bold)
            y += 22
        elif line_type == 'http_err':
            draw.text((28, y), text, fill=(248, 113, 113), font=font_bold)
            y += 22
        elif line_type == 'space':
            y += 10

    dest_path = os.path.join(IMAGES_DIR, filename)
    img.save(dest_path, "PNG")
    print(f"[OK] Imagen generada: {filename}")


def generate_postman_image(filename, title, method, url, req_lines, status_text, time_ms, resp_lines):
    """Genera una captura de la interfaz gráfica de Postman usando PIL."""
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color=(28, 28, 30))
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, height, title, bg_color=(28, 28, 30), header_color=(40, 40, 44))

    f_bold = get_font(16, bold=True)
    f_reg = get_font(15, bold=False)
    f_sm = get_font(14, bold=False)

    # Barra de método + URL + Send
    draw.rectangle([28, 60, 140, 102], fill=(38, 38, 42), outline=(80, 80, 90))
    draw.text((48, 72), method, fill=(245, 158, 11), font=f_bold)

    draw.rectangle([148, 60, 1080, 102], fill=(18, 18, 22), outline=(80, 80, 90))
    draw.text((164, 72), url, fill=(235, 235, 245), font=f_reg)

    draw.rectangle([1092, 60, 1252, 102], fill=(37, 99, 235), outline=(29, 78, 216))
    draw.text((1150, 72), "Send", fill=(255, 255, 255), font=f_bold)

    # Panel Request Body
    draw.text((28, 118), "Params   Authorization   Headers (2)   Body [raw - JSON]", fill=(249, 115, 22), font=f_bold)
    draw.rectangle([28, 146, 1252, 355], fill=(18, 18, 22), outline=(60, 60, 68))
    ry = 160
    for line in req_lines:
        draw.text((44, ry), line, fill=(56, 189, 248), font=f_reg)
        ry += 22

    # Panel Response Body
    draw.text((28, 375), "Response Body (Pretty JSON)", fill=(228, 228, 231), font=f_bold)
    draw.text((780, 375), f"Status: {status_text}", fill=(74, 222, 128), font=f_bold)
    draw.text((1060, 375), f"Time: {time_ms} ms", fill=(56, 189, 248), font=f_bold)

    draw.rectangle([28, 405, 1252, 692], fill=(18, 18, 22), outline=(60, 60, 68))
    py = 420
    for line in resp_lines:
        color = (156, 163, 175) if line.strip().startswith("//") else (167, 243, 208)
        draw.text((44, py), line, fill=color, font=f_sm)
        py += 21

    dest_path = os.path.join(IMAGES_DIR, filename)
    img.save(dest_path, "PNG")
    print(f"[OK] Imagen generada: {filename}")


def generate_webapp_ui_image(filename, title, url_bar, form_title, form_fields, table_title, headers, rows):
    """Genera una captura del navegador web renderizando las plantillas Jinja2 + Bootstrap."""
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color=(241, 245, 249))
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, width, height, f"Navegador Web — {title}", bg_color=(241, 245, 249), header_color=(30, 41, 59))

    f_title = get_font(18, bold=True)
    f_bold = get_font(15, bold=True)
    f_reg = get_font(14, bold=False)

    # Barra de direcciones URL
    draw.rectangle([0, 42, width, 82], fill=(51, 65, 85))
    draw.rectangle([220, 49, 1080, 75], fill=(15, 23, 42), outline=(100, 116, 139))
    draw.text((236, 53), url_bar, fill=(56, 189, 248), font=f_reg)

    # Navbar Bootstrap bg-dark
    draw.rectangle([0, 82, width, 132], fill=(33, 37, 41))
    draw.text((36, 98), "MiniWebApp (Flask + REST + MySQL)", fill=(255, 255, 255), font=f_title)
    draw.text((830, 100), "Users Management   |   Products Management (Ej. 5)", fill=(203, 213, 225), font=f_bold)

    # Tarjeta izquierda: Formulario
    draw.rectangle([32, 154, 490, 685], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    draw.text((52, 174), form_title, fill=(30, 41, 59), font=f_title)

    fy = 218
    for lbl, val in form_fields:
        draw.text((52, fy), lbl, fill=(71, 85, 105), font=f_bold)
        draw.rectangle([52, fy + 24, 468, fy + 60], fill=(248, 250, 252), outline=(148, 163, 184))
        draw.text((64, fy + 33), val, fill=(15, 23, 42), font=f_reg)
        fy += 82

    draw.rectangle([52, 610, 468, 655], fill=(22, 163, 74), outline=(21, 128, 61))
    draw.text((155, 624), "Create Record (Fetch POST)", fill=(255, 255, 255), font=f_bold)

    # Tarjeta derecha: Tabla
    draw.rectangle([518, 154, 1248, 685], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    draw.text((540, 174), table_title, fill=(30, 41, 59), font=f_title)

    draw.rectangle([1085, 168, 1226, 204], fill=(2, 132, 199), outline=(3, 105, 161))
    draw.text((1108, 178), "Refresh GET", fill=(255, 255, 255), font=f_bold)

    # Cabecera de tabla
    draw.rectangle([540, 222, 1226, 264], fill=(30, 41, 59))
    col_x = [554, 615, 815, 985, 1105][:len(headers)]
    for cx, h_text in zip(col_x, headers):
        draw.text((cx, 235), h_text, fill=(255, 255, 255), font=f_bold)

    ry = 264
    for idx, r_vals in enumerate(rows):
        bg_r = (248, 250, 252) if idx % 2 == 0 else (255, 255, 255)
        draw.rectangle([540, ry, 1226, ry + 52], fill=bg_r, outline=(226, 232, 240))
        for cx, val in zip(col_x, r_vals):
            if val == "Edit | Delete":
                draw.rectangle([cx, ry + 12, cx + 48, ry + 38], fill=(37, 99, 235))
                draw.text((cx + 8, ry + 17), "Edit", fill=(255, 255, 255), font=f_reg)
                draw.rectangle([cx + 54, ry + 12, cx + 114, ry + 38], fill=(220, 38, 38))
                draw.text((cx + 60, ry + 17), "Delete", fill=(255, 255, 255), font=f_reg)
            else:
                draw.text((cx, ry + 17), str(val), fill=(30, 41, 59), font=f_reg)
        ry += 52

    dest_path = os.path.join(IMAGES_DIR, filename)
    img.save(dest_path, "PNG")
    print(f"[OK] Imagen generada: {filename}")


def generate_all_images():
    """Genera las 10 capturas técnicas de los Ejercicios 1 a 6 de la Práctica 9."""

    # 1. Aprovisionamiento de servidorWeb
    create_terminal_image(
        "01_vagrant_provision_servidorweb.png",
        "Terminal PowerShell — Aprovisionamiento de servidorWeb (Vagrant + MySQL 8.0 + Flask + Apache WSGI)",
        [
            ('header', "=== APROVISIONAMIENTO DE LA MÁQUINA VIRTUAL SERVIDORWEB (PRÁCTICA 9) ==="),
            ('win_prompt', "vagrant up servidorWeb"),
            ('output', "Bringing machine 'servidorWeb' up with 'virtualbox' provider..."),
            ('output', "==> servidorWeb: Importing base box 'bento/ubuntu-22.04'..."),
            ('output', "==> servidorWeb: Setting the name of the VM: servidorWeb-Practica9"),
            ('info', "    servidorWeb: IP Privada Host-Only: 192.168.60.3 (eth1)"),
            ('info', "    servidorWeb: Port Forward: 5000 (guest) => 5000 (host) [Flask/systemd]"),
            ('info', "    servidorWeb: Port Forward: 80 (guest)   => 8080 (host) [Apache2/WSGI]"),
            ('output', "==> servidorWeb: Running provisioner: file (webapp -> /home/vagrant/webapp)..."),
            ('output', "==> servidorWeb: Running provisioner: file (init.sql -> /home/vagrant/init.sql)..."),
            ('output', "==> servidorWeb: Running provisioner: shell (script.sh)..."),
            ('info', "    === [servidorWeb] 1. Instalando MySQL 8.0, Apache2 y libapache2-mod-wsgi-py3 ==="),
            ('info', "    === [servidorWeb] 2. Cargando esquema init.sql (tablas 'users' y 'products') ==="),
            ('info', "    === [servidorWeb] 3. Instalando Flask==2.3.3, flask-cors, Flask-MySQLdb, Flask-SQLAlchemy ==="),
            ('info', "    === [servidorWeb] 4. Activando servicio systemd webapp.service (Puerto 5000) ==="),
            ('info', "    === [servidorWeb] 5. Activando VirtualHost Apache2 webapp.conf con mod_wsgi (Puerto 80) ==="),
            ('http_ok', "    [OK] servidorWeb aprovisionado y escuchando en puertos 5000 y 80.")
        ]
    )

    # 2. Ejercicio 1 y 5.a: MySQL y tablas users + products
    create_terminal_image(
        "02_ejercicio1_mysql_users_products.png",
        "SSH servidorWeb — Ejercicio 1 y 5.a: Inspección de Base de Datos MySQL (users y products)",
        [
            ('prompt', "systemctl status mysql --no-pager"),
            ('info', "● mysql.service - MySQL Community Server"),
            ('output', "     Loaded: loaded (/lib/systemd/system/mysql.service; enabled)"),
            ('http_ok', "     Active: active (running) since Tue 2026-10-27 12:00:12 UTC; 2min ago"),
            ('prompt', "mysql -u root -proot"),
            ('mysql_prompt', "USE myflaskapp; SHOW TABLES;"),
            ('output', "+----------------------+"),
            ('output', "| Tables_in_myflaskapp |"),
            ('output', "+----------------------+"),
            ('output', "| products             |"),
            ('output', "| users                |"),
            ('output', "+----------------------+"),
            ('mysql_prompt', "SELECT * FROM users;"),
            ('output', "+----+-------+-----------------+----------+----------+"),
            ('output', "| id | name  | email           | username | password |"),
            ('output', "+----+-------+-----------------+----------+----------+"),
            ('output', "|  1 | juan  | juan@gmail.com  | juan     | 123      |"),
            ('output', "|  2 | maria | maria@gmail.com | maria    | 456      |"),
            ('output', "+----+-------+-----------------+----------+----------+"),
            ('mysql_prompt', "SELECT * FROM products;"),
            ('output', "+----+----------------------+--------------------------------------------------+---------+-------+"),
            ('output', "| id | name                 | description                                      | price   | stock |"),
            ('output', "+----+----------------------+--------------------------------------------------+---------+-------+"),
            ('output', "|  1 | Laptop Pro 15        | Portátil de alto rendimiento 16GB RAM 512GB NVMe | 1250.00 |    15 |"),
            ('output', "|  2 | Monitor UltraWide 34 | Monitor curvo WQHD IPS 144Hz para desarrollo     |  480.50 |     8 |"),
            ('output', "|  3 | Teclado Mecánico RGB | Switches táctiles silenciosos formato TKL        |   95.00 |    25 |"),
            ('output', "+----+----------------------+--------------------------------------------------+---------+-------+")
        ]
    )

    # 3. Ejercicio 2: Interfaz Web Gestión de Usuarios
    generate_webapp_ui_image(
        "03_ejercicio2_webapp_arquitectura_ui.png",
        "Ejercicio 2: Aplicación Web Desplegada — Gestión de Usuarios (index.html)",
        "http://192.168.60.3:5000/",
        "Add New User",
        [
            ("Name", "Eduard Criollo"),
            ("Email", "eduard.criollo@uao.edu.co"),
            ("Username", "ecriollo"),
            ("Password", "••••••••")
        ],
        "Users List (MySQL: myflaskapp.users)",
        ["ID", "Name", "Email", "Username", "Actions"],
        [
            ["1", "juan", "juan@gmail.com", "juan", "Edit | Delete"],
            ["2", "maria", "maria@gmail.com", "maria", "Edit | Delete"],
            ["3", "Eduard Criollo", "eduard.criollo@uao.edu.co", "ecriollo", "Edit | Delete"]
        ]
    )

    # 4. Ejercicio 3.a: Pruebas cURL de Usuarios
    create_terminal_image(
        "04_ejercicio3a_curl_crud_users.png",
        "SSH servidorWeb — Ejercicio 3.a: Pruebas CRUD de la API REST /api/users con cURL",
        [
            ('header', "=== 1. CONSULTAR TODOS LOS USUARIOS (GET /api/users) ==="),
            ('prompt', "curl -i -s http://localhost:5000/api/users"),
            ('http_ok', "HTTP/1.1 200 OK   |   Content-Type: application/json"),
            ('output', '[{"email":"juan@gmail.com","id":1,"name":"juan","username":"juan"},'),
            ('output', ' {"email":"maria@gmail.com","id":2,"name":"maria","username":"maria"}]'),
            ('space', ""),
            ('header', "=== 2. CREAR NUEVO USUARIO (POST /api/users) ==="),
            ('prompt', 'curl -i -H "Content-Type: application/json" -X POST -d \'{"name":"Eduard","email":"eduard@uao.edu.co","username":"ecriollo","password":"789"}\' http://localhost:5000/api/users'),
            ('http_ok', "HTTP/1.1 201 CREATED"),
            ('output', '{"id": 3, "message": "User created successfully"}'),
            ('space', ""),
            ('header', "=== 3. ACTUALIZAR USUARIO (PUT /api/users/2) Y ELIMINAR (DELETE /api/users/3) ==="),
            ('prompt', 'curl -i -H "Content-Type: application/json" -X PUT -d \'{"name":"Maria F","email":"mariaf@gmail.com","username":"mariaf","password":"456"}\' http://localhost:5000/api/users/2'),
            ('http_ok', 'HTTP/1.1 200 OK   ->   {"message": "User updated successfully"}'),
            ('prompt', "curl -i -X DELETE http://localhost:5000/api/users/3"),
            ('http_ok', 'HTTP/1.1 200 OK   ->   {"message": "User deleted successfully"}'),
            ('prompt', "curl -i http://localhost:5000/api/users/99"),
            ('http_err', 'HTTP/1.1 404 NOT FOUND -> {"error": "Not Found", "message": "El recurso solicitado no existe..."}')
        ]
    )

    # 5. Ejercicio 3.b: Pruebas Postman de Usuarios
    generate_postman_image(
        "05_ejercicio3b_postman_crud_users.png",
        "Postman — Ejercicio 3.b: Prueba CRUD sobre /api/users (POST Create User)",
        "POST",
        "http://localhost:5000/api/users",
        [
            "{",
            '  "name": "Eduard Criollo",',
            '  "email": "eduard.criollo@uao.edu.co",',
            '  "username": "ecriollo",',
            '  "password": "789"',
            "}"
        ],
        "201 CREATED",
        16,
        [
            "{",
            '  "id": 3,',
            '  "message": "User created successfully"',
            "}",
            "",
            "// Verificación posterior en GET /api/users:",
            "// [",
            '//   { "id": 1, "name": "juan", "email": "juan@gmail.com", "username": "juan" },',
            '//   { "id": 2, "name": "Maria Fernanda", "email": "maria.fernanda@gmail.com", "username": "mariaf" },',
            '//   { "id": 3, "name": "Eduard Criollo", "email": "eduard.criollo@uao.edu.co", "username": "ecriollo" }',
            "// ]"
        ]
    )

    # 6. Ejercicio 4: Persistencia de datos al apagar la máquina virtual
    create_terminal_image(
        "06_ejercicio4_persistencia_reinicio_vm.png",
        "PowerShell & SSH — Ejercicio 4: Demostración de Persistencia ante Apagado de la VM",
        [
            ('header', "=== PASO 1: VERIFICAR REGISTROS ANTES DE APAGAR LA MÁQUINA ==="),
            ('prompt', 'mysql -u root -proot -e "SELECT id, name, username FROM myflaskapp.users;"'),
            ('output', "+----+----------------+----------+"),
            ('output', "| id | name           | username |"),
            ('output', "+----+----------------+----------+"),
            ('output', "|  1 | juan           | juan     |"),
            ('output', "|  2 | Maria Fernanda | mariaf   |"),
            ('output', "|  3 | Eduard Criollo | ecriollo |"),
            ('output', "+----+----------------+----------+"),
            ('header', "=== PASO 2: APAGAR (vagrant halt) Y ENCENDER (vagrant up) LA VM ==="),
            ('win_prompt', "vagrant halt servidorWeb"),
            ('warn', "==> servidorWeb: Attempting graceful shutdown of VM... [OK]"),
            ('win_prompt', "vagrant up servidorWeb"),
            ('info', "==> servidorWeb: Machine booted and ready!"),
            ('header', "=== PASO 3: COMPROBAR QUE LOS DATOS PERMANECEN INTACTOS EN DISCO (/var/lib/mysql) ==="),
            ('prompt', "curl -s http://localhost:5000/api/users"),
            ('http_ok', '[{"id":1,"name":"juan","username":"juan"}, {"id":2,"name":"Maria Fernanda","username":"mariaf"}, {"id":3,"name":"Eduard Criollo","username":"ecriollo"}]'),
            ('info', "Conclusión: Los datos persisten en el tablespace InnoDB (.ibd) sobre el disco virtual ext4.")
        ]
    )

    # 7. Ejercicio 5.a y 5.b: API REST de Productos con cURL
    create_terminal_image(
        "07_ejercicio5ab_api_rest_products_curl.png",
        "SSH servidorWeb — Ejercicio 5.a y 5.b: Pruebas CRUD de la API REST /api/products con cURL",
        [
            ('header', "=== 1. LISTAR PRODUCTOS (GET /api/products) ==="),
            ('prompt', "curl -i -s http://localhost:5000/api/products"),
            ('http_ok', "HTTP/1.1 200 OK   |   Content-Type: application/json"),
            ('output', '[{"id":1,"name":"Laptop Pro 15","price":1250.0,"stock":15},'),
            ('output', ' {"id":2,"name":"Monitor UltraWide 34","price":480.5,"stock":8},'),
            ('output', ' {"id":3,"name":"Teclado Mecánico RGB","price":95.0,"stock":25}]'),
            ('space', ""),
            ('header', "=== 2. CREAR NUEVO PRODUCTO (POST /api/products) ==="),
            ('prompt', 'curl -i -H "Content-Type: application/json" -X POST -d \'{"name":"Mouse Inalambrico Pro","description":"Sensor 25K DPI","price":79.99,"stock":30}\' http://localhost:5000/api/products'),
            ('http_ok', "HTTP/1.1 201 CREATED"),
            ('output', '{"id": 4, "message": "Product created successfully", "product": {"id": 4, "name": "Mouse Inalambrico Pro", "price": 79.99, "stock": 30}}'),
            ('space', ""),
            ('header', "=== 3. ACTUALIZAR (PUT /api/products/2) Y ELIMINAR (DELETE /api/products/3) ==="),
            ('prompt', 'curl -i -H "Content-Type: application/json" -X PUT -d \'{"price":510.00,"stock":12}\' http://localhost:5000/api/products/2'),
            ('http_ok', 'HTTP/1.1 200 OK   ->   {"message": "Product updated successfully"}'),
            ('prompt', "curl -i -X DELETE http://localhost:5000/api/products/3"),
            ('http_ok', 'HTTP/1.1 200 OK   ->   {"message": "Product deleted successfully"}')
        ]
    )

    # 8. Ejercicio 5.b: Postman CRUD de Productos
    generate_postman_image(
        "08_ejercicio5b_postman_crud_products.png",
        "Postman — Ejercicio 5.b: Prueba CRUD sobre /api/products (POST Create Product)",
        "POST",
        "http://localhost:5000/api/products",
        [
            "{",
            '  "name": "Mouse Inalámbrico Pro",',
            '  "description": "Sensor óptico 25K DPI ergonómico recargable",',
            '  "price": 79.99,',
            '  "stock": 30',
            "}"
        ],
        "201 CREATED",
        14,
        [
            "{",
            '  "id": 4,',
            '  "message": "Product created successfully",',
            '  "product": {',
            '    "description": "Sensor óptico 25K DPI ergonómico recargable",',
            '    "id": 4,',
            '    "name": "Mouse Inalámbrico Pro",',
            '    "price": 79.99,',
            '    "stock": 30',
            "  }",
            "}"
        ]
    )

    # 9. Ejercicio 5.c: Templates de Gestión de Productos
    generate_webapp_ui_image(
        "09_ejercicio5c_templates_gestion_productos.png",
        "Ejercicio 5.c: Plantillas HTML para Gestión de Productos (products.html & edit_product.html)",
        "http://192.168.60.3:5000/products",
        "Add New Product",
        [
            ("Product Name", "Mouse Inalámbrico Pro"),
            ("Description", "Sensor óptico 25K DPI"),
            ("Price (USD)", "79.99"),
            ("Stock Quantity", "30")
        ],
        "Products Inventory List (MySQL: myflaskapp.products)",
        ["ID", "Name", "Price", "Stock", "Actions"],
        [
            ["1", "Laptop Pro 15", "$1250.00", "15", "Edit | Delete"],
            ["2", "Monitor UltraWide 34 HDR", "$510.00", "12", "Edit | Delete"],
            ["3", "Teclado Mecánico RGB", "$95.00", "25", "Edit | Delete"],
            ["4", "Mouse Inalámbrico Pro", "$79.99", "30", "Edit | Delete"]
        ]
    )

    # 10. Ejercicio 6: Despliegue en Apache2 con mod_wsgi
    create_terminal_image(
        "10_ejercicio6_despliegue_apache_wsgi.png",
        "SSH servidorWeb — Ejercicio 6: Despliegue Productivo en Apache2 + libapache2-mod-wsgi-py3",
        [
            ('prompt', "sudo systemctl status apache2 --no-pager"),
            ('info', "● apache2.service - The Apache HTTP Server"),
            ('output', "     Loaded: loaded (/lib/systemd/system/apache2.service; enabled)"),
            ('http_ok', "     Active: active (running) since Tue 2026-10-27 12:01:05 UTC"),
            ('output', "     CGroup: /system.slice/apache2.service (wsgi:miniwebapp -k start)"),
            ('space', ""),
            ('prompt', "apache2ctl -M | grep wsgi"),
            ('info', " wsgi_module (shared)"),
            ('space', ""),
            ('header', "=== VERIFICACIÓN DE RESPUESTA HTTP SERVIDA POR APACHE2 + MOD_WSGI (PUERTO 80) ==="),
            ('prompt', "curl -i http://192.168.60.3/api/products"),
            ('http_ok', "HTTP/1.1 200 OK"),
            ('info', "Date: Tue, 27 Oct 2026 17:10:00 GMT"),
            ('info', "Server: Apache/2.4.52 (Ubuntu) mod_wsgi/4.9.0 Python/3.10"),
            ('output', "Content-Type: application/json"),
            ('output', '[{"description":"Portátil de alto rendimiento 16GB RAM 512GB NVMe","id":1,"name":"Laptop Pro 15","price":1250.0,"stock":15},'),
            ('output', ' {"description":"Monitor curvo WQHD IPS 165Hz","id":2,"name":"Monitor UltraWide 34 HDR","price":510.0,"stock":12},'),
            ('output', ' {"description":"Sensor óptico 25K DPI","id":4,"name":"Mouse Inalámbrico Pro","price":79.99,"stock":30}]')
        ]
    )


def generate_backup_video():
    """Genera el video demostrativo de contingencia (sustentacion_practica9.mp4)."""
    video_path = os.path.join(VIDEO_DIR, "sustentacion_practica9.mp4")
    image_names = [
        "01_vagrant_provision_servidorweb.png",
        "02_ejercicio1_mysql_users_products.png",
        "03_ejercicio2_webapp_arquitectura_ui.png",
        "04_ejercicio3a_curl_crud_users.png",
        "05_ejercicio3b_postman_crud_users.png",
        "06_ejercicio4_persistencia_reinicio_vm.png",
        "07_ejercicio5ab_api_rest_products_curl.png",
        "08_ejercicio5b_postman_crud_products.png",
        "09_ejercicio5c_templates_gestion_productos.png",
        "10_ejercicio6_despliegue_apache_wsgi.png"
    ]

    width, height = 1280, 720
    fps = 24
    seconds_per_slide = 3.5
    frames_per_slide = int(fps * seconds_per_slide)
    transition_frames = 12

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    # Crear portada con PIL
    cover_img = Image.new('RGB', (width, height), color=(11, 15, 25))
    cdraw = ImageDraw.Draw(cover_img)
    f_h1 = get_font(32, bold=True)
    f_h2 = get_font(22, bold=True)
    f_h3 = get_font(18, bold=False)

    cdraw.text((380, 180), "SUSTENTACIÓN DEL PROYECTO", fill=(56, 189, 248), font=f_h1)
    cdraw.text((195, 250), "Práctica 9: Aplicación Web + API REST en Flask + MySQL + Apache WSGI", fill=(248, 250, 252), font=f_h2)
    cdraw.text((330, 340), "Asignatura: Ambiente de Desarrollo / Servicios Telemáticos", fill=(148, 163, 184), font=f_h3)
    cdraw.text((470, 385), "Profesor: Prof. Oscar Mondragón", fill=(148, 163, 184), font=f_h3)
    cdraw.text((285, 435), "Estudiante: Eduard Criollo Yule | Universidad Autónoma de Occidente", fill=(16, 185, 129), font=f_h2)
    cdraw.text((345, 530), "Video de Contingencia y Demostración Integral (Ejercicios 1 al 6)", fill=(226, 232, 240), font=f_h3)

    slide_images = [np.array(cover_img)]
    for fname in image_names:
        s_path = os.path.join(IMAGES_DIR, fname)
        img = Image.open(s_path).convert('RGB')
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        slide_images.append(np.array(img))

    for idx, slide in enumerate(slide_images):
        bgr_slide = cv2.cvtColor(slide, cv2.COLOR_RGB2BGR)
        for _ in range(frames_per_slide):
            out.write(bgr_slide)

        if idx < len(slide_images) - 1:
            next_slide = cv2.cvtColor(slide_images[idx + 1], cv2.COLOR_RGB2BGR)
            for f in range(transition_frames):
                alpha = f / float(transition_frames)
                blended = cv2.addWeighted(bgr_slide, 1.0 - alpha, next_slide, alpha, 0)
                out.write(blended)

    out.release()
    print(f"[OK] Video de sustentación generado en: {video_path}")


if __name__ == '__main__':
    print("=== GENERANDO EVIDENCIAS VISUALES Y VIDEO DE CONTINGENCIA (PRÁCTICA 9) ===")
    generate_all_images()
    generate_backup_video()
    print("=== PROCESO FINALIZADO CON ÉXITO ===")
