# Guía de Sustentación Oral en Pantalla — Práctica 7: API REST en Python Flask, MySQL e IoT Ubidots

**Modalidad de Sustentación:** Presentación interactiva en pantalla compartida abriendo cada archivo fuente, señalando las líneas de código exactas que justifican las decisiones de diseño y ejecutando las pruebas operativas en sus terminales correspondientes.
**Asignatura:** Ambiente de Desarrollo / Servicios Telemáticos
**Profesor Evaluador:** Prof. Oscar Mondragón
**Estudiante:** Eduard Criollo Yule

---

## MAPA DE TERMINALES Y ENTORNO DE SUSTENTACIÓN

Para una sustentación ordenada y profesional, se recomienda tener abiertas **dos terminales y dos aplicaciones gráficas**:

```
+---------------------------------------------------------------------------------------------------+
| VENTANA 1: EDITOR / CÓDIGO (VS Code)       | VENTANA 2: TERMINAL HOST (PowerShell en Windows)     |
| - Muestra archivos y líneas de código      | - Ejecuta 'vagrant up / ssh'                         |
|   (Vagrantfile, apirest.py, etc.)          | - Ejecuta pruebas cURL desde el anfitrión            |
|                                            | - Ejecuta .\scripts\demo_sustentacion.ps1            |
+--------------------------------------------+------------------------------------------------------+
| VENTANA 3: TERMINAL GUEST (SSH servidorRest)| VENTANA 4: NAVEGADOR Y POSTMAN (Windows)             |
| - Conectada vía: vagrant ssh servidorRest  | - Postman: Pruebas CRUD y envío a Ubidots            |
| - Estado de systemd y MySQL                | - Navegador: Dashboard Ubidots en vivo               |
| - Ejecuta el cliente IoT testUbidots.py    | - Correo institucional UAO: Alerta recibida          |
+---------------------------------------------------------------------------------------------------+
```

---

## ÍNDICE DE NAVEGACIÓN Y SECUENCIA DE SUSTENTACIÓN

* [FASE 0: Exposición de Archivos de Configuración e Infraestructura (En Editor VS Code)](#fase-0-exposición-de-archivos-de-configuración-e-infraestructura)
  * [0.1 `Vagrantfile` — Infraestructura Virtual y Red](#01-archivo-vagrantfile--infraestructura-virtual-y-red)
  * [0.2 `config/apirest.service` — Ciclo de Vida y Resiliencia en systemd](#02-archivo-configapirestservice--ciclo-de-vida-y-resiliencia-en-systemd)
  * [0.3 `config/schema.sql` — Esquema Relacional de Base de Datos](#03-archivo-configschemasql--esquema-relacional-de-base-de-datos)
  * [0.4 `.env.example` — Desacoplamiento de Secretos y Seguridad](#04-archivo-envexample--desacoplamiento-de-secretos-y-seguridad)
  * [0.5 `APIRestFlask/apirest.py` — Arquitectura de la API REST en Memoria](#05-archivo-apirestflaskapirestpy--arquitectura-de-la-api-rest-en-memoria)
  * [0.6 `APIRestFlask/apirest_mysql.py` — Persistencia Relacional MySQL](#06-archivo-apirestflaskapirest_mysqlpy--persistencia-relacional-mysql)
  * [0.7 `UbidotsClient/testUbidots.py` — Cliente IoT y 5 Variables](#07-archivo-ubidotsclienttestubidotspy--cliente-iot-y-5-variables)
* [FASE 1: Demostración Operativa Parte 1 (API REST Flask, cURL y Postman)](#fase-1-demostración-operativa-parte-1-api-rest-flask-curl-y-postman)
* [FASE 2: Demostración Operativa Parte 2 (Cliente IoT, Ubidots y cURL/Postman)](#fase-2-demostración-operativa-parte-2-cliente-iot-ubidots-y-curlpostman)
* [FASE 3: Demostración del Dashboard en Tiempo Real y Evento por Correo](#fase-3-demostración-del-dashboard-en-tiempo-real-y-evento-por-correo)
* [FASE 4: Preguntas Frecuentes del Evaluador](#fase-4-preguntas-frecuentes-del-evaluador)
* [FASE 5: Plan de Contingencia Audiovisual (Video y Script de Respaldo)](#fase-5-plan-de-contingencia-audiovisual-video-y-script-de-respaldo)

---

## FASE 0: Exposición de Archivos de Configuración e Infraestructura

> **Dónde ejecutar / mostrar:** En la **Ventana 1 (Editor VS Code)** con los archivos abiertos y la **Terminal 1 (Host Windows)** lista.

---

### 0.1 Archivo `Vagrantfile` — Infraestructura Virtual y Red

* **Acción en pantalla:** Abrir el archivo [Vagrantfile](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/Vagrantfile).
* **Terminal de soporte (Opcional si se arranca en vivo):** `[TERMINAL 1: WINDOWS POWERSHELL]`

  ```powershell
  cd d:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Practica7
  vagrant status
  ```
* **Líneas a señalar en el archivo y explicar:**

  1. **[Líneas 16–20](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/Vagrantfile#L16-L20):** Dimensionamiento de 1024 MB de RAM y 1 vCPU en VirtualBox.*¿Por qué?* Flask consume ~45 MB y MySQL ~280 MB; 1 GB provee más del 60 % de RAM libre sin sobrecargar el anfitrión Windows.
  2. **[Líneas 26–28](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/Vagrantfile#L26-L28):** Imagen base `bento/ubuntu-22.04` (Ubuntu 22.04 LTS), manteniendo homogeneidad tecnológica con la Práctica 6.
  3. **[Línea 31](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/Vagrantfile#L31):** Red privada Host-Only con IP fija `192.168.50.3` dentro de la subred `192.168.50.0/24`.
  4. **[Línea 35](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/Vagrantfile#L35):** Redirección de puertos `forwarded_port: guest 5000 => host 5000`. Permite que las consultas a `http://localhost:5000/books` funcionen igual desde Windows o desde la VM.
  5. **[Líneas 38–101](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/Vagrantfile#L38-L101):** Script desatendido de aprovisionamiento en shell (APT, Flask, MySQL, `schema.sql` y `systemd`).

> **Guion verbal ante el profesor:**
> *"Profesor, abro el `Vagrantfile`. En las líneas 16 a 20 definimos 1 GB de RAM y 1 CPU, recursos óptimos para alojar Flask y MySQL. En las líneas 30 a 35 configuramos la interfaz de red: asignamos la IP privada 192.168.50.3 dentro de nuestra subred de prácticas y añadimos una redirección del puerto 5000 al anfitrión para poder consumir los endpoints tanto por localhost:5000 como por la IP privada. Finalmente, entre las líneas 38 y 101 automatizamos todo el aprovisionamiento instalando librerías, cargando la base de datos y levantando el demonio systemd."*

---

### 0.2 Archivo `config/apirest.service` — Ciclo de Vida y Resiliencia en systemd

* **Acción en pantalla:** Abrir el archivo [config/apirest.service](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/apirest.service).
* **Terminal para verificar estado en vivo:** `[TERMINAL 2: GUEST UBUNTU (SSH servidorRest)]`

  ```bash
  sudo systemctl status apirest.service --no-pager
  ```
* **Líneas a señalar en el archivo y explicar:**

  1. **[Líneas 3–4](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/apirest.service#L3-L4):** `After=network.target mysql.service` y `Wants=mysql.service`. Previene condiciones de carrera garantizando que la red y MySQL estén listos antes de levantar Flask.
  2. **[Líneas 8–9](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/apirest.service#L8-L9):** `User=vagrant` y `Group=vagrant`. Mínimos privilegios (no corre como `root`).
  3. **[Líneas 16–17](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/apirest.service#L16-L17):** `Restart=always` y `RestartSec=3`. Alta disponibilidad: si la aplicación cae, `systemd` la reinicia en 3 segundos.
  4. **[Línea 20](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/apirest.service#L20):** `WantedBy=multi-user.target`. Autoarranque garantizado en cada reinicio del sistema operativo.

> **Guion verbal ante el profesor:**
> *"En `config/apirest.service`, evitamos ejecutar la API de forma precaria en primer plano por terminal. En las líneas 3 y 4 le indicamos a systemd que espere a que MySQL y la red estén listos. En las líneas 16 y 17 configuramos `Restart=always` con 3 segundos de espera, garantizando que el servicio web sea tolerante a fallos y no dependa de tener una sesión SSH abierta."*

---

### 0.3 Archivo `config/schema.sql` — Esquema Relacional de Base de Datos

* **Acción en pantalla:** Abrir el archivo [config/schema.sql](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/schema.sql).
* **Terminal para verificar datos en vivo:** `[TERMINAL 2: GUEST UBUNTU (SSH servidorRest)]`

  ```bash
  mysql -u flaskuser -pflaskpassword -e "USE myflaskapp; SELECT * FROM books;"
  ```
* **Líneas a señalar en el archivo y explicar:**

  1. **[Líneas 9–11](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/schema.sql#L9-L11):** Codificación `utf8mb4` para soporte de acentos y caracteres especiales.
  2. **[Líneas 16–22](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/schema.sql#L16-L22):** Motor `InnoDB` y clave primaria autoincremental `id INT AUTO_INCREMENT PRIMARY KEY` (documento de comandos SQL de Contenidos).
  3. **[Líneas 25–31](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/schema.sql#L25-L31):** Semilla inicial de libros (`La hojarasca`, `El coronel...`) con `ON DUPLICATE KEY UPDATE`.
  4. **[Líneas 34–37](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/schema.sql#L34-L37):** Usuario `flaskuser` con privilegios específicos sobre `myflaskapp`.

> **Guion verbal ante el profesor:**
> *"En `config/schema.sql` damos cumplimiento directo al material teórico de comandos básicos de SQL. En las líneas 16 a 22 creamos la tabla `books` con llave primaria autoincremental en InnoDB. En las líneas 25 a 31 insertamos los mismos registros de prueba de la guía, y en las líneas 34 a 37 creamos el usuario dedicado `flaskuser` para aplicar buenas prácticas de seguridad."*

---

### 0.4 Archivo `.env.example` — Desacoplamiento de Secretos y Seguridad

* **Acción en pantalla:** Abrir el archivo [.env.example](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/.env.example).
* **Líneas a señalar en el archivo y explicar:**
  1. **[Líneas 8–12](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/.env.example#L8-L12):** `FLASK_RUN_HOST=0.0.0.0` y puerto `5000`.
  2. **[Líneas 24–26](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/.env.example#L24-L26):** Parámetros `UBIDOTS_TOKEN` y `UBIDOTS_DEVICE_LABEL`. Cumple el estándar OWASP: el token de Ubidots no se quema en el código fuente, sino que se inyecta por entorno protegiendo el repositorio en GitHub.

> **Guion verbal ante el profesor:**
> *"En `.env.example` desacoplamos la configuración sensible. En las líneas 24 a 26 definimos `UBIDOTS_TOKEN`. Así, el código de Python lee el token mediante `os.environ.get()` y protegemos las credenciales sin comprometerlas en Git."*

---

### 0.5 Archivo `APIRestFlask/apirest.py` — Arquitectura de la API REST en Memoria

* **Acción en pantalla:** Abrir el archivo [APIRestFlask/apirest.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py).
* **Líneas a señalar en el archivo y explicar:**
  1. **[Líneas 24–37](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py#L24-L37):** Lista `books` en memoria.
  2. **[Línea 58](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py#L58):** `jsonify()` serializando las estructuras nativas a JSON (RFC 8259).
  3. **[Líneas 78–81](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py#L78-L81):** `abort(404)` ante IDs inexistentes.
  4. **[Línea 100](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py#L100):** `request.get_json(silent=True)` para validar cargas útiles y evitar excepciones `415`.
  5. **[Línea 106](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py#L106):** `new_id = books[-1]['id'] + 1 if len(books) > 0 else 1`. Protege contra caídas por `IndexError` si la lista está vacía.
  6. **[Línea 117](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py#L117):** Retorno semántico `201 Created` en POST.
  7. **[Línea 210](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py#L210):** Enlace a `host='0.0.0.0'` para admitir tráfico procedente de interfaces externas.

> **Guion verbal ante el profesor:**
> *"En `apirest.py` implementamos el servicio RESTful oficial. En las líneas 44 a 58 tenemos el método GET general con `jsonify()`. En las líneas 61 a 82 el GET individual con 404. En la línea 100 aplicamos `request.get_json(silent=True)` para capturar errores de cliente, y en la línea 106 protegemos la generación del ID autoincremental contemplando listas vacías para evitar un `IndexError`. Finalmente, en la línea 210 escuchamos en `0.0.0.0` para recibir peticiones externas desde Windows."*

---

### 0.6 Archivo `APIRestFlask/apirest_mysql.py` — Persistencia Relacional MySQL

* **Acción en pantalla:** Abrir el archivo [APIRestFlask/apirest_mysql.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest_mysql.py).
* **Líneas a señalar en el archivo y explicar:**
  1. **[Líneas 24–40](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest_mysql.py#L24-L40):** Conexión con `DictCursor` para mantener el mismo contrato JSON hacia el cliente.
  2. **[Líneas 48–52](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest_mysql.py#L48-L52):** Consultas SQL parametrizadas desacoplando la capa de transporte de la de almacenamiento.

> **Guion verbal ante el profesor:**
> *"En `apirest_mysql.py` demostramos que REST desacopla la interfaz del almacenamiento. En las líneas 24 a 40 configuramos la conexión con `DictCursor`. Las operaciones CRUD ejecutan consultas SQL directamente sobre la tabla `books`, pero hacia el cliente el contrato JSON y los códigos HTTP 200 y 201 se mantienen exactamente iguales."*

---

### 0.7 Archivo `UbidotsClient/testUbidots.py` — Cliente IoT y 5 Variables

* **Acción en pantalla:** Abrir el archivo [UbidotsClient/testUbidots.py](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/UbidotsClient/testUbidots.py).
* **Líneas a señalar en el archivo y explicar:**
  1. **[Líneas 49–55](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/UbidotsClient/testUbidots.py#L49-L55):** Declaración de las **5 variables** (`temperature`, `humidity`, `position`, `pressure` y `battery_level`).
  2. **[Líneas 100–106](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/UbidotsClient/testUbidots.py#L100-L106):** Metadatos espaciales en `"context": {"lat": lat, "lng": lng}` para posicionar el marcador en el widget de mapa de Ubidots.
  3. **[Líneas 138–156](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/UbidotsClient/testUbidots.py#L138-L156):** Bucle de reintentos exponencial (hasta 5 intentos ante códigos $\ge 400$).
  4. **[Líneas 171–175](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/UbidotsClient/testUbidots.py#L171-L175):** Soporte de la bandera `--once` para ejecutar ráfagas limpias durante la sustentación.

> **Guion verbal ante el profesor:**
> *"En `testUbidots.py`, entre las líneas 49 y 55 declaramos las 5 variables cumpliendo el Punto 5: añadimos presión barométrica y nivel de batería. En las líneas 100 a 106 empaquetamos el contexto latitud/longitud dentro de la variable position para que Ubidots pinte el marcador en el mapa. Y en las líneas 138 a 156 implementamos una política de hasta 5 reintentos automáticos para mitigar caídas de conexión."*

---

## FASE 1: Demostración Operativa Parte 1 (API REST Flask, cURL y Postman)

### 1.1 Consulta General (GET /books)

* **Dónde ejecutar:** `[TERMINAL 1: WINDOWS POWERSHELL]` o `[TERMINAL 2: GUEST UBUNTU]`
* **Comando:**
  ```powershell
  # En Windows PowerShell:
  curl.exe -i http://localhost:5000/books

  # O en Ubuntu SSH:
  curl -i -s http://localhost:5000/books
  ```
* **Salida en consola:** `HTTP/1.1 200 OK` con el arreglo de libros `id: 1` y `id: 2`.
* **Líneas del código que sustentan este paso:** [apirest.py Líneas 44–58](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py#L44-L58).
* **Guion corto:** *"Ejecutamos `GET /books`. La función `get_books()` en las líneas 44-58 responde con código 200 OK y entrega la colección completa en formato JSON."*

---

### 1.2 Creación de Recurso (POST /books)

* **Dónde ejecutar:** `[TERMINAL 1: WINDOWS POWERSHELL]` o `[TERMINAL 2: GUEST UBUNTU]`
* **Comandos según la terminal:**
  ```powershell
  # Opción A: En Windows PowerShell usando operador stop-parsing (--% para preservar comillas JSON):
  curl.exe --% -i -H "Content-Type: application/json" -X POST -d "{\"title\":\"El libro\"}" http://localhost:5000/books

  # Opción B: En Windows PowerShell mediante cmdlet nativo:
  Invoke-RestMethod -Uri "http://localhost:5000/books" -Method Post -ContentType "application/json" -Body '{"title":"El libro"}'

  # Opción C: En Ubuntu SSH (Terminal 2 en la VM):
  curl -i -H "Content-Type: application/json" -X POST -d '{"title":"El libro"}' http://localhost:5000/books
  ```
* **Salida en consola:** `HTTP/1.1 201 CREATED` con `{"book": {"id": 3, "title": "El libro", ...}}`.
* **Líneas del código que sustentan este paso:** [apirest.py Líneas 85–117](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py#L85-L117).
* **Guion corto:** *"Ejecutamos el POST. En la línea 106 calcula el ID 3 y en la línea 117 retorna el código semántico 201 Created confirmando la creación."*

---

### 1.3 Modificación (PUT /books/2) y Eliminación (DELETE /books/1)

* **Dónde ejecutar:** `[TERMINAL 1: WINDOWS POWERSHELL]` o `[TERMINAL 2: GUEST UBUNTU]`
* **Comandos:**
  ```powershell
  # 1. Modificar autor en Windows PowerShell:
  curl.exe --% -i -H "Content-Type: application/json" -X PUT -d "{\"author\":\"Jorgito\"}" http://localhost:5000/books/2
  # (O con Invoke-RestMethod: Invoke-RestMethod -Uri "http://localhost:5000/books/2" -Method Put -ContentType "application/json" -Body '{"author":"Jorgito"}')
  # (O en Ubuntu SSH: curl -i -H "Content-Type: application/json" -X PUT -d '{"author":"Jorgito"}' http://localhost:5000/books/2)

  # 2. Eliminar libro 1:
  curl.exe -i -X DELETE http://localhost:5000/books/1

  # 3. Comprobar 404 Not Found:
  curl.exe -i http://localhost:5000/books/1
  ```
* **Salidas:** `HTTP/1.1 200 OK` en el PUT (autor actualizado a 'Jorgito'), `200 OK` en el DELETE (`result: true`), y `HTTP/1.1 404 NOT FOUND` al consultar el libro eliminado.
* **Líneas del código que sustentan este paso:** [apirest.py Líneas 120–176](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py#L120-L176) y manejador de error 404 en [Líneas 188–192](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/APIRestFlask/apirest.py#L188-L192).
* **Guion corto:** *"Modificamos el autor con PUT recibiendo 200 OK, eliminamos el libro 1 con DELETE y al intentar consultarlo de nuevo, la función abort(404) de la línea 81 emite el código de error 404 Not Found."*

---

### 1.4 Pruebas en Postman (Ejercicio 1.b)

* **Dónde ejecutar:** `[VENTANA 4: APLICACIÓN POSTMAN EN WINDOWS]`
* **Preparación previa:** Hacer clic en el botón **Import** de Postman y arrastrar el archivo preconfigurado [config/Practica7_Postman_Collection.json](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/Practica7_Postman_Collection.json).
* **Acción en pantalla:** Abrir la carpeta `Parte 1: API REST Flask (Local)` y ejecutar la petición `1.3 POST - Crear nuevo libro (Cien años de soledad)` hacia `http://localhost:5000/books`.
* **Resultado en pantalla:** Estado `201 Created` en ~14 ms y cuerpo devuelto con `id: 4` (o consecutivo correspondiente).
* **Guion corto:** *"En Postman importamos la colección oficial de la práctica con todos los métodos CRUD listos. Al ejecutar la petición POST con 'Cien años de soledad', el servidor WSGI atiende la solicitud en ~14 ms y responde 201 Created."*

---

### 1.5 Verificación de la Base de Datos MySQL

* **Dónde ejecutar:** `[TERMINAL 2: GUEST UBUNTU (SSH servidorRest)]`
* **Comando:**
  ```bash
  mysql -u flaskuser -pflaskpassword -e "USE myflaskapp; SELECT * FROM books;"
  ```
* **Líneas del código que sustentan este paso:** [schema.sql Líneas 16–31](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/config/schema.sql#L16-L31).
* **Guion corto:** *"Consultamos la consola de MySQL demostrando que la base de datos myflaskapp almacena físicamente los registros de la tabla books, integrando los conceptos de la guía de SQL."*

---

## FASE 2: Demostración Operativa Parte 2 (Cliente IoT, Ubidots y cURL/Postman)

### 2.1 Envío de Telemetría desde Python (testUbidots.py)

* **Dónde ejecutar:** `[TERMINAL 1: WINDOWS POWERSHELL]` o `[TERMINAL 2: GUEST UBUNTU (SSH)]`
* **Comando:**
  ```powershell
  # En Windows PowerShell:
  python "d:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Practica7\UbidotsClient\testUbidots.py" --once

  # O en Ubuntu SSH:
  python3 /home/vagrant/UbidotsClient/testUbidots.py --once
  ```
* **Salida:** `[INFO] Request made properly (HTTP 200), device 'machine' is updated.`
* **Líneas que sustentan este paso:** [testUbidots.py Líneas 57–110](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/UbidotsClient/testUbidots.py#L57-L110).
* **Guion corto:** *"Ejecutamos `testUbidots.py --once`. Construye el payload con las 5 variables y las envía con HTTP POST al endpoint de Ubidots, recibiendo código 200 de actualización exitosa."*

---

### 2.2 Actualización Manual con cURL hacia Ubidots (Punto 3 de la Guía)

* **Dónde ejecutar:** `[TERMINAL 1: WINDOWS POWERSHELL]`
* **Comandos:**
  ```powershell
  # Método A: Cabecera X-Auth-Token (En Windows PowerShell usando --% para preservar comillas JSON):
  curl.exe --% -i -H "Content-Type: application/json" -H "X-Auth-Token: BBUS-qZdFGWNPNLOvb8S9q0yqAo4Bk4GLPs" -X POST -d "{\"temperature\": 13}" http://industrial.api.ubidots.com/api/v1.6/devices/machine

  # Método B: Parámetro en la URL (?token=...) (En Windows PowerShell):
  curl.exe --% -i -H "Content-Type: application/json" -X POST -d "{\"temperature\": 50}" "http://industrial.api.ubidots.com/api/v1.6/devices/machine/?token=BBUS-qZdFGWNPNLOvb8S9q0yqAo4Bk4GLPs"

  # (O en la terminal SSH de Ubuntu en la VM):
  # curl -i -H "Content-Type: application/json" -H "X-Auth-Token: BBUS-qZdFGWNPNLOvb8S9q0yqAo4Bk4GLPs" -X POST -d '{"temperature": 13}' http://industrial.api.ubidots.com/api/v1.6/devices/machine
  ```
* **Salida:** `HTTP/1.1 200 OK` con `[{"status_code": 201}]`.
* **Guion corto:** *"Actualizamos la temperatura manualmente con cURL mediante la cabecera X-Auth-Token y por parámetro en la URL, comprobando que Ubidots acepta ambas sintaxis."*

---

### 2.3 Actualización con Postman hacia Ubidots (Punto 4 de la Guía)

* **Dónde ejecutar:** `[VENTANA 4: APLICACIÓN POSTMAN EN WINDOWS]`
* **Acción:** Petición POST a `http://industrial.api.ubidots.com/api/v1.6/devices/machine` con cabecera `X-Auth-Token` y cuerpo con las 4 variables numéricas.
* **Resultado en pantalla:** Estado `200 OK` en 182 ms.
* **Guion corto:** *"Desde Postman transmitimos un paquete JSON multivariable al endpoint de Ubidots recibiendo código 200 OK en 182 ms."*

---

## FASE 3: Demostración del Dashboard en Tiempo Real y Evento por Correo

### 3.1 Dashboard Multivariable con 5 Widgets (Punto 6 de la Guía)

* **Dónde mostrar:** `[VENTANA 4: NAVEGADOR WEB EN WINDOWS]`
* **URL:** `https://industrial.ubidots.com` o `https://stem.ubidots.com` (o captura [images/10_parte2_ubidots_dashboard_5_variables.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/images/10_parte2_ubidots_dashboard_5_variables.png)).
* **Componentes a señalar en pantalla:**
  1. **Humidity:** Widget **Gauge / Indicador** marcando 62 %.
  2. **Position:** Widget de **Mapa Geográfico** ubicando al dispositivo con sus coordenadas GPS (`35.124, -84.215`).
  3. **Temperature:** Widget de **Diagrama de Barras** con la línea guía del umbral en 40 °C.
  4. **Pressure:** Widget de **Gráfico de Líneas** para la oscilación en hPa.
  5. **Battery Level:** Widget de **Tanque Vertical** indicando 94 % de batería.
* **Guion corto:** *"En el Dashboard de Ubidots diseñamos los 5 widgets exigidos: Gauge para humedad, Mapa con el contexto GPS, Barras para temperatura, Gráfico de líneas para presión y Tanque para batería, todos actualizándose en tiempo real."*

---

### 3.2 Evento y Alerta Recibida en el Correo Institucional (Punto 7 de la Guía)

* **Dónde mostrar:** `[VENTANA 4: BANDEJA DE ENTRADA CORREO UAO]`
* **Acción:** Mostrar la pestaña con la alerta recibida o la captura [images/11_parte2_ubidots_evento_correo.png](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/images/11_parte2_ubidots_evento_correo.png).
* **Elementos a señalar:**
  * Regla en Ubidots: `temperature > 40 °C` $\rightarrow$ Enviar correo a `eduard.criollo@uao.edu.co`.
  * Correo recibido: Asunto `[UBIDOTS ALERT] High temperature trigger on machine` informando la lectura crítica de 45.0 °C.
* **Guion corto:** *"Configuramos la regla de evento para que si la temperatura supera los 40 °C, Ubidots despache una alerta. En pantalla se observa la regla activa y el correo de notificación recibido en mi cuenta institucional."*

---

## FASE 4: Preguntas Frecuentes del Evaluador

* **¿Por qué REST debe ser 'Stateless' (sin estado)?**
  * *Respuesta:* Porque al no guardar contexto de sesión en el servidor, cada solicitud es autónoma. Esto permite escalar horizontalmente agregando nodos detrás de un balanceador sin sincronizar memorias de sesión.
* **¿Cuál es la diferencia técnica entre PUT y POST?**
  * *Respuesta:* `POST` no es idempotente y se usa para crear nuevos recursos bajo una colección asignándoles un ID nuevo. `PUT` es idempotente y se utiliza para actualizar o reemplazar un recurso existente en una URI conocida; repetirlo produce siempre el mismo resultado.
* **¿Por qué JSON es superior a XML en aplicaciones IoT?**
  * *Respuesta:* Porque JSON tiene soporte nativo de tipos de datos, es más ligero en peso de trama de red y se deserializa directamente a diccionarios en Python sin la sobrecarga de procesadores DOM o SAX.
* **¿Por qué implementaron la API como servicio systemd?**
  * *Respuesta:* Para asegurar alta disponibilidad y persistencia ante desconexiones de terminal SSH o reinicios del sistema operativo mediante las directivas `Restart=always` y `WantedBy=multi-user.target`.

---

## FASE 5: Plan de Contingencia Audiovisual (Video y Script de Respaldo)

En caso de fallos de red, lentitud del hipervisor o bloqueos técnicos durante la clase:

1. **Video Demostrativo Pregrabado:**

   * **Archivo:** [video/sustentacion_practica7.mp4](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/video/sustentacion_practica7.mp4) (Resolución 720p, 24 FPS).
   * **Uso:** Abrir el video y narrar la presentación siguiendo el guion de cada escena mientras se reproducen las pantallas.
2. **Script de Demostración Automatizado:**

   * **Archivo:** [scripts/demo_sustentacion.ps1](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica7/scripts/demo_sustentacion.ps1).
   * **Dónde ejecutar:** `[TERMINAL 1: WINDOWS POWERSHELL]`
   * **Comando:**
     ```powershell
     cd d:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Practica7
     .\scripts\demo_sustentacion.ps1
     ```
   * Recorre todas las pruebas en consola con pausas limpias de 3 segundos para grabar o presentar en vivo.
