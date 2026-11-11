# Guía de Sustentación Oral en Pantalla — Práctica 11: AWS EC2 (Servidor Apache + API REST Flask)

**Modalidad de Sustentación:** Ejecución manual comando por comando en pantalla compartida, alternando cada explicación breve con su bloque de código individual listo para copiar al portapapeles con un clic.  
**Asignatura:** Ambiente de Desarrollo / Servicios Telemáticos  
**Profesor Evaluador:** Prof. Oscar Mondragón  
**Estudiante:** Eduard Criollo Yule  
**Código:** 2220335  
**Repositorio:** [Practica_AmbienteDesarrollo](https://github.com/CriolloYule/Practica_AmbienteDesarrollo)  
**Directorio de la Práctica:** `mipracticas/Practica11`

---

## MAPA DE TERMINALES Y ENTORNO DE SUSTENTACIÓN

Para una sustentación ordenada, sincronizada y profesional ante el profesor, organice las siguientes ventanas en su escritorio:

```
+----------------------------------------------------------------------------------------------------+
| VENTANA 1: EDITOR VS CODE                   | VENTANA 2: TERMINAL SSH VM1 (Servidor test)          |
| - Muestra archivos de infraestructura y     | - Conectada vía: ssh -i $KEY ubuntu@$VM1_PUB         |
|   código (.gitignore, service, script,      | - Instalación manual de Apache, verificación local,  |
|   app.py, 000-default.conf, index.html)     |   despliegue del API y sockets de red (80, 5000).    |
+---------------------------------------------+------------------------------------------------------+
| VENTANA 3: TERMINAL SSH VM2 (Cliente test)  | VENTANA 4: POWERSHELL HOST (PC Anfitrión Windows)    |
| - Conectada vía: ssh -i $KEY ubuntu@$VM2_PUB| - Punto 4.b: Auditoría con Invoke-RestMethod         |
| - Punto 4.a: Pruebas de fallo inicial de    |   mediante .\scripts\test_api_from_host.ps1          |
|   HTTP e ICMP, y suite test_api_from_vm2.sh.| - Test-NetConnection y curl.exe nativo de Windows.   |
+---------------------------------------------+------------------------------------------------------+
| VENTANA 5: NAVEGADOR WEB (Consola AWS EC2 + http://$VM1_PUB/ + http://$VM1_PUB:5000/api/products)   |
+----------------------------------------------------------------------------------------------------+
```

---

## ÍNDICE DE NAVEGACIÓN Y SECUENCIA DE SUSTENTACIÓN

* [PUESTA A PUNTO PREVIA: Checklist y Parametrización de Sesión](#puesta-a-punto-previa-checklist-y-parametrización-de-sesión)
* [FASE 0: Exposición de Archivos de Infraestructura y Código en VS Code](#fase-0-exposición-de-archivos-de-infraestructura-y-código-en-vs-code)
* [FASE 1: Evidencia en Consola AWS (Instancias en Pareja y Security Group Inicial)](#fase-1-evidencia-en-consola-aws-instancias-en-pareja-y-security-group-inicial)
* [FASE 2: Métodos de Conexión (EC2 Instance Connect en Navegador y SSH en Consola)](#fase-2-métodos-de-conexión-ec2-instance-connect-en-navegador-y-ssh-en-consola)
* [FASE 3: Réplica Exacta de la Guía y Video (Diagnóstico, Apache, Fallas y Reglas HTTP/ICMP)](#fase-3-réplica-exacta-de-la-guía-y-video-diagnóstico-apache-fallas-y-reglas-httpicmp)
* [FASE 4: Despliegue del Microservicio API REST en VM1 (Ejercicio de la Guía)](#fase-4-despliegue-del-microservicio-api-rest-en-vm1-ejercicio-de-la-guía)
* [FASE 5: Demostración del Punto 4.a — Consumo y Auditoría desde VM2 hacia VM1](#fase-5-demostración-del-punto-4a--consumo-y-auditoría-desde-vm2-hacia-vm1)
* [FASE 6: Demostración del Punto 4.b — Consumo desde Dispositivo Externo (Host Windows)](#fase-6-demostración-del-punto-4b--consumo-desde-dispositivo-externo-host-windows)
* [FASE 7: Demostración de Ciclo de Vida y FinOps en AWS Academy](#fase-7-demostración-de-ciclo-de-vida-y-finops-en-aws-academy)
* [FASE 8: Banco Ampliado de Preguntas y Respuestas Técnicas del Docente Evaluador](#fase-8-banco-ampliado-de-preguntas-y-respuestas-técnicas-del-docente-evaluador)

---

## PUESTA A PUNTO PREVIA: Checklist y Parametrización de Sesión

### A. Checklist Pre-Sustentación (Realizar 15 minutos antes de la reunión)

1. **Subir la Práctica 11 a GitHub (Obligatorio para que VM1 descargue el API):**
   * *Ejecutar en PowerShell:*
   ```powershell
   git add mipracticas/Practica11
   git commit -m "feat(practica11): infraestructura IaaS EC2 con Apache, API REST Flask y auditoria automatizada"
   git push origin main
   ```

2. **Iniciar AWS Academy Learner Lab:**
   * Entrar a AWS Academy LMS $\rightarrow$ **AWS Academy Learner Lab** $\rightarrow$ Clic en **"Start Lab"**.
   * Esperar 2 a 3 minutos hasta que el círculo de estado pase a **verde**.
   * Pulsar en **"AWS"** para abrir la consola de administración en una pestaña nueva (región `us-east-1`).

3. **Lanzar las 2 Instancias EC2 en un solo paso (`count=2`):**
   * En EC2 $\rightarrow$ **Launch instances**:
     * Nombre: `test`
     * AMI: `Ubuntu Server 22.04 LTS (HVM)` (64-bit x86).
     * Tipo: `t2.micro`.
     * Par de claves: Crear `test-ssh` en formato `.pem` (se descarga a `Downloads`).
     * Security Group: Crear nuevo grupo (dejar solo la casilla de SSH marcada).
     * En el panel derecho **Number of instances**: Cambiar a **`2`**.
     * Clic en **Launch instance**.
   * En la lista de instancias: Renombrar una como `test-vm1-servidor` y la otra como `test-vm2-cliente`.
   * Copiar sus 4 direcciones IP (pública y privada de VM1, pública y privada de VM2).

---

### B. Parametrización de Variables en PowerShell (Ventana 4)

Ejecute estos comandos individuales en su terminal PowerShell local (Ventana 4) reemplazando con las IPs reales de su sesión para tener todo listo antes de compartir pantalla:

Paso 0.1 — Definir la ruta local hacia la llave privada descargada (`test-ssh.pem`):
```powershell
$KEY = "$HOME\Downloads\test-ssh.pem"
```

Paso 0.2 — Asegurar permisos de lectura exclusivos sobre la clave privada con `icacls` (evita rechazo de OpenSSH en Windows):
```powershell
icacls.exe $KEY /inheritance:r; icacls.exe $KEY /grant:r "$($env:USERNAME):(R)"
```

Paso 0.3 — Asignar la IP pública real provista por AWS para VM1 en esta sesión:
```powershell
$VM1_PUB = "52.91.99.132"
```

Paso 0.4 — Asignar la IP privada real de VM1:
```powershell
$VM1_PRIV = "172.31.16.58"
```

Paso 0.5 — Asignar la IP pública de VM2:
```powershell
$VM2_PUB = "54.221.25.113"
```

Paso 0.6 — Asignar la IP privada de VM2:
```powershell
$VM2_PRIV = "172.31.23.119"
```

---

## FASE 0: Exposición de Archivos de Infraestructura y Código en VS Code

> **Dónde mostrar:** En la **Ventana 1 (VS Code)** abriendo cada archivo en el orden indicado antes de pasar a la consola de AWS.

### 0.1 Exclusión de Secretos en `.gitignore` y Normalización en `.gitattributes`
* **Archivos a abrir:** [mipracticas/Practica11/.gitignore](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica11/.gitignore) y [mipracticas/Practica11/.gitattributes](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica11/.gitattributes).
* **Qué sustentar brevemente:**
  * En `.gitignore`: Exclusión de claves privadas (`*.pem`, `*.ppk`, `*.key`) y credenciales IAM (`credentials`, `*.csv`) para prevenir fugas de acceso a la cuenta de AWS (OWASP A01/A07).
  * En `.gitattributes`: Forzado de saltos de línea LF (`eol=lf`) para scripts shell, evitando incompatibilidades de sintaxis por caracteres CRLF al ejecutar en Ubuntu.

### 0.2 Script de Configuración Desatendida: `provision/install_apache_and_api.sh`
* **Archivo a abrir:** [provision/install_apache_and_api.sh](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica11/provision/install_apache_and_api.sh).
* **Qué sustentar brevemente:**
  * Uso de `set -Eeuo pipefail` y bandera `-o DPkg::Lock::Timeout=120` para evitar bloqueos por `apt-daily`.
  * Detección automática del Apache preinstalado manualmente durante el paso guiado del video.
  * Creación de usuario de sistema `practica11` sin shell, entorno virtual aislado y cronómetro de despliegue inferior a 60 segundos.

### 0.3 Unidad systemd Endurecida y Proxy Inverso Apache
* **Archivos a abrir:** [provision/practica11-api.service](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica11/provision/practica11-api.service) y [provision/000-default.conf](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Practica11/provision/000-default.conf).
* **Qué sustentar brevemente:**
  * En `practica11-api.service`: Uso de `--preload` en Gunicorn para cargar la app en el maestro antes de hacer fork, eliminando condiciones de carrera sobre SQLite. Directivas de sandboxing (`ProtectSystem=full`, `ReadWritePaths=/var/lib/practica11`).
  * En `000-default.conf`: Directiva `ProxyPass /api/ http://127.0.0.1:5000/api/` que unifica el servidor web Apache con el microservicio.

---

## FASE 1: Evidencia en Consola AWS (Instancias en Pareja y Security Group Inicial)

> **Dónde mostrar:** En la **Ventana 5 (Navegador en la consola de AWS EC2)**.

1. **Pantalla de AWS Academy Learner Lab:**
   * Mostrar el indicador en **verde**, el temporizador activo de la sesión de **4 horas** y el presupuesto restante disponible.
2. **Instancias Creadas en un Solo Paso (`Number of instances = 2`):**
   * Mostrar en el panel de **Instances** las dos máquinas (`test-vm1-servidor` y `test-vm2-cliente`) en estado *Running* con comprobaciones *2/2 checks passed*.
   * Señalar las direcciones IPv4 públicas y privadas asignadas en la misma subred de la VPC.
3. **Security Group Inicial (`launch-wizard-1`):**
   * Mostrar que ambas instancias comparten el mismo Security Group.
   * Mostrar en **Inbound rules** que **únicamente** está autorizada la regla de SSH (Puerto TCP 22 con origen `0.0.0.0/0`), sin reglas HTTP ni ICMP en este momento.

---

## FASE 2: Métodos de Conexión (EC2 Instance Connect en Navegador y SSH en Consola)

> **Dónde ejecutar:** En la **Ventana 5 (Navegador)** y luego en las **Ventanas 2 y 3 (Terminales SSH)**.

Paso 2.1 — Demostrar la conexión web vía EC2 Instance Connect (Opción A del video):
* *Sustentación breve:* Seleccionamos `test-vm1-servidor` en la consola de AWS, pulsamos **"Connect"** $\rightarrow$ pestaña **EC2 Instance Connect** $\rightarrow$ **"Connect"**. Se abre la terminal web en el navegador autenticada por API sin requerir el archivo de llave local.

Paso 2.2 — Conectarse a VM1 desde la terminal local usando OpenSSH y la llave privada (Opción B del video):
```powershell
ssh -i $KEY ubuntu@$VM1_PUB
```
*Sustentación breve:* Ingresamos a la primera instancia a través de la terminal de Windows autenticando con la clave `test-ssh.pem` protegida con `icacls`.

Paso 2.3 — Conectarse a VM2 desde una segunda terminal de PowerShell:
```powershell
ssh -i $KEY ubuntu@$VM2_PUB
```
*Sustentación breve:* Abrimos la sesión interactiva hacia la segunda máquina cliente usando el mismo par de claves criptográficas.

---

## FASE 3: Réplica Exacta de la Guía y Video (Diagnóstico, Apache, Fallas y Reglas HTTP/ICMP)

### 3.1 Instalación de Diagnóstico de Red (`net-tools` e `ifconfig`)

Paso 3.1.1 — En VM1 (Terminal 2): Instalar `net-tools` y visualizar la IP privada asignada:
```bash
sudo apt-get update && sudo apt-get install -y net-tools && ifconfig
```
*Sustentación breve:* Mostramos la interfaz de red `eth0` o `ens5` con su dirección IPv4 privada de la VPC.

Paso 3.1.2 — En VM2 (Terminal 3): Instalar `net-tools` e inspeccionar la IP privada de la segunda máquina:
```bash
sudo apt-get update && sudo apt-get install -y net-tools && ifconfig
```
*Sustentación breve:* Comprobamos que ambas máquinas residen en el mismo segmento de red de la VPC.

---

### 3.2 Instalación Manual de Apache2 en VM1 y Prueba Local

Paso 3.2.1 — En VM1 (Terminal 2): Instalar el servidor web Apache:
```bash
sudo apt-get install -y apache2
```
*Sustentación breve:* Instalamos el paquete oficial de Apache2 en la primera máquina virtual.

Paso 3.2.2 — En VM1 (Terminal 2): Probar el servicio web localmente en `localhost`:
```bash
curl -I http://localhost
```
*Sustentación breve:* Apache responde con código `HTTP/1.1 200 OK` en el socket local de la máquina.

---

### 3.3 Demostración de Fallo HTTP y Apertura de Regla en el Security Group

Paso 3.3.1 — En VM2 (Terminal 3): Intentar consumir Apache en VM1 usando su IP privada (falla esperada):
```bash
curl --max-time 5 http://$VM1_PRIV
```
*Sustentación breve:* La petición se agota por timeout (`Operation timed out`). Aunque Apache está corriendo en VM1, el Security Group bloquea el puerto 80.

Paso 3.3.2 — En Windows (Terminal 4 o Navegador): Intentar acceder por la IP pública de VM1 (falla esperada):
```powershell
curl.exe --max-time 5 -I "http://${VM1_PUB}"
```
*Sustentación breve:* La petición externa también falla porque el firewall perimetral de AWS descarta los paquetes TCP SYN.

Paso 3.3.3 — En la consola de AWS (Ventana 5): Agregar la regla para el Puerto 80:
* Ir a **Security Groups** $\rightarrow$ `launch-wizard-1` $\rightarrow$ **Edit inbound rules** $\rightarrow$ **Add rule**:
  * **Type:** `HTTP` (Puerto TCP 80).
  * **Source:** `Anywhere-IPv4` (`0.0.0.0/0`).
  * Hacer clic en **"Save rules"**.

Paso 3.3.4 — En VM2 (Terminal 3): Repetir la petición HTTP por IP privada (éxito inmediato):
```bash
curl -s http://$VM1_PRIV | grep -E "<title>|<h1>"
```
*Sustentación breve:* Ahora responde de inmediato entregando el título oficial `Apache2 Ubuntu Default Page`.

Paso 3.3.5 — En Windows (Terminal 4): Comprobar respuesta exitosa por la IP pública:
```powershell
curl.exe -s -I "http://${VM1_PUB}"
```
*Sustentación breve:* Recibimos `HTTP/1.1 200 OK` desde el equipo anfitrión en Windows.

---

### 3.4 Demostración de Fallo de Ping (ICMP) y Apertura de Regla Bidireccional

Paso 3.4.1 — En VM1 (Terminal 2): Probar ping hacia VM2 (falla esperada):
```bash
ping -c 3 -W 2 $VM2_PRIV
```
*Sustentación breve:* Se reporta `100% packet loss` porque el protocolo ICMP no está autorizado en el Security Group.

Paso 3.4.2 — En VM2 (Terminal 3): Probar ping hacia VM1 en sentido inverso (falla esperada):
```bash
ping -c 3 -W 2 $VM1_PRIV
```
*Sustentación breve:* También falla en sentido opuesto con `100% packet loss`.

Paso 3.4.3 — En la consola de AWS (Ventana 5): Agregar la regla para ICMP:
* En `launch-wizard-1` $\rightarrow$ **Edit inbound rules** $\rightarrow$ **Add rule**:
  * **Type:** `All ICMP - IPv4`.
  * **Source:** `Anywhere-IPv4` (`0.0.0.0/0`).
  * Guardar reglas (**Save rules**).

Paso 3.4.4 — En VM1 (Terminal 2): Repetir ping hacia VM2 (éxito inmediato):
```bash
ping -c 3 $VM2_PRIV
```
*Sustentación breve:* Respuesta instantánea con `0% packet loss` y latencia menor a 0.5 ms.

Paso 3.4.5 — En VM2 (Terminal 3): Repetir ping hacia VM1 (éxito inmediato):
```bash
ping -c 3 $VM1_PRIV
```
*Sustentación breve:* Demostramos conectividad bidireccional completa dentro de la nube privada virtual.

---

## FASE 4: Despliegue del Microservicio API REST en VM1 (Ejercicio de la Guía)

Paso 4.1 — En la consola de AWS (Ventana 5): Agregar la regla para el Puerto 5000:
* En `launch-wizard-1` $\rightarrow$ **Edit inbound rules** $\rightarrow$ **Add rule**:
  * **Type:** `Custom TCP` | **Port:** `5000` | **Source:** `Anywhere-IPv4` (`0.0.0.0/0`).
  * Guardar reglas (**Save rules**).

Paso 4.2 — En VM1 (Terminal 2): Ejecutar el aprovisionamiento desatendido de la API REST:
```bash
TMP=$(mktemp -d) && git clone --depth 1 --filter=blob:none --sparse https://github.com/EduardCY/Practica_AmbienteDesarrollo.git "$TMP" && git -C "$TMP" sparse-checkout set mipracticas/Practica11 && sudo bash "$TMP/mipracticas/Practica11/provision/install_apache_and_api.sh"
```
*Sustentación breve:* El script despliega el microservicio Flask, compila el entorno virtual y activa el demonio systemd con Gunicorn `--preload` en menos de 45 segundos.

Paso 4.3 — En VM1 (Terminal 2): Verificar estado activo de los demonios en systemd:
```bash
systemctl is-active apache2 practica11-api.service
```
*Sustentación breve:* Confirmamos que tanto el servidor web como el servidor de aplicaciones están activos.

Paso 4.4 — En VM1 (Terminal 2): Inspeccionar sockets TCP en escucha:
```bash
sudo ss -tulpn | grep -E "apache2|gunicorn"
```
*Sustentación breve:* Evidenciamos Apache en el puerto 80 y los workers de Gunicorn en el puerto 5000.

Paso 4.5 — En VM1 (Terminal 2): Probar el endpoint de salud con metadatos IMDSv2 localmente:
```bash
curl -s http://127.0.0.1:5000/api/health | jq .
```
*Sustentación breve:* La API responde con el ID de instancia y la Zona de Disponibilidad consultados en AWS.

---

## FASE 5: Demostración del Punto 4.a — Consumo y Auditoría desde VM2 hacia VM1

Paso 5.1 — En VM2 (Terminal 3): Descargar la suite de auditoría:
```bash
TMP=$(mktemp -d) && git clone --depth 1 --filter=blob:none --sparse https://github.com/EduardCY/Practica_AmbienteDesarrollo.git "$TMP" && git -C "$TMP" sparse-checkout set mipracticas/Practica11 && cp -r "$TMP/mipracticas/Practica11/scripts" ~/ && chmod +x ~/scripts/*.sh
```
*Sustentación breve:* Obtenemos el script de auditoría en la máquina cliente.

Paso 5.2 — En VM2 (Terminal 3): Ejecutar auditoría contra la IP privada de VM1 en el puerto 5000:
```bash
~/scripts/test_api_from_vm2.sh $VM1_PRIV 5000
```
*Sustentación breve:* Validamos el ciclo CRUD completo (Health-check, GET, POST, PUT, DELETE y verificación de 404) a través de la red privada interna de la VPC con 100% PASS.

Paso 5.3 — En VM2 (Terminal 3): Ejecutar auditoría contra la IP pública de VM1:
```bash
~/scripts/test_api_from_vm2.sh $VM1_PUB 5000
```
*Sustentación breve:* Demostramos que cuando el tráfico se dirige a la IP pública, el paquete transita por el Internet Gateway y es admitido por la regla del Security Group.

Paso 5.4 — En VM2 (Terminal 3): Validar consumo a través del proxy inverso de Apache (Puerto 80):
```bash
~/scripts/test_api_from_vm2.sh $VM1_PRIV 80
```
*Sustentación breve:* Confirmamos que Apache redirige las peticiones bajo `/api/` hacia Gunicorn transparentemente.

---

## FASE 6: Demostración del Punto 4.b — Consumo desde Dispositivo Externo (Host Windows)

Paso 6.1 — En Windows (Terminal 4): Comprobar conectividad TCP al puerto 5000 desde el anfitrión:
```powershell
Test-NetConnection -ComputerName $VM1_PUB -Port 5000
```
*Sustentación breve:* `TcpTestSucceeded : True` certifica que el firewall de AWS autoriza el tráfico entrante desde Internet.

Paso 6.2 — En Windows (Terminal 4): Ejecutar el script automatizado de auditoría en PowerShell:
```powershell
Set-Location "d:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Practica11"; .\scripts\test_api_from_host.ps1 -PublicIp $VM1_PUB -Port 5000
```
*Sustentación breve:* La suite en PowerShell ejecuta las aserciones de creación, modificación y borrado de productos directamente contra la IP pública real de AWS.

Paso 6.3 — En Windows (Terminal 4): Abrir en el navegador la landing page interactiva con IMDSv2:
```powershell
Start-Process "http://${VM1_PUB}/"
```
*Sustentación breve:* Mostramos la interfaz web Glassmorphism con el ID de la instancia de AWS y pulsamos **"Consultar Catálogo"** para realizar una petición AJAX en vivo.

Paso 6.4 — En Windows (Terminal 4): Abrir en el navegador el JSON nativo de productos:
```powershell
Start-Process "http://${VM1_PUB}:5000/api/products"
```
*Sustentación breve:* Visualización directa de los datos en formato JSON desde cualquier cliente web.

---

## FASE 7: Demostración de Ciclo de Vida y FinOps en AWS Academy

Paso 7.1 — Demostrar que al detener (Stop) y reanudar (Start) la instancia, la IP pública cambia:
* En la consola de AWS, seleccionar `test-vm1-servidor` $\rightarrow$ **Instance state** $\rightarrow$ **Stop instance**.
* Explicar al profesor: Al detener la máquina, AWS desasigna la IPv4 pública y libera el cómputo. Al darle **Start instance**, AWS le asignará una IP pública totalmente nueva, comprobando la naturaleza dinámica del direccionamiento IaaS.

Paso 7.2 — Buenas prácticas de cierre de sesión:
* Al concluir la sustentación: Seleccionar ambas máquinas $\rightarrow$ **Instance state** $\rightarrow$ **Terminate instance** para eliminar cómputo y volúmenes EBS.
* En el LMS: Pulsar **"End Lab"** para finalizar la sesión de 4 horas y proteger el crédito de la cuenta.

---

## FASE 8: Banco Ampliado de Preguntas y Respuestas Técnicas del Docente Evaluador

### 1. ¿Cuál es la diferencia fundamental entre el modelo IaaS implementado aquí y un modelo PaaS?
* **Respuesta:** En IaaS (Amazon EC2) nosotros aprovisionamos y controlamos la máquina virtual completa: kernel de Linux, paquetes del sistema operativo, servidores web (Apache), demonios en systemd (Gunicorn) y reglas de red. En PaaS (como Elastic Beanstalk o Heroku), el proveedor abstrae el sistema operativo y el desarrollador solo sube el código, cediendo el control de bajo nivel a cambio de menor administración.

### 2. ¿Por qué en la prueba inicial de Apache el comando `curl` falló si el servicio estaba corriendo activamente en VM1?
* **Respuesta:** Porque el Security Group actúa como un firewall perimetral a nivel de hipervisor (fuera de la máquina virtual). Cuando una petición llega a la tarjeta de red virtual (ENI), el hipervisor evalúa la tabla de reglas de entrada antes de entregar los paquetes TCP SYN al kernel de Linux. Al no existir una regla para el puerto 80, el paquete fue descartado silenciosamente sin que Apache tuviera oportunidad de procesarlo.

### 3. ¿Por qué las pruebas de ping fallaron inicialmente a pesar de que el puerto 22 estaba abierto?
* **Respuesta:** Porque `ping` opera sobre el protocolo ICMP (Internet Control Message Protocol), que es un protocolo de nivel de red (Capa 3 de OSI) que no utiliza puertos TCP ni UDP (Capa 4 de OSI). Por ende, tener abiertos los puertos 22 u 80 no autoriza los mensajes de tipo *Echo Request* / *Echo Reply* de ICMP.

### 4. ¿Qué es y cómo funciona EC2 Instance Connect?
* **Respuesta:** Es un mecanismo de acceso web provisto por AWS que permite conectarse por SSH directamente desde el navegador. Cuando pulsamos "Connect", el plano de control de AWS inyecta una clave pública temporal (vigente durante 60 segundos) en los metadatos de la instancia mediante la API de EC2, permitiendo la autenticación sin que el estudiante deba gestionar manualmente claves en su máquina local.

### 5. ¿Por qué es mandatorio aplicar `icacls` (o `chmod 400`) a la clave privada `test-ssh.pem`?
* **Respuesta:** Porque el protocolo OpenSSH exige que las claves privadas tengan permisos exclusivos de lectura únicamente para el propietario del archivo. Si el archivo hereda permisos abiertos para grupos u otros usuarios del sistema operativo, el cliente SSH asume que la clave está potencialmente comprometida y aborta la conexión con el error *UNPROTECTED PRIVATE KEY FILE*.

### 6. ¿Qué ocurre con la dirección IP pública de una instancia EC2 cuando se hace Stop y luego Start?
* **Respuesta:** La dirección IPv4 pública asignada dinámicamente es liberada y devuelta al pool público común de AWS. Al reanudar la máquina, AWS le asigna una nueva dirección IPv4 pública disponible. Para mantener una dirección fija entre reinicios se requeriría asociar una **Dirección IP Elástica (Elastic IP)**.

### 7. ¿Cuál es la política de costos de AWS para direcciones IPv4 públicas vigente desde 2024?
* **Respuesta:** Desde febrero de 2024, AWS cobra **$0.005 USD por hora** por cada dirección IPv4 pública asignada a un recurso en ejecución (~$3.60 USD al mes por IP), con el fin de desincentivar el consumo indiscriminado del espacio global de direcciones IPv4.

### 8. ¿Qué diferencia existe entre pulsar "End Lab" y pulsar "Reset" en el LMS de AWS Academy?
* **Respuesta:** "End Lab" suspende la sesión activa de 4 horas y detiene las instancias, pero **conserva todos los datos** y volúmenes EBS creados para la siguiente sesión. "Reset" es un reinicio destructivo total: elimina todas las instancias, Security Groups, llaves y volúmenes, restableciendo la cuenta de AWS a su estado inicial en blanco.

### 9. ¿Por qué se utilizó la directiva `--preload` en la unidad systemd de Gunicorn?
* **Respuesta:** Porque cuando Gunicorn arranca sin `--preload`, inicia primero los procesos worker y cada worker ejecuta de forma independiente la inicialización de la aplicación. Al utilizar una base de datos embebida como SQLite, esto causaba una condición de carrera donde múltiples procesos intentaban crear tablas e insertar datos semilla simultáneamente. Con `--preload`, el proceso maestro carga la app y puebla la base de datos de manera atómica antes de crear los workers mediante `fork()`.

### 10. ¿Por qué se utilizó Gunicorn y no el servidor integrado de desarrollo de Flask (`app.run`)?
* **Respuesta:** El servidor integrado de Flask (`Werkzeug`) es de un solo hilo, no maneja concurrencia eficiente, es vulnerable a ataques de denegación de servicio por conexiones lentas (Slowloris) y muestra advertencias explícitas de no usarse en producción. Gunicorn es un servidor WSGI de producción basado en el modelo pre-fork de UNIX, que distribuye las peticiones entre múltiples workers y reinicia procesos si colapsan.

### 11. ¿Por qué Gunicorn debe escuchar en `0.0.0.0:5000` y no en `127.0.0.1:5000`?
* **Respuesta:** `127.0.0.1` es la interfaz de loopback local, lo que limitaría el tráfico exclusivamente a procesos internos de la misma máquina. Al escuchar en `0.0.0.0`, el servicio se enlaza a todas las interfaces IPv4 disponibles, permitiendo recibir paquetes provenientes de la tarjeta de red de la VPC y atender peticiones tanto desde VM2 como desde clientes externos en Internet.

### 12. ¿Qué ventajas aporta integrar un Proxy Inverso con Apache frente a Gunicorn?
* **Respuesta:**
  1. Permite servir la interfaz web y el API bajo un único puerto estándar (80), evitando que firewalls externos bloqueen puertos no estándar como el 5000.
  2. Sirve archivos estáticos (HTML, CSS, JS) con máximo rendimiento en C a través de Apache, descargando de trabajo al intérprete de Python.
  3. Facilita la inyección de cabeceras de seguridad globales (`X-Content-Type-Options`, `X-Frame-Options`) y simplifica la incorporación de certificados SSL/TLS en un único punto.

### 13. ¿Qué es IMDSv2 y por qué es más seguro que IMDSv1 en AWS?
* **Respuesta:** El servicio de metadatos de instancia (en `169.254.169.254`) permite a las máquinas consultar información de su propio entorno. IMDSv1 aceptaba peticiones GET simples sin autenticación, lo que permitía a atacantes explotar vulnerabilidades de tipo SSRF (Server-Side Request Forgery) para extraer tokens de roles IAM. IMDSv2 exige una sesión orientada a conexión iniciada mediante una petición `PUT` con cabecera de expiración que entrega un token temporal obligatorio para cualquier consulta posterior.

### 14. ¿Cómo se migraría esta solución a una arquitectura de base de datos desacoplada en AWS?
* **Respuesta:** Gracias al diseño basado en **12-Factor App**, el microservicio no tiene la base de datos acoplada en el código fuente. Se aprovisionaría una instancia de base de datos gestionada en **Amazon RDS (Multi-AZ)** con MySQL o PostgreSQL, y simplemente se actualizaría la variable de entorno `DATABASE_URL` en la unidad systemd (`practica11-api.service`) sin modificar una sola línea del código de la aplicación.

### 15. ¿Por qué en PowerShell de Windows se utilizó `Invoke-RestMethod` en lugar de `curl.exe`?
* **Respuesta:** En Windows PowerShell 5.1, `curl` es un alias de `Invoke-WebRequest`. Además, al invocar el binario nativo `curl.exe` con cadenas JSON complejas desde la consola de comandos de Windows, el analizador de PowerShell desescapa las comillas dobles internas provocando errores sintácticos 400 en el servidor. `Invoke-RestMethod` utiliza la serialización nativa de objetos de .NET con `ConvertTo-Json`, asegurando un envío de carga útil 100% tipado y sin problemas de escape de caracteres.
