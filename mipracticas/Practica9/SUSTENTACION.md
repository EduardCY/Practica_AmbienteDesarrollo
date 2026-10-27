# Guía de Sustentación Oral en Pantalla — Práctica 9: Aplicación Web + API REST en Python Flask + MySQL + Apache WSGI

**Modalidad de Sustentación:** Presentación interactiva en pantalla compartida abriendo cada archivo fuente en el editor, señalando las líneas de código exactas que justifican las decisiones de diseño y ejecutando las pruebas operativas en sus terminales correspondientes.  
**Asignatura:** Ambiente de Desarrollo / Servicios Telemáticos  
**Profesor Evaluador:** Prof. Oscar Mondragón  
**Estudiante:** Eduard Criollo Yule

---

## MAPA DE TERMINALES Y ENTORNO DE SUSTENTACIÓN

Para una sustentación ordenada y ágil, tenga abiertas **dos terminales y dos aplicaciones gráficas**:

```
+----------------------------------------------------------------------------------------------------+
| VENTANA 1: EDITOR / CÓDIGO (VS Code)        | VENTANA 2: TERMINAL HOST (PowerShell en Windows)     |
| - Muestra archivos y líneas de código       | - Ejecuta 'vagrant up / halt / ssh servidorWeb'      |
|   (Vagrantfile, init.sql, views.py,         | - Ejecuta pruebas cURL desde Windows                 |
|    product_controller.py, wsgi.py, etc.)    | - Ejecuta .\scripts\demo_sustentacion.ps1            |
+---------------------------------------------+------------------------------------------------------+
| VENTANA 3: TERMINAL GUEST (SSH servidorWeb) | VENTANA 4: NAVEGADOR WEB Y POSTMAN (Windows)         |
| - Conectada vía: vagrant ssh servidorWeb    | - Navegador: http://localhost:5000 (Flask)           |
| - Inspección de MySQL (users y products)    | - Navegador: http://localhost:8080 (Apache WSGI)     |
| - Estado de systemd y Apache2 (mod_wsgi)    | - Postman: Colección CRUD /api/users y /api/products |
+---------------------------------------------+------------------------------------------------------+
```

---

## ÍNDICE DE NAVEGACIÓN Y SECUENCIA DE SUSTENTACIÓN

* [FASE 0: Exposición de Archivos de Configuración y Código en VS Code](#fase-0-exposición-de-archivos-de-configuración-y-código-en-vs-code)
  * [0.1 `Vagrantfile` y `script.sh` — Orquestación y Aprovisionamiento](#01-archivos-vagrantfile-y-scriptsh--orquestación-y-aprovisionamiento)
  * [0.2 `init.sql` — Esquema Relacional MySQL (`users` y `products`)](#02-archivo-initsql--esquema-relacional-mysql-users-y-products)
  * [0.3 `webapp/config.py` y `webapp/users/models/db.py` — Conexión ORM SQLAlchemy](#03-archivos-webappconfigpy-y-webappusersmodelsdbpy--conexión-orm-sqlalchemy)
  * [0.4 `user_model.py` y `user_controller.py` — Arquitectura REST de Usuarios](#04-archivos-user_modelpy-y-user_controllerpy--arquitectura-rest-de-usuarios)
  * [0.5 `product_model.py` y `product_controller.py` — API REST de Productos (Ejercicio 5.b)](#05-archivos-product_modelpy-y-product_controllerpy--api-rest-de-productos-ejercicio-5b)
  * [0.6 `views.py`, `script.js` y Plantillas HTML — Interfaz Web (Ejercicio 5.c)](#06-archivos-viewspy-scriptjs-y-plantillas-html--interfaz-web-ejercicio-5c)
  * [0.7 `wsgi.py` y `config/webapp_apache.conf` — Despliegue en Apache2 (Ejercicio 6)](#07-archivos-wsgipy-y-configwebapp_apacheconf--despliegue-en-apache2-ejercicio-6)
* [FASE 1: Demostración Operativa Ejercicios 1, 2, 3 y 4 (Usuarios y Persistencia en Disco)](#fase-1-demostración-operativa-ejercicios-1-2-3-y-4-usuarios-y-persistencia-en-disco)
* [FASE 2: Demostración Operativa Ejercicio 5 (Gestión Integral de Productos)](#fase-2-demostración-operativa-ejercicio-5-gestión-integral-de-productos)
* [FASE 3: Demostración Operativa Ejercicio 6 (Sitio Web Desplegado en Apache2 WSGI)](#fase-3-demostración-operativa-ejercicio-6-sitio-web-desplegado-en-apache2-wsgi)
* [FASE 4: Preguntas Frecuentes del Evaluador](#fase-4-preguntas-frecuentes-del-evaluador)
* [FASE 5: Plan de Contingencia Audiovisual (Video y Scripts)](#fase-5-plan-de-contingencia-audiovisual-video-y-scripts)

---

## FASE 0: Exposición de Archivos de Configuración y Código en VS Code

> **Dónde mostrar:** En la **Ventana 1 (VS Code)** abriendo cada archivo en orden.

---

### 0.1 Archivos `Vagrantfile` y `script.sh` — Orquestación y Aprovisionamiento

* **Acción en pantalla:** Abrir [Vagrantfile](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/Vagrantfile) y [script.sh](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/script.sh).
* **Líneas a señalar y explicar:**
  1. **[Vagrantfile Líneas 22–28](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/Vagrantfile#L22-L28):** Definición del nodo `servidorWeb` sobre `bento/ubuntu-22.04` con IP privada `192.168.60.3` (idéntica al repositorio guía `MiniWebApp`).
  2. **[Vagrantfile Líneas 33–34](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/Vagrantfile#L33-L34):** Redirección de puertos `5000 => 5000` (Flask directo) y `80 => 8080` (Apache2 WSGI) para probar cómodamente desde Windows.
  3. **[script.sh Líneas 15–29](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/script.sh#L15-L29):** Instalación desatendida de `mysql-server`, `apache2` y `libapache2-mod-wsgi-py3`.
  4. **[script.sh Líneas 49–57](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/script.sh#L49-L57):** Instalación de `Flask==2.3.3`, `flask-cors`, `Flask-MySQLdb` y `Flask-SQLAlchemy` usando `--ignore-installed blinker` para evitar bloqueos de `distutils` en Ubuntu 22.04.

> **Guion verbal ante el profesor:**
> *"Profesor, en el `Vagrantfile` definimos la máquina `servidorWeb` con IP `192.168.60.3` (líneas 22-28) y redirigimos tanto el puerto 5000 para Flask como el puerto 80 hacia el 8080 para Apache. En `script.sh` automatizamos la instalación de MySQL 8.0, las librerías `Flask-SQLAlchemy` y `Flask-MySQLdb` previniendo conflictos con `blinker`, y dejamos activos tanto el servicio de Flask como el VirtualHost de Apache con `mod_wsgi`."*

---

### 0.2 Archivo `init.sql` — Esquema Relacional MySQL (`users` y `products`)

* **Acción en pantalla:** Abrir [init.sql](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/init.sql).
* **Líneas a señalar y explicar:**
  1. **[Líneas 9–13](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/init.sql#L9-L13):** Creación de la base de datos `myflaskapp` con `utf8mb4`.
  2. **[Líneas 16–31](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/init.sql#L16-L31):** Creación de la tabla `users` e inserción de los registros iniciales `juan` y `maria` (Ejercicio 1).
  3. **[Líneas 34–51](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/init.sql#L34-L51):** Creación de la tabla `products` (`id`, `name`, `description`, `price`, `stock`) e inserción de 3 productos semilla cumpliendo el **Ejercicio 5.a**.
  4. **[Líneas 55–66](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/init.sql#L55-L66):** Configuración de autenticación `mysql_native_password` para `root` y `flaskuser` en MySQL 8.0.

> **Guion verbal ante el profesor:**
> *"En `init.sql`, entre las líneas 16 y 31 creamos la tabla `users` con los usuarios iniciales `juan` y `maria`. Y entre las líneas 34 y 51 damos cumplimiento al Ejercicio 5.a creando la tabla `products` con llave primaria autoincremental, nombre, descripción, precio decimal y stock en inventario."*

---

### 0.3 Archivos `webapp/config.py` y `webapp/users/models/db.py` — Conexión ORM SQLAlchemy

* **Acción en pantalla:** Abrir [webapp/config.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/config.py) y [webapp/users/models/db.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/models/db.py).
* **Líneas a señalar y explicar:**
  1. **[config.py Líneas 15–24](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/config.py#L15-L24):** Construcción de `SQLALCHEMY_DATABASE_URI = f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'`.
  2. **[db.py Líneas 9–11](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/models/db.py#L9-L11):** Instancia única `db = SQLAlchemy()` compartida por los modelos `Users` y `Products`.

---

### 0.4 Archivos `user_model.py` y `user_controller.py` — Arquitectura REST de Usuarios

* **Acción en pantalla:** Abrir [webapp/users/models/user_model.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/models/user_model.py) y [webapp/users/controllers/user_controller.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/controllers/user_controller.py).
* **Líneas a señalar y explicar:**
  1. **[user_model.py Líneas 10–25](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/models/user_model.py#L10-L25):** Clase `Users(db.Model)` que mapea las columnas de la tabla `users`.
  2. **[user_controller.py Línea 17](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/controllers/user_controller.py#L17):** Definición del `Blueprint('user_controller', __name__)`.
  3. **[user_controller.py Líneas 20–88](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/users/controllers/user_controller.py#L20-L88):** Endpoints CRUD (`GET /api/users`, `GET /api/users/<id>`, `POST /api/users`, `PUT /api/users/<id>`, `DELETE /api/users/<id>`) utilizando `db.session.add()`, `db.session.commit()` y `Users.query.get_or_404()`.

---

### 0.5 Archivos `product_model.py` y `product_controller.py` — API REST de Productos (Ejercicio 5.b)

* **Acción en pantalla:** Abrir [webapp/products/models/product_model.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/products/models/product_model.py) y [webapp/products/controllers/product_controller.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/products/controllers/product_controller.py).
* **Líneas a señalar y explicar:**
  1. **[product_model.py Líneas 13–36](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/products/models/product_model.py#L13-L36):** Modelo ORM `Products(db.Model)` mapeado a `__tablename__ = 'products'` con `id`, `name`, `description`, `price` y `stock`, más el método serializador `to_dict()`.
  2. **[product_controller.py Líneas 19–102](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/products/controllers/product_controller.py#L19-L102):** Blueprint `product_controller` con las 5 rutas REST CRUD bajo `/api/products` (`GET`, `GET /<id>`, `POST` con retorno `201 Created`, `PUT /<id>` y `DELETE /<id>`).

> **Guion verbal ante el profesor:**
> *"Para el Ejercicio 5.b replicamos el patrón arquitectónico de Blueprints creando el paquete `products`. En `product_model.py` (líneas 13-36) definimos el modelo `Products` sobre SQLAlchemy, y en `product_controller.py` (líneas 19-102) implementamos los 5 endpoints RESTful en `/api/products` con validación de tipos numéricos para precio y stock."*

---

### 0.6 Archivos `views.py`, `script.js` y Plantillas HTML — Interfaz Web (Ejercicio 5.c)

* **Acción en pantalla:** Abrir [webapp/web/views.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/views.py), [webapp/web/static/script.js](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/static/script.js), [webapp/web/templates/products.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/products.html) y [webapp/web/templates/edit_product.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/edit_product.html).
* **Líneas a señalar y explicar:**
  1. **[views.py Líneas 25–26](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/views.py#L25-L26):** Registro de ambos Blueprints (`app.register_blueprint(user_controller)` y `app.register_blueprint(product_controller)`).
  2. **[views.py Líneas 43–53](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/views.py#L43-L53):** Rutas `/products` y `/edit_product/<string:id>` que renderizan las nuevas plantillas de productos.
  3. **[script.js Líneas 147–288](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/static/script.js#L147-L288):** Funciones asíncronas `getProducts()`, `createProduct()`, `updateProduct()` y `deleteProduct(productId)` que consumen `/api/products` mediante `fetch()`.

---

### 0.7 Archivos `wsgi.py` y `config/webapp_apache.conf` — Despliegue en Apache2 (Ejercicio 6)

* **Acción en pantalla:** Abrir [webapp/wsgi.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/wsgi.py) y [config/webapp_apache.conf](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/config/webapp_apache.conf).
* **Líneas a señalar y explicar:**
  1. **[wsgi.py Líneas 18–22](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/wsgi.py#L18-L22):** Inserción de `/var/www/webapp` en `sys.path` y exposición del objeto `from web.views import app as application` requerido por `mod_wsgi`.
  2. **[webapp_apache.conf Líneas 11–16](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/config/webapp_apache.conf#L11-L16):** Directivas `WSGIDaemonProcess miniwebapp`, `WSGIProcessGroup miniwebapp` y `WSGIScriptAlias / /var/www/webapp/wsgi.py`.

> **Guion verbal ante el profesor:**
> *"Para el Ejercicio 6, creamos el adaptador `wsgi.py` que expone la instancia de Flask como `application` según el estándar PEP 3333. En `config/webapp_apache.conf` configuramos el VirtualHost de Apache en el puerto 80 usando `libapache2-mod-wsgi-py3` con un grupo de procesos demonio dedicado."*

---

## FASE 1: Demostración Operativa Ejercicios 1, 2, 3 y 4 (Usuarios y Persistencia en Disco)

### 1.1 Ejercicio 1: Inspección de MySQL y Tablas Creadas

* **Dónde ejecutar:** `[VENTANA 3: TERMINAL GUEST (SSH servidorWeb)]`
* **Comandos:**

  1. Verificar estado del servicio MySQL:
  ```bash
  sudo systemctl status mysql --no-pager
  ```

  2. Inspeccionar base de datos, tablas y usuarios iniciales:
  ```bash
  mysql -u root -proot -e "USE myflaskapp; SHOW TABLES; DESCRIBE users; SELECT * FROM users;"
  ```
* **Guion corto:** *"Verificamos que MySQL está activo y consultamos la base de datos `myflaskapp`. Observamos las tablas `users` y `products`, y los registros iniciales `juan` y `maria`."*

---

### 1.2 Ejercicio 2 y 3.a: Pruebas CRUD de `/api/users` con cURL

* **Dónde ejecutar:** `[VENTANA 2: WINDOWS POWERSHELL]` o `[VENTANA 3: SSH servidorWeb]`
* **Comandos:**

  1. Listar usuarios (`GET /api/users`):
  ```powershell
  curl.exe -i http://localhost:5000/api/users
  ```

  2. Crear usuario (`POST /api/users` en PowerShell con `--%`):
  ```powershell
  curl.exe --% -i -H "Content-Type: application/json" -X POST -d "{\"name\":\"Eduard Criollo\",\"email\":\"eduard.criollo@uao.edu.co\",\"username\":\"ecriollo\",\"password\":\"789\"}" http://localhost:5000/api/users
  ```

  3. Actualizar usuario 2 (`PUT /api/users/2`):
  ```powershell
  curl.exe --% -i -H "Content-Type: application/json" -X PUT -d "{\"name\":\"Maria Fernanda\",\"email\":\"maria.fernanda@gmail.com\",\"username\":\"mariaf\",\"password\":\"456\"}" http://localhost:5000/api/users/2
  ```

  4. Eliminar usuario 3 (`DELETE /api/users/3`):
  ```powershell
  curl.exe -i -X DELETE http://localhost:5000/api/users/3
  ```

---

### 1.3 Ejercicio 3.b: Pruebas en Postman (`/api/users`)

* **Dónde ejecutar:** `[VENTANA 4: POSTMAN EN WINDOWS]`
* **Acción:** Importar [config/Practica9_Postman_Collection.json](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/config/Practica9_Postman_Collection.json) y ejecutar `1.3 POST - Crear nuevo usuario (Eduard Criollo)` y `1.1 GET - Listar todos los usuarios`.

---

### 1.4 Ejercicio 4: ¿Qué sucede con los datos al apagar la máquina?

* **Dónde ejecutar:** `[VENTANA 2: WINDOWS POWERSHELL]`
* **Comandos:**

  1. Apagar la máquina virtual:
  ```powershell
  vagrant halt servidorWeb
  ```

  2. Volver a encender la máquina virtual:
  ```powershell
  vagrant up servidorWeb
  ```

  3. Comprobar que el usuario creado sigue almacenado en MySQL:
  ```powershell
  curl.exe -i http://localhost:5000/api/users
  ```
* **Guion corto:** *"Al apagar la máquina con `vagrant halt` y encenderla con `vagrant up`, los datos creados permanecen intactos porque SQLAlchemy confirma cada transacción (`db.session.commit()`) sobre el motor InnoDB de MySQL en el disco virtual persistente (`/var/lib/mysql`), a diferencia de una lista volátil en memoria RAM."*

---

## FASE 2: Demostración Operativa Ejercicio 5 (Gestión Integral de Productos)

### 2.1 Ejercicio 5.a: Verificar Tabla `products` en MySQL

* **Dónde ejecutar:** `[VENTANA 3: SSH servidorWeb]`
* **Comando:**

  Consultar estructura y registros de la tabla `products`:
  ```bash
  mysql -u root -proot -e "USE myflaskapp; DESCRIBE products; SELECT * FROM products;"
  ```

### 2.2 Ejercicio 5.b: Pruebas CRUD de `/api/products` (cURL y Postman)

* **Dónde ejecutar:** `[VENTANA 2: WINDOWS POWERSHELL]` y `[VENTANA 4: POSTMAN]`
* **Comandos:**

  1. Listar productos (`GET /api/products`):
  ```powershell
  curl.exe -i http://localhost:5000/api/products
  ```

  2. Crear nuevo producto (`POST /api/products`):
  ```powershell
  curl.exe --% -i -H "Content-Type: application/json" -X POST -d "{\"name\":\"Mouse Inalambrico Pro\",\"description\":\"Sensor optico 25K DPI\",\"price\":79.99,\"stock\":30}" http://localhost:5000/api/products
  ```

  3. Actualizar producto 2 (`PUT /api/products/2`):
  ```powershell
  curl.exe --% -i -H "Content-Type: application/json" -X PUT -d "{\"name\":\"Monitor UltraWide 34 HDR\",\"description\":\"Monitor curvo WQHD IPS 165Hz\",\"price\":510.00,\"stock\":12}" http://localhost:5000/api/products/2
  ```

### 2.3 Ejercicio 5.c: Demostración de los Templates Web de Productos

* **Dónde mostrar:** `[VENTANA 4: NAVEGADOR WEB EN WINDOWS]`
* **URL:** Abrir `http://localhost:5000/products` (o `http://192.168.60.3:5000/products`).
* **Acción en vivo:**
  1. Mostrar el formulario **Add New Product** y la tabla **Products Inventory List** ([products.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/products.html)).
  2. Crear un producto desde el formulario web y ver cómo se actualiza la tabla asíncronamente vía `fetch()`.
  3. Hacer clic en el botón **Edit** de un producto para abrir [edit_product.html](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/webapp/web/templates/edit_product.html), modificar su precio o stock y guardar cambios.

---

## FASE 3: Demostración Operativa Ejercicio 6 (Sitio Web Desplegado en Apache2 WSGI)

* **Dónde ejecutar:** `[VENTANA 3: SSH servidorWeb]` y `[VENTANA 4: NAVEGADOR WEB]`
* **Comandos en `servidorWeb`:**

  1. Verificar estado del servicio Apache2:
  ```bash
  sudo systemctl status apache2 --no-pager
  ```

  2. Verificar que el módulo `wsgi` está activo en Apache:
  ```bash
  apache2ctl -M | grep wsgi
  ```

  3. Comprobar cabecera HTTP `Server: Apache/2.4.52 (Ubuntu) mod_wsgi`:
  ```bash
  curl -i http://localhost/api/products
  ```
* **En el Navegador de Windows:**
  Abrir `http://localhost:8080/products` o `http://192.168.60.3/products`.
* **Guion corto:** *"Finalmente, comprobamos el Ejercicio 6 consumiendo la aplicación en el puerto 80 a través de Apache2. Al inspeccionar las cabeceras HTTP con `curl -i`, observamos `Server: Apache/2.4.52 (Ubuntu)` junto con `mod_wsgi`, confirmando que Apache gestiona la aplicación Flask en producción."*

---

## FASE 4: Preguntas Frecuentes del Evaluador

1. **¿Por qué se usa `db = SQLAlchemy()` en un archivo separado (`db.py`) y luego `db.init_app(app)` en `views.py`?**
   * *Respuesta:* Para aplicar el patrón *Application Factory* y evitar referencias circulares (*Circular Imports*). Si `db` se creara dentro de `views.py`, cuando `views.py` importa los controladores y estos importan los modelos, los modelos tendrían que volver a importar `views.py` antes de que termine de inicializarse.
2. **¿Cuál es la diferencia técnica entre correr Flask con `flask run` y desplegarlo en Apache con `libapache2-mod-wsgi-py3`?**
   * *Respuesta:* `flask run` utiliza el servidor de desarrollo *Werkzeug*, diseñado para depuración local de un solo proceso. En cambio, Apache2 con `mod_wsgi` (`WSGIDaemonProcess`) administra múltiples hilos de trabajo aislados en C nativo, sirve los archivos estáticos (`/static`) directamente sin sobrecargar Python y gestiona el ciclo de vida del proceso ante caídas.
3. **¿Cómo se comunican las plantillas HTML con la base de datos en esta arquitectura?**
   * *Respuesta:* Las plantillas HTML no acceden directamente a MySQL; cargan el script `/static/script.js` en el navegador del cliente, el cual realiza peticiones HTTP asíncronas (`fetch`) con cargas JSON hacia los endpoints REST (`/api/users` y `/api/products`), desacoplando completamente el frontend del backend.

---

## FASE 5: Plan de Contingencia Audiovisual (Video y Scripts)

* **Video Demostrativo Completo (720p, 24 fps):**  
  [video/sustentacion_practica9.mp4](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica9/video/sustentacion_practica9.mp4)
* **Script Automatizado en Windows PowerShell:**

  1. Navegar al directorio de la práctica:
  ```powershell
  cd d:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Practica9
  ```

  2. Ejecutar script de demostración:
  ```powershell
  .\scripts\demo_sustentacion.ps1
  ```
* **Script Automatizado en Ubuntu SSH (`servidorWeb`):**

  Ejecutar script de demostración:
  ```bash
  bash /vagrant/scripts/demo_sustentacion.sh
  ```
