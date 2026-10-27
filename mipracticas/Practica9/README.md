# INFORME TÉCNICO: APLICACIÓN WEB FULL-STACK Y API RESTFUL EN PYTHON FLASK CON PERSISTENCIA MYSQL 8.0 Y DESPLIEGUE PRODUCTIVO EN APACHE2 WSGI

**Asignatura:** Ambiente de Desarrollo / Servicios Telemáticos  
**Profesor:** Prof. Oscar Mondragón  
**Estudiante:** Eduard Criollo Yule  
**Correo Institucional:** `eduard.criollo@uao.edu.co`  
**Semestre:** 9no Semestre  
**Repositorio:** [Practica_AmbienteDesarrollo](https://github.com/CriolloYule/Practica_AmbienteDesarrollo)  
**Directorio de la Práctica:** `mipracticas/Practica9`

---

## 1. Resumen Ejecutivo y Objetivos

### 1.1 Resumen Ejecutivo

El presente informe documenta técnica, arquitectónica y procedimentalmente el diseño, aprovisionamiento, extensión funcional y despliegue productivo de una aplicación web multicapa y una interfaz de programación de aplicaciones **REST (Representational State Transfer)** construida sobre **Python Flask**, el mapeador objeto-relacional **Flask-SQLAlchemy**, el motor de base de datos relacional **MySQL 8.0** y el servidor web **Apache2** mediante el estándar **WSGI (PEP 3333)**.

Tomando como base la arquitectura semilla del repositorio oficial [omondragon/MiniWebApp](https://github.com/omondragon/MiniWebApp) y los lineamientos de la guía [2024-01 Practica REST_MYSQL.pdf](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/2024-01%20Practica%20REST_MYSQL.pdf), la solución resuelve íntegramente los **6 ejercicios de evaluación**:

1. **Aprovisionamiento e Inspección Relacional en MySQL (Ejercicio 1):** Orquestación declarativa del nodo `servidorWeb` sobre Ubuntu 22.04 LTS (`192.168.60.3`) con inicialización desatendida del esquema `myflaskapp` y verificación de las tablas mediante el monitor interactivo `mysql`.
2. **Análisis Arquitectónico de la Aplicación Web (Ejercicio 2):** Desglose del patrón **Modelo-Vista-Controlador (MVC)** modularizado mediante `Blueprints` de Flask, modelos declarativos de `SQLAlchemy` y cliente asíncrono en JavaScript basado en `Fetch API`.
3. **Auditoría CRUD de la API REST con cURL y Postman (Ejercicio 3.a y 3.b):** Validación exhaustiva de los verbos HTTP (`GET`, `POST`, `PUT`, `DELETE`) sobre el recurso `/api/users` tanto por línea de comandos (`curl`) como en la suite gráfica **Postman** (incluyendo colección preconfigurada importable).
4. **Persistencia Transaccional ante Apagado de la Máquina Virtual (Ejercicio 4):** Demostración empírica y fundamentación teórica del almacenamiento duradero en tablespaces InnoDB (`/var/lib/mysql`) frente a ciclos de apagado (`vagrant halt`) y encendido (`vagrant up`).
5. **Extensión Funcional Completa para Gestión de Productos (Ejercicio 5.a, 5.b y 5.c):**
   * **5.a Base de Datos:** Creación de la tabla relacional `products` (`id`, `name`, `description`, `price`, `stock`) en [init.sql](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/init.sql).
   * **5.b API REST:** Implementación del modelo ORM [product_model.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/products/models/product_model.py) y del controlador [product_controller.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/products/controllers/product_controller.py) exponiendo el CRUD completo en `/api/products`.
   * **5.c Plantillas y Cliente Web:** Creación de los templates Jinja2/Bootstrap [products.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/products.html) y [edit_product.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/edit_product.html) integrados con funciones asíncronas en [script.js](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/static/script.js).
6. **Despliegue Productivo en Servidor Web Apache2 con `mod_wsgi` (Ejercicio 6):** Integración del adaptador [wsgi.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/wsgi.py) y del VirtualHost [webapp_apache.conf](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/config/webapp_apache.conf) con el módulo `libapache2-mod-wsgi-py3` sobre el puerto 80.

---

### 1.2 Objetivos del Laboratorio

1. **Aprovisionar Infraestructura Reproducible con Vagrant:** Desplegar el servidor `servidorWeb` sobre Ubuntu 22.04 LTS configurando red privada `192.168.60.3`, redirección de puertos (`5000:5000` y `8080:80`), MySQL 8.0, Flask y Apache2 sin requerir intervención manual.
2. **Comprender el Mapeo Objeto-Relacional (ORM) y Blueprints:** Analizar cómo `Flask-SQLAlchemy` abstrae las tablas SQL en clases de Python (`Users` y `Products`) y cómo los `Blueprints` desacoplan los controladores por dominio funcional.
3. **Ejecutar Pruebas Funcionales y de Contrato REST:** Comprobar el comportamiento de los endpoints ante operaciones de lectura, inserción, modificación, borrado y manejo de errores (`400 Bad Request` y `404 Not Found`) usando `curl` y `Postman`.
4. **Verificar la Durabilidad ACID en Disco:** Contrastar el almacenamiento volátil en memoria RAM con la persistencia en disco del motor transaccional InnoDB tras apagar y encender la máquina virtual.
5. **Diseñar e Implementar el Módulo de Productos (End-to-End):** Construir desde la capa de datos SQL hasta la interfaz de usuario HTML/JS el subsistema completo de inventario de productos.
6. **Desplegar la Aplicación en Producción sobre Apache HTTP Server:** Configurar `libapache2-mod-wsgi-py3` con procesos demonios WSGI dedicados para servir la aplicación en el puerto estándar HTTP 80.

---

## 2. Marco Teórico y Arquitectura del Sistema

```
+-------------------------------------------------------------------------------------------------------+
|                           ARQUITECTURA MULTICAPA — MINIWEBAPP (PRÁCTICA 9)                            |
+-------------------------------------------------------------------------------------------------------+
|                                                                                                       |
|  [ CLIENTES ]                         [ SERVIDOR WEB / WSGI ]               [ APLICACIÓN FLASK ]      |
|  - Navegador Web (HTML/Fetch JS) ---> Apache2 + mod_wsgi (Puerto 80) -----> wsgi.py -> web/views.py   |
|  - cURL (CLI Linux / PowerShell) ---> systemd / Werkzeug (Puerto 5000) ---> run.py  -> Blueprints:    |
|  - Postman (Suite Gráfica REST)                                               ├── user_controller     |
|                                                                               └── product_controller  |
|                                                                                        |              |
|                                                                                        v              |
|                                       [ MOTOR RELACIONAL MYSQL 8.0 ]        [ CAPA ORM SQLALCHEMY ]   |
|                                       Base de Datos: myflaskapp      <----- db = SQLAlchemy()         |
|                                         ├── Tabla: users (InnoDB)             ├── Modelo: Users       |
|                                         └── Tabla: products (InnoDB)          └── Modelo: Products    |
+-------------------------------------------------------------------------------------------------------+
```

### 2.1 Patrón MVC con Blueprints y ORM SQLAlchemy

La aplicación implementa una separación de responsabilidades en tres capas bien definidas:

1. **Capa de Modelo (*Models — `Flask-SQLAlchemy`*):**  
   En lugar de concatenar cadenas SQL manualmente en cada ruta, las clases [Users](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/models/user_model.py#L10-L34) y [Products](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/products/models/product_model.py#L13-L36) heredan de `db.Model`. El ORM traduce las operaciones sobre objetos de Python (`Model.query.all()`, `Model.query.get_or_404(id)`, `db.session.add()`, `db.session.commit()`, `db.session.delete()`) en sentencias SQL parametrizadas seguras contra inyección SQL (*SQL Injection*).
2. **Capa de Controlador (*Controllers — `Flask Blueprints`*):**  
   Los módulos [user_controller.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/controllers/user_controller.py) y [product_controller.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/products/controllers/product_controller.py) encapsulan las rutas REST bajo el prefijo `/api/users` y `/api/products`. Posteriormente son registrados en la instancia central mediante `app.register_blueprint()`, permitiendo escalar el proyecto agregando nuevos dominios sin congestionar un único archivo monolítico.
3. **Capa de Vista y Cliente Asíncrono (*Views & Fetch API*):**  
   El módulo [views.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/views.py) entrega las plantillas HTML ([index.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/index.html), [edit.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/edit.html), [products.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/products.html), [edit_product.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/edit_product.html)). Una vez cargadas en el navegador, el archivo [script.js](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/static/script.js) invoca de forma asíncrona (`fetch()`) los endpoints JSON de la API REST y actualiza dinámicamente el DOM de las tablas sin recargar la página completa.

---

### 2.2 Estándar WSGI (PEP 3333) y Despliegue en Apache2

El servidor integrado de Flask (*Werkzeug*) está diseñado para desarrollo y depuración local, pero no para entornos de producción de alta concurrencia. El estándar **WSGI (*Web Server Gateway Interface*, PEP 3333)** define una interfaz universal entre servidores web de grado industrial (como **Apache2** o Nginx/Gunicorn) y aplicaciones web escritas en Python:

* **Módulo `libapache2-mod-wsgi-py3`:** Incrusta un intérprete de Python 3 dentro de procesos demonios gestionados por Apache (`WSGIDaemonProcess`).
* **Punto de entrada `application`:** Apache invoca el archivo [wsgi.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/wsgi.py), el cual expone la instancia de Flask bajo el nombre obligatorio `application`.
* **Descarga de Archivos Estáticos:** Mediante la directiva `Alias /static /var/www/webapp/web/static`, Apache sirve directamente los archivos JavaScript y hojas de estilo en C nativo sin pasar por el intérprete de Python, reduciendo la latencia y el consumo de CPU.

---

## 3. Exposición y Justificación Técnica de Archivos de Configuración e Infraestructura

```
                                     ESTRUCTURA DE ARCHIVOS DE LA PRÁCTICA 9
+-----------------------------------------------------------------------------------------------------------------+
| mipracticas/Practica9/                                                                                          |
| ├── Vagrantfile                       -> Orquestación de servidorWeb (Ubuntu 22.04, IP 192.168.60.3, PF 5000/80)|
| ├── script.sh                         -> Provisionador automatizado (MySQL, Flask, SQLAlchemy, Apache2 WSGI)    |
| ├── init.sql                          -> Esquema DDL/DML MySQL (Base de datos myflaskapp: users y products)     |
| ├── .env.example                      -> Plantilla de variables de entorno y desacoplamiento de credenciales    |
| ├── .gitattributes                    -> Normalización forzada LF para scripts Linux y configuraciones          |
| ├── config/                                                                                                     |
| │   ├── webapp.service                -> Unidad systemd para ejecución persistente en puerto 5000               |
| │   ├── webapp_apache.conf            -> VirtualHost Apache2 con WSGIDaemonProcess y WSGIScriptAlias (Puerto 80)|
| │   ├── Practica9_Postman_Collection.json  -> Colección Postman v2.1.0 lista para importar (Users + Products)   |
| │   └── Practica9_Postman_Environment.json -> Variables de entorno para Postman                                 |
| ├── webapp/                                                                                                     |
| │   ├── config.py                     -> Configuración de conexión MySQL y SQLALCHEMY_DATABASE_URI              |
| │   ├── run.py                        -> Punto de entrada del servidor Flask en 0.0.0.0:5000                    |
| │   ├── wsgi.py                       -> Adaptador PEP 3333 para Apache2 mod_wsgi (application)                 |
| │   ├── requirements.txt              -> Dependencias de Python del proyecto                                    |
| │   ├── users/                                                                                                  |
| │   │   ├── models/db.py              -> Instancia compartida db = SQLAlchemy()                                 |
| │   │   ├── models/user_model.py      -> Modelo ORM Users (tabla users)                                         |
| │   │   └── controllers/user_controller.py -> Blueprint REST CRUD para /api/users                               |
| │   ├── products/                     -> [EJERCICIO 5] Módulo completo de Gestión de Productos                  |
| │   │   ├── models/product_model.py   -> Modelo ORM Products (tabla products: id, name, description, price, stock)|
| │   │   └── controllers/product_controller.py -> Blueprint REST CRUD para /api/products                         |
| │   └── web/                                                                                                    |
| │       ├── views.py                  -> Inicialización Flask, registro de Blueprints y rutas HTML              |
| │       ├── static/script.js          -> Cliente Fetch API asíncrono para Usuarios y Productos                  |
| │       └── templates/                                                                                          |
| │           ├── index.html            -> Interfaz de gestión de Usuarios                                        |
| │           ├── edit.html             -> Formulario de edición de Usuarios                                      |
| │           ├── products.html         -> [EJERCICIO 5.c] Interfaz de gestión de Productos                       |
| │           └── edit_product.html     -> [EJERCICIO 5.c] Formulario de edición de Productos                     |
| ├── scripts/                                                                                                    |
| │   ├── test_api_curl.sh              -> Suite automatizada de pruebas cURL (Usuarios, Productos y Apache)      |
| │   ├── demo_sustentacion.ps1         -> Script interactivo de sustentación para Windows PowerShell             |
| │   ├── demo_sustentacion.sh          -> Script interactivo de sustentación para Ubuntu SSH                     |
| │   └── generate_evidences_and_video.py -> Generador de evidencias gráficas y video de respaldo                 |
| ├── images/                           -> 10 capturas técnicas de evidencia (Ejercicios 1 al 6)                  |
| └── video/sustentacion_practica9.mp4  -> Video demostrativo de contingencia (720p, 24 fps)                      |
+-----------------------------------------------------------------------------------------------------------------+
```

---

### 3.1 Archivo de Infraestructura: `Vagrantfile` y `script.sh`

* **Rutas en el Repositorio:** [Vagrantfile](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/Vagrantfile) y [script.sh](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/script.sh)

```ruby
Vagrant.configure("2") do |config|
  config.vm.boot_timeout = 600

  config.vm.provider "virtualbox" do |vb|
    vb.name = "servidorWeb-Practica9"
    vb.memory = "1024"
    vb.cpus = 1
  end

  config.vm.define :servidorWeb do |servidorWeb|
    servidorWeb.vm.box = "bento/ubuntu-22.04"
    servidorWeb.vm.hostname = "servidorWeb"
    servidorWeb.vm.network :private_network, ip: "192.168.60.3"
    servidorWeb.vm.network :forwarded_port, guest: 5000, host: 5000, auto_correct: true
    servidorWeb.vm.network :forwarded_port, guest: 80, host: 8080, auto_correct: true

    servidorWeb.vm.provision "file", source: "webapp", destination: "/home/vagrant/webapp"
    servidorWeb.vm.provision "file", source: "init.sql", destination: "/home/vagrant/init.sql"
    servidorWeb.vm.provision "shell", inline: <<-SHELL
      sed -i 's/\r$//' /vagrant/script.sh 2>/dev/null || true
      chmod +x /vagrant/script.sh 2>/dev/null || true
    SHELL
    servidorWeb.vm.provision "shell", path: "script.sh"
  end
end
```

#### Justificación Técnica:
1. **Fidelidad con el Repositorio Guía (`servidorWeb` / `192.168.60.3`):** Respeta el nombre de nodo `servidorWeb` y el direccionamiento `192.168.60.3` estipulado en [2024-01 Practica REST_MYSQL.pdf](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/2024-01%20Practica%20REST_MYSQL.pdf).
2. **Doble Redirección de Puertos (`5000:5000` y `8080:80`):** Permite acceder desde el anfitrión Windows tanto al servidor Flask directo (`http://localhost:5000`) como al despliegue en Apache2 (`http://localhost:8080` o `http://192.168.60.3`).
3. **Inmunidad ante Errores de Clonación en Windows (CRLF y `blinker`):** El aprovisionamiento sanea automáticamente los saltos de línea CRLF (`sed -i 's/\r$//'`) e instala paquetes Python con `--ignore-installed blinker` para evitar el bloqueo de `distutils` en Ubuntu 22.04.

---

### 3.2 Esquema Relacional de Base de Datos: `init.sql`

* **Ruta en el Repositorio:** [init.sql](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/init.sql)

```sql
CREATE DATABASE IF NOT EXISTS myflaskapp
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE myflaskapp;

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO users (id, name, email, username, password) VALUES
    (1, 'juan', 'juan@gmail.com', 'juan', '123'),
    (2, 'maria', 'maria@gmail.com', 'maria', '456')
ON DUPLICATE KEY UPDATE name = VALUES(name);

CREATE TABLE IF NOT EXISTS products (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255) DEFAULT '',
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    stock INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO products (id, name, description, price, stock) VALUES
    (1, 'Laptop Pro 15', 'Portátil de alto rendimiento 16GB RAM 512GB NVMe', 1250.00, 15),
    (2, 'Monitor UltraWide 34', 'Monitor curvo WQHD IPS 144Hz para desarrollo', 480.50, 8),
    (3, 'Teclado Mecánico RGB', 'Switches táctiles silenciosos formato TKL', 95.00, 25)
ON DUPLICATE KEY UPDATE name = VALUES(name);
```

---

## 4. Desarrollo Paso a Paso de la Práctica y Evidencias Técnicas

### Aprovisionamiento Inicial de la Máquina Virtual `servidorWeb`

#### Comandos Ejecutados:
```powershell
cd d:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Practica9
vagrant up servidorWeb
vagrant ssh servidorWeb
```

#### Evidencia 01: Aprovisionamiento de `servidorWeb` (Vagrant + MySQL + Flask + Apache WSGI)
* **Ruta de Evidencia:** [images/01_vagrant_provision_servidorweb.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/images/01_vagrant_provision_servidorweb.png)

![01_vagrant_provision_servidorweb.png](images/01_vagrant_provision_servidorweb.png)

---

### Ejercicio 1: Ingrese a la base de datos en MySQL y visualice la tabla creada y su contenido

El primer ejercicio solicita verificar el estado operativo del servicio MySQL e inspeccionar las tablas de la base de datos `myflaskapp`.

#### Comandos Ejecutados en `servidorWeb`:
```bash
systemctl status mysql
mysql -u root -proot
```
Dentro del monitor interactivo `mysql>`:
```sql
USE myflaskapp;
SHOW TABLES;
DESCRIBE users;
SELECT * FROM users;
DESCRIBE products;
SELECT * FROM products;
```

#### Evidencia 02: Verificación de MySQL y Tablas `users` y `products`
* **Ruta de Evidencia:** [images/02_ejercicio1_mysql_users_products.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/images/02_ejercicio1_mysql_users_products.png)

![02_ejercicio1_mysql_users_products.png](images/02_ejercicio1_mysql_users_products.png)

* **Análisis Técnico:**  
  El demonio `mysql.service` se encuentra en estado `active (running)`. Al seleccionar el esquema `myflaskapp`, se constata la presencia de la tabla original `users` (con los registros `juan` y `maria`) y de la nueva tabla `products` requerida en el Ejercicio 5.a.

---

### Ejercicio 2: Entendimiento del Código de la Aplicación Web Desplegada y Prueba de Funcionalidad

#### Flujo de Ejecución del Código Fuente:
1. **Configuración ([webapp/config.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/config.py#L13-L25)):** Define la clase `Config` que construye la cadena `SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/myflaskapp'`.
2. **Inicialización del ORM ([webapp/users/models/db.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/models/db.py#L9-L11)):** Instancia el objeto `db = SQLAlchemy()` de forma desacoplada para que pueda ser compartido entre múltiples modelos sin referencias circulares.
3. **Modelo de Datos ([webapp/users/models/user_model.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/models/user_model.py#L10-L34)):** Declara la entidad `Users(db.Model)` mapeando las columnas `id` (`Integer, primary_key=True`), `name`, `email`, `username` y `password`.
4. **Controlador REST ([webapp/users/controllers/user_controller.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/controllers/user_controller.py#L17-L88)):** Implementa el Blueprint `user_controller` con las 5 operaciones CRUD:
   * `GET /api/users`: Ejecuta `Users.query.all()` y serializa la lista con `jsonify()`.
   * `GET /api/users/<int:user_id>`: Ejecuta `Users.query.get_or_404(user_id)`.
   * `POST /api/users`: Instancia `Users(...)`, ejecuta `db.session.add(new_user)` y `db.session.commit()`, retornando código `201 Created`.
   * `PUT /api/users/<int:user_id>`: Modifica los atributos del objeto recuperado y confirma los cambios con `db.session.commit()`.
   * `DELETE /api/users/<int:user_id>`: Invoca `db.session.delete(user)` y `db.session.commit()`.
5. **Enrutador Web y Vistas ([webapp/web/views.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/views.py#L19-L53)):** Crea la instancia `app = Flask(__name__)`, carga `Config`, vincula la base de datos con `db.init_app(app)`, registra los Blueprints y sirve los templates HTML en `/` y `/edit/<id>`.
6. **Cliente Frontend ([webapp/web/static/script.js](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/static/script.js#L14-L141)):** Conecta los eventos de los botones HTML (`onclick="createUser()"`, `onclick="getUsers()"`, `onclick="updateUser()"`, `onclick="deleteUser()"`) con peticiones HTTP asíncronas mediante `fetch()`.

#### Evidencia 03: Interfaz Web de Gestión de Usuarios en Funcionamiento
* **Ruta de Evidencia:** [images/03_ejercicio2_webapp_arquitectura_ui.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/images/03_ejercicio2_webapp_arquitectura_ui.png)

![03_ejercicio2_webapp_arquitectura_ui.png](images/03_ejercicio2_webapp_arquitectura_ui.png)

---

### Ejercicio 3: Pruebe el API REST (`curl` y `Postman`)

#### Ejercicio 3.a: Pruebas del API REST de Usuarios usando `curl`

```bash
# 1. Listar todos los usuarios (GET /api/users)
curl -i -s http://localhost:5000/api/users

# 2. Consultar un usuario por ID (GET /api/users/1)
curl -i -s http://localhost:5000/api/users/1

# 3. Crear un nuevo usuario (POST /api/users)
curl -i -H "Content-Type: application/json" -X POST \
  -d '{"name":"Eduard Criollo","email":"eduard.criollo@uao.edu.co","username":"ecriollo","password":"789"}' \
  http://localhost:5000/api/users

# 4. Actualizar un usuario existente (PUT /api/users/2)
curl -i -H "Content-Type: application/json" -X PUT \
  -d '{"name":"Maria Fernanda","email":"maria.fernanda@gmail.com","username":"mariaf","password":"456"}' \
  http://localhost:5000/api/users/2

# 5. Eliminar un usuario (DELETE /api/users/3)
curl -i -X DELETE http://localhost:5000/api/users/3

# 6. Validar error semántico 404 Not Found (GET /api/users/99)
curl -i http://localhost:5000/api/users/99
```

> [!TIP]
> **Ejecución desde Windows PowerShell:**  
> Utilice el operador stop-parsing `--%` para preservar las comillas JSON:
> ```powershell
> curl.exe --% -i -H "Content-Type: application/json" -X POST -d "{\"name\":\"Eduard Criollo\",\"email\":\"eduard.criollo@uao.edu.co\",\"username\":\"ecriollo\",\"password\":\"789\"}" http://localhost:5000/api/users
> ```

#### Evidencia 04: Pruebas CRUD sobre `/api/users` con cURL
* **Ruta de Evidencia:** [images/04_ejercicio3a_curl_crud_users.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/images/04_ejercicio3a_curl_crud_users.png)

![04_ejercicio3a_curl_crud_users.png](images/04_ejercicio3a_curl_crud_users.png)

---

#### Ejercicio 3.b: Pruebas del API REST de Usuarios usando Postman

Se incluye la colección preconfigurada en [config/Practica9_Postman_Collection.json](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/config/Practica9_Postman_Collection.json).

#### Evidencia 05: Pruebas CRUD sobre `/api/users` en Postman
* **Ruta de Evidencia:** [images/05_ejercicio3b_postman_crud_users.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/images/05_ejercicio3b_postman_crud_users.png)

![05_ejercicio3b_postman_crud_users.png](images/05_ejercicio3b_postman_crud_users.png)

---

### Ejercicio 4: ¿Qué sucede con los datos al apagar la máquina?

#### Respuesta Técnica Fundamentada:

**Los datos NO se pierden; permanecen 100 % íntegros y disponibles al volver a encender la máquina virtual.**

1. **Almacenamiento No Volátil en Disco (InnoDB Tablespaces):**  
   A diferencia de la Práctica 7 (donde la lista de libros se almacenaba en una estructura `list` en la memoria RAM volátil del proceso Python y se reiniciaba al detener el proceso o apagar la VM), en esta arquitectura cada operación `POST`, `PUT` o `DELETE` ejecuta una transacción confirmada mediante `db.session.commit()` contra el motor **InnoDB de MySQL 8.0**.
2. **Garantía ACID (Durabilidad):**  
   Al ejecutarse `COMMIT`, MySQL escribe los cambios en el *Redo Log* (`#ib_redo`) y en los archivos de espacio de tablas físicos (`/var/lib/mysql/myflaskapp/users.ibd` y `products.ibd`) alojados dentro del disco virtual persistente (`.vmdk` / `.vdi`) del sistema de archivos `ext4` de Ubuntu.
3. **Comportamiento ante `vagrant halt` y `vagrant up`:**  
   * Cuando se ejecuta `vagrant halt servidorWeb`, el sistema operativo envía la señal `SIGTERM` a `mysqld`, cerrando limpiamente los descriptores de archivo en disco.
   * Cuando se ejecuta `vagrant up servidorWeb`, systemd inicia automáticamente `mysql.service`, `webapp.service` y `apache2.service` (gracias a `systemctl enable`), montando nuevamente `/var/lib/mysql` con todos los registros creados o modificados antes del apagado.
   * *(Nota: El script `script.sh` solo se ejecuta durante el primer `vagrant up` o si se invoca explícitamente `vagrant provision`, e incluso en ese caso nuestras sentencias `CREATE TABLE IF NOT EXISTS` e `INSERT ... ON DUPLICATE KEY UPDATE` en `init.sql` preservan todos los registros adicionales).*

#### Evidencia 06: Comprobación Experimental de Persistencia tras `vagrant halt` y `vagrant up`
* **Ruta de Evidencia:** [images/06_ejercicio4_persistencia_reinicio_vm.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/images/06_ejercicio4_persistencia_reinicio_vm.png)

![06_ejercicio4_persistencia_reinicio_vm.png](images/06_ejercicio4_persistencia_reinicio_vm.png)

---

### Ejercicio 5: Complemente la Aplicación con la Funcionalidad Necesaria para Gestionar Productos

El quinto ejercicio exige ampliar la aplicación de extremo a extremo (Base de Datos + API REST + Plantillas Web) para gestionar un catálogo de **Productos**.

#### Ejercicio 5.a: Creación de la Tabla `products` en la Base de Datos
En [init.sql Líneas 33–51](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/init.sql#L33-L51) se definió la tabla `products` con los atributos `id` (`INT AUTO_INCREMENT PRIMARY KEY`), `name` (`VARCHAR(255)`), `description` (`VARCHAR(255)`), `price` (`DECIMAL(10,2)`) y `stock` (`INT`).

#### Ejercicio 5.b: Creación del Modelo ORM y API REST de Productos (`/api/products`)
1. **Modelo ORM ([webapp/products/models/product_model.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/products/models/product_model.py)):**  
   Implementa la clase `Products(db.Model)` y el método serializador `to_dict()`.
2. **Controlador Blueprint ([webapp/products/controllers/product_controller.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/products/controllers/product_controller.py)):**  
   Implementa los 5 endpoints RESTful:
   * `GET /api/products` -> Lista todos los productos (`200 OK`).
   * `GET /api/products/<int:product_id>` -> Obtiene un producto por ID (`200 OK` o `404 Not Found`).
   * `POST /api/products` -> Crea un nuevo producto en MySQL (`201 Created`).
   * `PUT /api/products/<int:product_id>` -> Actualiza nombre, descripción, precio y stock (`200 OK`).
   * `DELETE /api/products/<int:product_id>` -> Elimina el producto de MySQL (`200 OK`).

#### Comandos de Prueba cURL para `/api/products`:
```bash
# 1. Listar productos
curl -i -s http://localhost:5000/api/products

# 2. Crear un nuevo producto
curl -i -H "Content-Type: application/json" -X POST \
  -d '{"name":"Mouse Inalambrico Pro","description":"Sensor optico 25K DPI","price":79.99,"stock":30}' \
  http://localhost:5000/api/products

# 3. Actualizar precio y stock de un producto existente
curl -i -H "Content-Type: application/json" -X PUT \
  -d '{"name":"Monitor UltraWide 34 HDR","description":"Monitor curvo WQHD IPS 165Hz","price":510.00,"stock":12}' \
  http://localhost:5000/api/products/2

# 4. Eliminar un producto
curl -i -X DELETE http://localhost:5000/api/products/3
```

#### Evidencia 07: Pruebas CRUD sobre `/api/products` con cURL
* **Ruta de Evidencia:** [images/07_ejercicio5ab_api_rest_products_curl.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/images/07_ejercicio5ab_api_rest_products_curl.png)

![07_ejercicio5ab_api_rest_products_curl.png](images/07_ejercicio5ab_api_rest_products_curl.png)

#### Evidencia 08: Pruebas CRUD sobre `/api/products` en Postman
* **Ruta de Evidencia:** [images/08_ejercicio5b_postman_crud_products.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/images/08_ejercicio5b_postman_crud_products.png)

![08_ejercicio5b_postman_crud_products.png](images/08_ejercicio5b_postman_crud_products.png)

---

#### Ejercicio 5.c: Creación de los Templates Necesarios para la Gestión de Productos

Se crearon las plantillas HTML y las funciones JavaScript Fetch:
1. **[webapp/web/templates/products.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/products.html):** Vista principal de inventario accesible en `/products` con formulario de creación (`Add New Product`) y tabla dinámica (`Products Inventory List`).
2. **[webapp/web/templates/edit_product.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/edit_product.html):** Vista de edición individual accesible en `/edit_product/<id>` que precarga los datos actuales del producto mediante `fetch('/api/products/' + productId)` y envía los cambios por `PUT`.
3. **[webapp/web/static/script.js Líneas 147–288](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/static/script.js#L147-L288):** Funciones `getProducts()`, `createProduct()`, `updateProduct()` y `deleteProduct(productId)`.

#### Evidencia 09: Interfaz Web de Gestión de Productos (`products.html` y `edit_product.html`)
* **Ruta de Evidencia:** [images/09_ejercicio5c_templates_gestion_productos.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/images/09_ejercicio5c_templates_gestion_productos.png)

![09_ejercicio5c_templates_gestion_productos.png](images/09_ejercicio5c_templates_gestion_productos.png)

---

### Ejercicio 6: Despliegue del Sitio Web en Apache (`libapache2-mod-wsgi-py3`)

El sexto ejercicio requiere desplegar la aplicación web y la API REST sobre el servidor **Apache2** utilizando el conector WSGI para Python 3.

#### Arquitectura e Implementación del Despliegue:
1. **Instalación del Módulo WSGI ([script.sh Líneas 26–27](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/script.sh#L26-L27)):**
   ```bash
   sudo apt-get install -y apache2 libapache2-mod-wsgi-py3
   ```
2. **Creación del Script Adaptador WSGI ([webapp/wsgi.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/wsgi.py)):**
   ```python
   import os
   import sys

   CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
   if CURRENT_DIR not in sys.path:
       sys.path.insert(0, CURRENT_DIR)

   from web.views import app as application
   ```
3. **Configuración del VirtualHost ([config/webapp_apache.conf](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/config/webapp_apache.conf)):**
   Configura `WSGIDaemonProcess miniwebapp`, `WSGIScriptAlias / /var/www/webapp/wsgi.py` y el alias de recursos estáticos `/static`.
4. **Activación del Sitio en Apache ([script.sh Líneas 82–90](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/script.sh#L82-L90)):**
   ```bash
   sudo cp /vagrant/config/webapp_apache.conf /etc/apache2/sites-available/webapp.conf
   sudo a2enmod wsgi
   sudo a2dissite 000-default.conf
   sudo a2ensite webapp.conf
   sudo systemctl restart apache2
   ```

#### Verificación del Despliegue en Apache2:
```bash
# Desde dentro de servidorWeb (Puerto 80):
curl -i http://localhost/api/products

# Desde Windows PowerShell (IP privada o puerto redirigido 8080):
curl.exe -i http://192.168.60.3/api/products
curl.exe -i http://localhost:8080/api/products
```

#### Evidencia 10: Sitio Web y API REST Servidos por Apache2 + `mod_wsgi`
* **Ruta de Evidencia:** [images/10_ejercicio6_despliegue_apache_wsgi.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/images/10_ejercicio6_despliegue_apache_wsgi.png)

![10_ejercicio6_despliegue_apache_wsgi.png](images/10_ejercicio6_despliegue_apache_wsgi.png)

* **Análisis Técnico:**  
  La cabecera de respuesta HTTP muestra `Server: Apache/2.4.52 (Ubuntu) mod_wsgi/4.9.0 Python/3.10`, demostrando que las peticiones ya no son atendidas por el servidor de desarrollo de Flask, sino por el motor multiproceso de Apache2 en el puerto 80.

---

## 5. Plan de Contingencia Audiovisual y Scripts de Sustentación

Para respaldar la presentación en vivo ante el docente, el repositorio incluye:

1. **Guía de Sustentación Paso a Paso:** [SUSTENTACION.md](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/SUSTENTACION.md) con mapeo de ventanas, líneas exactas de código a señalar en VS Code y guion verbal.
2. **Video de Contingencia (720p, 24 fps):** [video/sustentacion_practica9.mp4](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/video/sustentacion_practica9.mp4).
3. **Scripts Interactivos de Demostración:**
   * Desde Windows PowerShell: [scripts/demo_sustentacion.ps1](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/scripts/demo_sustentacion.ps1)
   * Desde Ubuntu SSH (`servidorWeb`): [scripts/demo_sustentacion.sh](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/scripts/demo_sustentacion.sh)

---

## 6. Referencias Bibliográficas

1. Mondragón, O. (2024). *Repositorio Oficial MiniWebApp*. GitHub. https://github.com/omondragon/MiniWebApp
2. Pallets Projects. (2024). *Flask Documentation (2.3.x) — Modular Applications with Blueprints & mod_wsgi (Apache)*. https://flask.palletsprojects.com/
3. SQLAlchemy Authors. (2024). *Flask-SQLAlchemy Documentation*. https://flask-sqlalchemy.palletsprojects.com/
4. Dumpleton, G. (2024). *mod_wsgi Documentation — Virtual Environments and Daemon Mode*. https://modwsgi.readthedocs.io/
5. Postman Inc. (2024). *Postman API Platform*. https://www.postman.com/
