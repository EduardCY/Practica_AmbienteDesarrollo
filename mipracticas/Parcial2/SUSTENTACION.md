# Protocolo y Guía de Sustentación Oral — Segundo Parcial (Servicios Telemáticos)

**Materia:** Servicios Telemáticos (Sistemas Operativos y Redes)  
**Evaluador:** Prof. Oscar Mondragón  
**Estudiante:** Eduard Criollo Yule (`2220335`)  
**Tiempo Total Disponible:** **20 minutos estricto** (~1 minuto por punto evaluable)  
**Calificación Objetivo:** 5.0 / 5.0 (100% de cumplimiento)

---

## Cronograma Táctico de Sustentación (20 Minutos)

| Bloque Temporal | Sección / Puntos | Foco Principal | Minutos |
| :---: | :--- | :--- | :---: |
| **00:00 - 02:00** | **Capítulo 0:** Apertura & Pre-Vuelo | Demostrar clúster activo y pasar suite `15 OK / 0 FAIL`. | 2 min |
| **02:00 - 09:00** | **Capítulo 1:** FTPS & Seguridad UFW (Pts 1-9) | Aislamiento, UFW/NAT, vsftpd, FileZilla + huella, Wireshark plano vs cifrado. | 7 min |
| **09:00 - 14:00** | **Capítulo 2:** DNS sobre TLS (Pts 10-14) | DoT estricto, resolvectl `+DNSOverTLS`, Wireshark 853 vs 53, simulación bloqueo. | 5 min |
| **14:00 - 19:00** | **Capítulo 3:** SFTP Seguro & Chroot (Pts 15-19) | Usuario enjaulado, shell denegado, UFW 2222, Wireshark multiplexado, tabla FTPS vs SFTP. | 5 min |
| **19:00 - 20:00** | **Capítulo 4:** Conclusión y Cierre | Preguntas finales del evaluador y cierre formal. | 1 min |

---

## Convención Operativa de Terminales de Trabajo

| Identificador | Terminal / Entorno | Comando de Acceso | IP / Rol en la Arquitectura |
| :---: | :--- | :--- | :--- |
| 🖥️ **T1** | **Terminal 1 (`srv1`)** | `vagrant ssh srv1` | `192.168.100.3` / `192.168.50.3` — Bastión, UFW, NAT/DNAT |
| 🖧 **T2** | **Terminal 2 (`srv2`)** | `vagrant ssh srv2` | `192.168.50.2` (Aislado) — vsftpd (FTPS), OpenSSH (SFTP chroot) |
| 💻 **T3** | **Terminal 3 (`cli`)** | `vagrant ssh cli` | `192.168.100.10` — Cliente de pruebas DoT, lftp, sftp, tshark |
| 🪟 **T4** | **Host Windows** | PowerShell nativo | `192.168.100.1` (`Ethernet 4`) — FileZilla GUI, Wireshark GUI |

---

## Capítulo 0: Preparación Previa y Protocolo de Apertura

### 0.1 Comprobación Pre-Vuelo Inmediata

> **Terminal a utilizar:** 🪟 **Terminal 4 (Host Windows PowerShell)**  
> **Objetivo:** Demostrar al evaluador que las 3 VMs están operativas y que los 15 controles automatizados pasan al 100%.

```powershell
vagrant status
vagrant ssh cli -c "bash /vagrant/scripts/verify/cli_checks.sh"
```
- **Salida esperada:** Las tres máquinas en estado `running` y `Resultado: 15 OK / 0 FAIL`.

---

## Capítulo 1: Primera Parte — Servicio FTPS y Seguridad Perimetral UFW (2.0 Puntos)

### Punto 1: Servidor 1 como Único Punto de Entrada (0.3 Pts)

#### Paso 1.1: Inspección de Políticas en el Firewall
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Comprobar que el reenvío IP esté activo y que UFW bloquee por defecto todo tráfico enrutado (`deny routed`).

```bash
sudo ufw status verbose
sysctl net.ipv4.ip_forward
```
- **Salida esperada:** `Default: deny (incoming), allow (outgoing), deny (routed)` y `net.ipv4.ip_forward = 1`.
- 💡 **Explicación sencilla:**
  * El Servidor 1 es como el **portero de un edificio**. La regla `deny (routed)` significa que nadie puede pasar al interior del edificio a menos que el portero tenga una orden escrita explícita para dejarlo cruzar.
  * `net.ipv4.ip_forward = 1` es como darle permiso al portero de abrir la puerta trasera que da al patio interior (`srv2`). Si esto estuviera en 0, aunque el portero quisiera pasar el paquete, el sistema operativo Linux se lo prohibiría.

#### Paso 1.2: Intento de Acceso Directo desde el Cliente (Debe Fallar)
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que el cliente no tiene alcance directo de capa 2/3 hacia la IP interna de `srv2`.

```bash
nc -zv -w 3 192.168.50.2 21
nc -zv -w 3 192.168.50.2 22
```
- **Salida esperada:** `timed out` en ambos intentos.
- 💡 **Explicación sencilla:**
  * La IP `192.168.50.2` pertenece a una red privada cerrada dentro de VirtualBox. El cliente `cli` está en otra red (`192.168.100.x`) y no tiene cable ni camino directo hacia ella.
  * Es como intentar llamar por interfono a un apartamento sin marcar antes por la portería: nadie responde y la llamada se cae por tiempo de espera (`timed out`).

#### Paso 1.3: Prueba desde el Host Físico de Windows (Debe Fallar)
> **Terminal a utilizar:** 🪟 **Terminal 4 (Host Windows PowerShell)**  
> **Objetivo:** Comprobar que el aislamiento de `srv2` aplica también para el computador físico real del estudiante.

```powershell
Test-NetConnection 192.168.50.2 -Port 21
```
- **Salida esperada:** `TcpTestSucceeded : False`.
- 💡 **Explicación sencilla:**
  * Esto demuestra que ni siquiera tu propio computador físico con Windows puede tocar al Servidor 2 directamente. El Servidor 2 está completamente escondido y protegido detrás del Servidor 1.

---

### Punto 2: Política Restrictiva por Defecto y Puertos Locales (0.2 Pts)

#### Paso 2.1: Comprobación de Reglas de Entrada y Reenvío
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Verificar que el único puerto local abierto en `srv1` sea el 22/tcp (SSH) y que los servicios hacia `srv2` se manejen vía `ALLOW FWD`.

```bash
sudo ufw status numbered
```
- **Salida esperada:** Regla 1 `22/tcp ALLOW IN` (administración local), y reglas `ALLOW FWD` para `21/tcp`, `50000:50010/tcp` y `22/tcp` dirigidas a `192.168.50.2`.
- 💡 **Explicación sencilla:**
  * `ALLOW IN` significa "servicios que atiende el propio Servidor 1" (solo el puerto 22 para que nosotros podamos administrarlo por consola).
  * `ALLOW FWD` significa "tráfico que el Servidor 1 no atiende él mismo, sino que lo deja pasar hacia el Servidor 2". Así separamos la seguridad del router de los servicios que están detrás.

#### Paso 2.2: Escaneo de Puertos No Autorizados
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que puertos no autorizados (ej. HTTP 80) están bloqueados por la política deny.

```bash
nc -zv -w 3 192.168.100.3 80
```
- **Salida esperada:** `nc: connect to 192.168.100.3 port 80 (tcp) timed out`.
- 💡 **Explicación sencilla:**
  * Si intentamos tocar cualquier puerta que no hayamos autorizado (como el puerto web 80), el firewall simplemente ignora el mensaje y no contesta nada. Aplica el principio de seguridad de **mínimo privilegio**: todo lo que no esté explícitamente permitido, está prohibido.

---

### Punto 3: Control de Acceso Perimetral (ufw allow vs ufw route allow) (0.3 Pts)

#### Paso 3.1: Eliminar Regla de Reenvío en Servidor 1
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Deshabilitar el paso del tráfico FORWARD hacia el puerto 21 de `srv2` para simular denegación perimetral.

```bash
sudo ufw route delete allow proto tcp from any to 192.168.50.2 port 21
```
- **Salida esperada:** `Rule updated`.
- 💡 **Explicación sencilla:**
  * Aquí le quitamos el permiso al portero de dejar pasar gente al puerto 21 de `srv2`.

#### Paso 3.2: Constatar Bloqueo en el Cliente
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que el tráfico hacia `192.168.100.3:21` queda bloqueado por la política `deny (routed)` en la cadena FORWARD.

```bash
nc -zv -w 3 192.168.100.3 21
```
- **Salida esperada:** `Connection timed out`.
- 💡 **Explicación sencilla:**
  * Como el portero ya no tiene la orden de dejar pasar, tira los paquetes a la basura. El cliente se queda esperando respuesta hasta que se rinde (`timed out`).

#### Paso 3.3: Restaurar la Regla de Reenvío
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Restablecer el reenvío mediante `ufw route allow` (diferenciándolo de `ufw allow` que aplica a INPUT).

```bash
sudo ufw route allow proto tcp from any to 192.168.50.2 port 21 comment 'FTPS control -> srv2'
```
- **Salida esperada:** `Rule added`.
- 💡 **Explicación de diferencia clave:**
  * `ufw allow`: Se usa cuando el servicio corre **en el mismo servidor** (cadena INPUT).
  * `ufw route allow`: Se usa cuando el paquete va **de paso hacia otra máquina** (cadena FORWARD). Es la forma correcta y moderna de configurar firewalls enrutadores en Ubuntu.

#### Paso 3.4: Constatar Conectividad Inmediata
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Verificar que el acceso al servicio FTPS se restaura inmediatamente tras aplicar la regla.

```bash
nc -zv -w 3 192.168.100.3 21
```
- **Salida esperada:** `Connection to 192.168.100.3 21 port [tcp/ftp] succeeded!`.

---

### Punto 4: Reglas NAT y Contadores iptables (0.2 Pts)

#### Paso 4.1: Mostrar Bloque NAT en before.rules y Explicar Cada Regla
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Inspeccionar el bloque `*nat` y justificar la función de cada directiva de traducción.

```bash
sudo sed -n '/^\*nat/,/^COMMIT/p' /etc/ufw/before.rules
```
- **Salida esperada:**
  ```text
  *nat
  :PREROUTING ACCEPT [0:0]
  :POSTROUTING ACCEPT [0:0]
  -A PREROUTING -d 192.168.100.3 -p tcp --dport 21 -j DNAT --to-destination 192.168.50.2:21
  -A PREROUTING -d 192.168.100.3 -p tcp --dport 50000:50010 -j DNAT --to-destination 192.168.50.2
  -A PREROUTING -d 192.168.100.3 -p tcp --dport 2222 -j DNAT --to-destination 192.168.50.2:22
  -A POSTROUTING -d 192.168.50.2 -p tcp --dport 21 -j MASQUERADE
  -A POSTROUTING -d 192.168.50.2 -p tcp --dport 50000:50010 -j MASQUERADE
  -A POSTROUTING -d 192.168.50.2 -p tcp --dport 22 -j MASQUERADE
  COMMIT
  ```
- 💡 **Explicación sencilla (por qué se hizo y qué significa cada regla):**
  * `-d 192.168.100.3`: Le dice al firewall: *"Solo traduce los paquetes dirigidos a mi IP pública"*. De esta forma, el tráfico local del propio Servidor 1 no se confunde ni se altera.
  * `DNAT --dport 21`: **Canal de control FTPS**. Cuando un cliente toca la puerta 21 del Servidor 1 pidiendo FTP, el Servidor 1 le cambia el destinatario al sobre y se lo entrega en privado al Servidor 2 (`192.168.50.2:21`).
  * `DNAT --dport 50000:50010`: **Canal de datos pasivo**. En FTP, para listar carpetas o transferir archivos se abre una segunda conexión en puertos altos. Estos 11 puertos son los canales autorizados para transferir los datos.
  * `DNAT --dport 2222`: Publica el servicio SFTP en el puerto 2222 externo para no chocar con el puerto 22 de administración de `srv1`, y lo reenvía al puerto 22 de `srv2`.
  * `POSTROUTING MASQUERADE`: **Regla salvavidas contra ruta asimétrica**. Si no estuviera, el Servidor 2 vería que le escribió el cliente e intentaría responderle por su salida a internet común (la red NAT de Vagrant). Saldría por una puerta diferente a la que entró y la conexión se rompería. Con MASQUERADE, el Servidor 1 le dice al Servidor 2: *"Respóndeme a mí, que yo me encargo de entregárselo al cliente"*. Así la conversación nunca se corta.

#### Paso 4.2: Inspeccionar Contadores de Paquetes en iptables
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Constatar en tiempo real los contadores de paquetes y bytes de las cadenas PREROUTING y POSTROUTING.

```bash
sudo iptables -t nat -L -n -v
```
- **Salida esperada:** Tablas PREROUTING y POSTROUTING con contadores de paquetes activos (> 0), demostrando que el tráfico atraviesa las reglas NAT.
- 💡 **Explicación sencilla:** Los números que aumentan en las columnas `pkts` (paquetes) y `bytes` son la prueba viva de que los datos están pasando por nuestras reglas de traducción.

---

### Punto 5: Configuración de vsftpd para FTPS Explícito (0.2 Pts)

#### Paso 5.1: Inspeccionar y Explicar Parámetros TLS en el Servidor
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Mostrar `/etc/vsftpd.conf` y explicar por qué se eligió cada parámetro criptográfico.

```bash
grep -E '^(ssl_|force_|rsa_|userlist_)' /etc/vsftpd.conf
```
- **Salida esperada:**
  ```text
  userlist_enable=YES
  userlist_file=/etc/vsftpd.userlist
  userlist_deny=NO
  ssl_enable=YES
  force_local_logins_ssl=YES
  force_local_data_ssl=YES
  ssl_tlsv1=YES
  ssl_ciphers=HIGH
  rsa_cert_file=/etc/ssl/certs/servidor.crt
  rsa_private_key_file=/etc/ssl/private/servidor.key
  ```
- 💡 **Explicación sencilla (por qué se hizo y qué significa cada parámetro):**
  * `userlist_enable=YES` y `userlist_deny=NO`: Es una **lista de invitados VIP**. Solo quien esté explícitamente anotado en el archivo `/etc/vsftpd.userlist` (`ftp_2220335`) tiene permiso de entrar. Los demás usuarios del sistema (como `vagrant`) son rechazados de inmediato con error 530, ni siquiera se molesta en mirar si su contraseña es correcta.
  * `ssl_enable=YES`: Prende el motor de encriptación para soportar FTPS explícito con el comando `AUTH TLS`.
  * `force_local_logins_ssl=YES` y `force_local_data_ssl=YES`: **Cifrado obligatorio**. El servidor le exige al cliente encriptar tanto la contraseña como los archivos. Si el cliente intenta hablar en texto plano sin cifrar, el servidor le cuelga la llamada.
  * `ssl_tlsv1=YES` (con SSLv2 y SSLv3 en NO): Apaga versiones viejas e inseguras de SSL de los años 90 que tienen fallos conocidos como POODLE o DROWN.

#### Paso 5.2: Verificación de Permisos de Clave y Cadena Criptográfica
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Confirmar permisos restrictivos de la clave privada (0600) y validez del certificado X.509 firmado por la CA del curso.

```bash
sudo ls -l /etc/ssl/private/servidor.key
openssl verify -CAfile /vagrant/certs/ca.crt /etc/ssl/certs/servidor.crt
```
- **Salida esperada:** Permisos `-rw------- 1 root root` y `/etc/ssl/certs/servidor.crt: OK`.

---

### Punto 6: Configuración del Modo Pasivo tras NAT (0.2 Pts)

#### Paso 6.1: Inspección de Parámetros Pasivos en vsftpd
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Explicar la necesidad de `pasv_address` y el rango delimitado de puertos.

```bash
grep -E '^pasv_' /etc/vsftpd.conf
```
- **Salida esperada:**
  ```ini
  pasv_enable=YES
  pasv_min_port=50000
  pasv_max_port=50010
  pasv_address=192.168.100.3
  pasv_addr_resolve=NO
  ```
- 💡 **Explicación sencilla:**
  * En FTP pasivo, cuando el cliente pide ver archivos, el servidor le responde: *"Listo, conéctate a esta IP y a este puerto para pasarte los datos"*.
  * Como el Servidor 2 está escondido en la red interna (`192.168.50.2`), si no le ponemos `pasv_address`, le diría al cliente: *"Conéctate a 192.168.50.2"*. Pero el cliente está afuera y no tiene cómo llegar a esa IP privada.
  * Con `pasv_address=192.168.100.3`, obligamos al Servidor 2 a decirle al cliente la verdad útil: *"Conéctate a la IP pública del Servidor 1 (192.168.100.3), que él me pasa los paquetes"*.
  * Delimitamos los puertos de 50000 a 50010 para solo tener que abrir 11 puertos en el firewall, en lugar de abrir miles de puertos inseguros al azar.

---

### Punto 7: Pruebas en FileZilla: Fallos Controlados vs Éxito y Huella SHA-256 (0.2 Pts)

#### Paso 7.1: Consultar Huella Criptográfica en el Servidor
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Extraer la huella SHA-256 oficial del certificado X.509 de `srv2` para contrastarla en FileZilla.

```bash
openssl x509 -in /etc/ssl/certs/servidor.crt -noout -fingerprint -sha256
```
- **Salida esperada:** `SHA256 Fingerprint=88:3D:11:C7:C4:F5:D6:7F:2B:37:69:9D:9A:86:3C:62:7A:6E:1B:15:23:0B:3E:B0:81:4A:6F:41:BF:0A:B8:3D`.

#### Paso 7.2: Prueba de Fallo 1 — Conexión a la IP Interna `192.168.50.3` (Debe Fallar)
> **Terminal a utilizar:** 🪟 **Terminal 4 (Host Windows — FileZilla GUI)**  
> **Objetivo:** Demostrar que el cliente externo no puede conectarse directamente a la subred interna `192.168.50.0/24`.

1. **Datos en FileZilla (Conexión rápida o Gestor de sitios):**
   * **Servidor:** `192.168.50.3` | **Usuario:** `ftp_2220335` | **Contraseña:** `Ftps2220335!` | **Puerto:** `21`
2. **Hacer clic en "Conexión rápida".**
- **Salida esperada en el log de FileZilla:**
  ```text
  Estado: Conectando a 192.168.50.3:21...
  Error: Conexión superó el tiempo de espera después de 20 segundos de inactividad
  Error: No se pudo conectar al servidor
  ```
- 💡 **Explicación sencilla del fallo:** La red `192.168.50.0/24` es una red privada interna que solo existe adentro de VirtualBox. Windows no tiene ninguna tarjeta de red en esa subred. Es como intentar marcar a una extensión telefónica desconectada: la señal se pierde en el vacío y se produce un tiempo de espera agotado (**Timeout**).

#### Paso 7.3: Prueba de Fallo 2 — Conexión con Usuario No Autorizado (`vagrant` / `vagrant`) (Debe Fallar)
> **Terminal a utilizar:** 🪟 **Terminal 4 (Host Windows — FileZilla GUI)**  
> **Objetivo:** Demostrar que la lista blanca protege al sistema rechazando cuentas no autorizadas aunque existan en Linux.

1. **Datos en FileZilla:**
   * **Servidor:** `192.168.100.3` | **Usuario:** `vagrant` | **Contraseña:** `vagrant` | **Puerto:** `21`
2. **Hacer clic en "Conexión rápida" (o Aceptar).**
- **Salida esperada en el log de FileZilla:**
  ```text
  Estado: Conectando a 192.168.100.3:21...
  Respuesta: 220 (vsFTPd 3.0.5)
  Comando: AUTH TLS
  Respuesta: 234 Using authentication type TLS
  Estado: Inicializando TLS...
  Estado: Conexión TLS establecida.
  Comando: USER vagrant
  Respuesta: 530 Permission denied.
  Error: Error crítico: No se pudo conectar al servidor
  ```
- 💡 **Explicación sencilla del fallo:** El usuario `vagrant` sí existe en el sistema operativo Linux con clave `vagrant`, pero en `vsftpd.conf` configuramos una **lista blanca VIP** (`userlist_deny=NO`). Como `vagrant` no está en la lista de invitados (`/etc/vsftpd.userlist`), el servidor le dice de inmediato `530 Permission denied` y le cierra la puerta en la cara sin siquiera verificar su contraseña.

#### Paso 7.4: Prueba de Éxito — Conexión Legítima FTPS, Validación de Huella y Transferencia
> **Terminal a utilizar:** 🪟 **Terminal 4 (Host Windows — FileZilla GUI)**  
> **Objetivo:** Conectarse exitosamente con el usuario autorizado, validar el certificado y transferir archivos.

1. **Configuración en Gestor de Sitios (`Ctrl + S`):**
   * **Servidor:** `192.168.100.3` | **Puerto:** `21`
   * **Cifrado:** `Requiere FTP explícito sobre TLS`
   * **Usuario:** `ftp_2220335` | **Contraseña:** `Ftps2220335!`
   * **Ajustes de transferencia:** `Pasivo`
2. **Validación visual de la Alerta de Certificado:**
   * FileZilla saca una ventana diciendo: *"El certificado del servidor no es conocido"*.
   * Mostrarle al evaluador que la **Huella digital SHA-256** es idéntica a la que consultamos en la terminal del Servidor 2 (`88:3D:11:...`).
   * Marcar la casilla *"Confiar siempre en este certificado"* y pulsar **Aceptar**.
3. **Transferencia de Archivos:**
   * Arrastrar o hacer doble clic en `2220335.txt` para subirlo al servidor y descargarlo de vuelta.
- **Salida esperada:** Conexión exitosa, listado de carpetas obtenido por los puertos 50000..50010 y mensaje verde `Transferencia satisfactoria`.
- 💡 **Explicación sencilla:** Con esto demostramos las 3 cosas clave: entramos con el usuario correcto, confirmamos que el certificado es auténtico comparando su huella digital, y transferimos archivos con total cifrado.

---

### Punto 8: Conexión openssl s_client y Cadena de Confianza CA (0.2 Pts)

#### Paso 8.1: Validación de Cadena de Confianza por Terminal
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Validar por consola que la negociación STARTTLS resuelva la cadena completa hasta la CA raíz institucional con código 0.

```bash
openssl s_client -connect 192.168.100.3:21 -starttls ftp -CAfile ~/ca.crt </dev/null | grep -E '(depth|New,|Verify return|Server certificate)'
```
- **Salida esperada:**
```text
depth=1 CN = CA Servicios Telematicos 2220335
depth=0 CN = srv2-2220335
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Verify return code: 0 (ok)
```
- 💡 **Explicación sencilla:**
  * `depth=1`: Es el emisor o "padre" (nuestra Autoridad Certificadora CA).
  * `depth=0`: Es el servidor o "hijo" (el certificado del Servidor 2).
  * `Verify return code: 0 (ok)`: Significa que el certificado es 100% auténtico y encaja a la perfección con la firma de la CA. Cero advertencias y máxima seguridad bajo TLS 1.3.

---

### Punto 9: Capturas Wireshark: FTP Plano vs FTPS Cifrado (0.2 Pts)

> [!IMPORTANT]
> **Interfaz a capturar en Wireshark:** Seleccionar **`Ethernet 4`** en Windows (asociada a la IP `192.168.100.1`) o capturar directamente en `cli` sobre **`eth1`**.

#### Paso 9.1: Demostración FTP en Texto Plano (Peligro de Intercepción)
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)** + 💻 **Terminal 3 (`cli`)** + 🪟 **Wireshark GUI (`Ethernet 4`)**  
> **Objetivo:** Demostrar cómo en FTP clásico cualquier persona en la red puede espiar y robar contraseñas.

1. En 🖧 `srv2`: Apagar el cifrado con `sudo bash /vagrant/scripts/demo/ftps_tls.sh off`
2. En 🪟 Wireshark: Iniciar captura en `Ethernet 4` con filtro `ftp || ftp-data` (o ejecutar en 💻 `cli`: `sudo tshark -i eth1 -f "host 192.168.100.3" -w /vagrant/captures/p09_ftp_plano.pcapng -c 40 &`).
3. En 💻 `cli`:
   ```bash
   lftp -e "set ftp:ssl-allow no; put /home/vagrant/2220335.txt; ls; bye" -u ftp_2220335,Ftps2220335! 192.168.100.3
   ```
4. En 🪟 Wireshark: Clic derecho sobre paquete `USER` → **Follow → TCP Stream**.
- **Salida esperada:** Usuario `ftp_2220335` y contraseña `Ftps2220335!` visibles en texto claro sin cifrar.
- 💡 **Explicación sencilla:** En FTP plano, los datos viajan como una postal abierta. Cualquiera conectado al mismo Wi-Fi o router puede leer tu clave sin ningún esfuerzo.

#### Paso 9.2: Demostración FTPS Cifrado (Seguridad TLS 1.3)
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)** + 💻 **Terminal 3 (`cli`)** + 🪟 **Wireshark GUI (`Ethernet 4`)**  
> **Objetivo:** Evidenciar la total confidencialidad e ininteligibilidad del tráfico bajo TLS 1.3.

1. En 🖧 `srv2`: Reactivar el cifrado con `sudo bash /vagrant/scripts/demo/ftps_tls.sh on`
2. En 🪟 Wireshark: Iniciar nueva captura en `Ethernet 4` con filtro `tcp.port == 21 || tcp.port in {50000..50010} || tls`.
3. En 💻 `cli`:
   ```bash
   lftp -e "put /home/vagrant/2220335.txt; ls; bye" -u ftp_2220335,Ftps2220335! 192.168.100.3
   ```
4. En 🪟 Wireshark: Observar comando inicial `AUTH TLS`, respuesta `234`, transición a `TLSv1.3` y registros `Application Data`.
- **Salida esperada:** Follow TCP Stream en `Application Data` muestra únicamente bytes binarios cifrados. Credenciales y archivos protegidos con AES-256-GCM.
- 💡 **Explicación sencilla:** Gracias a TLS 1.3 con AES-256, los datos están encriptados con matemáticas avanzadas. Incluso teniendo el paquete completo capturado en Wireshark, nadie puede saber qué usuario se conectó ni qué contenía el archivo.

---

### Modificaciones en Vivo y FAQs de la Parte 1

| Petición Docente | Terminal | Procedimiento Rápido | Verificación |
| :--- | :---: | :--- | :--- |
| **Cambiar rango pasivo a 50020:50030** | 🖧 `srv2` + 🖥️ `srv1` | En `srv2`: editar `vsftpd.conf` y `sudo systemctl restart vsftpd`. En `srv1`: actualizar `before.rules` y `ufw reload`. | Transferir archivo en `cli` comprobando puerto efímero en 5002X. |
| **Simular fallo de `pasv_address`** | 🖧 `srv2` | `sudo sed -i 's/^pasv_address/#pasv_address/' /etc/vsftpd.conf && sudo systemctl restart vsftpd` | `lftp` hace login pero el listado da timeout anunciando IP privada. |

---

## Capítulo 2: Segunda Parte — Resolución DNS Segura sobre TLS (DoT) (1.5 Puntos)

### Punto 10: Configuración de systemd-resolved y Modo Estricto (0.3 Pts)

#### Paso 10.1: Inspección y Explicación de resolved.conf en el Cliente
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Mostrar `/etc/systemd/resolved.conf` y explicar por qué se configuró cada directiva.

```bash
grep -vE '^\s*(#|$)' /etc/systemd/resolved.conf
```
- **Salida esperada:**
  ```ini
  [Resolve]
  DNS=1.1.1.1#cloudflare-dns.com 1.0.0.1#cloudflare-dns.com 8.8.8.8#dns.google
  FallbackDNS=9.9.9.9#dns.quad9.net 8.8.4.4#dns.google
  Domains=~.
  DNSOverTLS=yes
  DNSSEC=no
  MulticastDNS=no
  LLMNR=no
  Cache=yes
  DNSStubListener=yes
  ```
- 💡 **Explicación sencilla (por qué se hizo y qué significa cada parámetro):**
  * `DNS=1.1.1.1#cloudflare-dns.com`: La parte `#cloudflare-dns.com` le dice al cliente: *"Verifica que el certificado de seguridad pertenezca legítimamente a Cloudflare"*. Si alguien en la red intenta suplantar el servidor, el cliente detecta el engaño y no se conecta.
  * `Domains=~.`: La tilde y el punto (`~.`) es una regla que significa: *"Cualquier dominio del planeta debe consultarse obligatoriamente por este canal cifrado"*. Evita que las consultas se escapen por los servidores DNS no seguros que entrega el router de la casa o de la universidad por DHCP.
  * `DNSOverTLS=yes`: Es el **modo estricto**. Significa: *"O viaja 100% cifrado por el puerto 853, o no viaja nada"*. Si alguien intenta forzar una conexión insegura, el sistema prefiere dar error antes que regalar nuestra privacidad.
  * `DNSStubListener=yes`: Crea un intermediario local en la IP `127.0.0.53:53` para que los programas comunes de Linux (`ping`, `curl`, navegadores) puedan consultar normalmente sin saber nada de TLS; `systemd-resolved` se encarga de recibir la consulta y meterla en el túnel seguro DoT.

#### Paso 10.2: Verificación del Stub Local
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Confirmar que `/etc/resolv.conf` apunte al stub resolver seguro de systemd (`127.0.0.53`).

```bash
ls -l /etc/resolv.conf
grep nameserver /etc/resolv.conf
```
- **Salida esperada:** Enlace a `stub-resolv.conf` y `nameserver 127.0.0.53`.

---

### Punto 11: Comprobación del Protocolo Activo +DNSOverTLS (0.2 Pts)

#### Paso 11.1: Consultar Estado de Enlaces y Protocolos
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Verificar mediante `resolvectl status` que el indicador de protocolo `+DNSOverTLS` esté activo a nivel global.

```bash
resolvectl status | grep -E '(Protocols|\+DNSOverTLS|Current DNS)'
```
- **Salida esperada:** `Protocols: -LLMNR -mDNS +DNSOverTLS DNSSEC=no/unsupported`.

---

### Punto 12: Demostración de Resolución de Dominios (0.2 Pts)

#### Paso 12.1: Consultas Resolviendo por DoT
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Comprobar la resolución exitosa de dominios vía DoT estricto.

```bash
resolvectl query uao.edu.co google.com wikipedia.org
```
- **Salida esperada:** Respuestas IP resueltas con `Data was acquired via local or encrypted transport: yes`.

#### Paso 12.2: Demostración con dig Estándar vs dig Forzando Servidor Externo
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Evidenciar que `dig` estándar utiliza el stub local seguro (`127.0.0.53`), mientras que forzar `@8.8.8.8` viaja en texto plano por UDP 53.

```bash
dig wikipedia.org | grep 'SERVER:'
dig @8.8.8.8 wikipedia.org | grep 'SERVER:'
```
- **Salida esperada:** `SERVER: 127.0.0.53#53` (resuelto por DoT) vs `SERVER: 8.8.8.8#53` (texto plano no cifrado).

---

### Punto 13: Capturas Wireshark: Puerto 853/tcp vs Puerto 53/udp (0.5 Pts)

#### Demostración Práctica en Wireshark
> **Terminal a utilizar:** 🪟 **Wireshark GUI (`captures/`)** o consola en 💻 `cli`  
> **Objetivo:** Demostrar que en DoT el contenido de la consulta permanece completamente oculto bajo registros TLS, a diferencia de DNS tradicional.

1. **DoT Cifrado (`captures/p13_dot_853.pcapng` — Filtro: `tcp.port == 853`):**
   * **Interfaz de captura:** `eth0` de `cli` (salida externa a internet) o abrir captura guardada.
   * **Secuencia observada en Wireshark:**
     - Handshake TCP de 3 vías con la IP de Cloudflare (`1.1.1.1:853`).
     - `Client Hello` anunciando extensiones TLS y SNI `cloudflare-dns.com`.
     - `Server Hello` estableciendo TLS 1.3 con clave efímera.
     - Registros `Application Data`: la consulta sobre `uao.edu.co` y sus respuestas de tipo A/AAAA viajan 100% cifradas e indescifrables.
2. **DNS Convencional en Texto Claro (`captures/p13_dns_53.pcapng` — Filtro: `udp.port == 53`):**
   * Al ejecutar `dig @8.8.8.8 uao.edu.co`, se observa el paquete UDP `Standard query 0x... A uao.edu.co` legible en texto plano absoluto. Cualquier atacante o proveedor de internet puede registrar las consultas y realizar ataques de spoofing/envenenamiento de caché.
- **Salida esperada:** Contraste claro entre confidencialidad total en 853/tcp vs vulnerabilidad de intercepción en 53/udp.
- 💡 **Explicación sencilla:**
  * En **853/tcp (DoT)**, los paquetes viajan cifrados bajo TLS 1.3. La consulta de `uao.edu.co` está completamente oculta; un espía en la red solo ve que te conectas a Cloudflare, pero no tiene idea de qué página buscas.
  * En **53/udp (DNS clásico)**, el paquete grita en texto plano `Standard query A uao.edu.co`. Cualquier operador de internet, vecino en la red o atacante puede registrar tus hábitos de navegación o falsificar la respuesta.

---

### Punto 14: Simulación de Bloqueo de DoT y Resistencia Anti-Downgrade (0.3 Pts)

#### Paso 14.1: Bloquear Puerto 853 en Firewall Local
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Simular un bloqueo perimetral o censura del puerto 853/tcp para evaluar el comportamiento del resolver.

```bash
sudo iptables -I OUTPUT -p tcp --dport 853 -j REJECT
```
- **Salida esperada:** Regla de rechazo insertada en la cadena OUTPUT de `cli`.

#### Paso 14.2: Comprobar Resistencia a la Degradación en Modo Estricto (`yes`)
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que con `DNSOverTLS=yes` la resolución se bloquea deliberadamente para impedir degradaciones hacia texto claro (*anti-downgrade*).

```bash
resolvectl query uao.edu.co
```
- **Salida esperada:**
  ```text
  uao.edu.co: resolve call failed: All synthetically created DNS servers failed.
  ```
- 💡 **Explicación sencilla del fallo:** Al bloquear el puerto 853 con iptables, `systemd-resolved` se da cuenta de que no puede negociar el túnel cifrado. Como configuramos `DNSOverTLS=yes` (modo estricto), el sistema se rehúsa a bajar la guardia: **prefiere fallar y quedarse sin internet antes que enviar tu consulta en texto plano desprotegido**. Esto nos protege contra atacantes que bloquean el puerto 853 a propósito para obligarnos a usar DNS tradicional y espiarnos.

#### Paso 14.3: Comprobar Caída a Texto Claro en Modo Oportunista (`opportunistic`)
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que el modo `opportunistic` sacrifica la privacidad cayendo a texto plano por UDP 53 cuando el puerto 853 está bloqueado.

```bash
sudo bash /vagrant/scripts/demo/dot_mode.sh opportunistic
resolvectl query uao.edu.co
```
- **Salida esperada:** Resuelve exitosamente entregando las IPs, pero la consulta viaja en **texto claro no cifrado** por el puerto 53 UDP, confirmando la vulnerabilidad del modo oportunista.
- 💡 **Explicación sencilla:** En modo oportunista el sistema es complaciente: si el candado falla, se rinde y envía la consulta en texto claro por UDP 53. La página carga, pero la privacidad del usuario quedó totalmente expuesta.

#### Paso 14.4: Restaurar Estado Operativo Estricto
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Eliminar la regla de bloqueo de iptables y reactivar el modo DoT estricto.

```bash
sudo iptables -D OUTPUT -p tcp --dport 853 -j REJECT
sudo bash /vagrant/scripts/demo/dot_mode.sh yes
resolvectl query uao.edu.co
```
- **Salida esperada:** `DNSOverTLS=yes` reactivado y resolución restaurada satisfactoriamente por DoT cifrado.

---

### Modificaciones en Vivo y FAQs de la Parte 2

| Petición Docente | Terminal | Procedimiento Rápido | Verificación |
| :--- | :---: | :--- | :--- |
| **Cambiar resolver a Quad9** | 💻 `cli` | En `/etc/systemd/resolved.conf`: `DNS=9.9.9.9#dns.quad9.net` y `sudo systemctl restart systemd-resolved`. | `resolvectl status` muestra Quad9 como servidor activo. |
| **Introducir SNI erróneo** | 💻 `cli` | Colocar `DNS=1.1.1.1#servidor-falso.com` con `DNSOverTLS=yes` y reiniciar. | Resolución falla por discrepancia en validación de certificado TLS. |

---

## Capítulo 3: Tercera Parte — Transferencia SFTP Segura Protegida por UFW (1.5 Puntos)

### Punto 15: Usuario Dedicado, Jaula Chroot y Rechazo de Shell (0.4 Pts)

#### Paso 15.1: Inspección de sshd_config y Explicación de Directivas
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Comprobar el bloque `Match User` en `/etc/ssh/sshd_config` y justificar la arquitectura de confinamiento.

```bash
sudo sed -n '/^Match User sftp_2220335/,$p' /etc/ssh/sshd_config
```
- **Salida esperada:**
  ```ini
  Match User sftp_2220335
      ChrootDirectory /home/sftp_2220335
      ForceCommand internal-sftp
      PasswordAuthentication yes
      AllowTcpForwarding no
      AllowAgentForwarding no
      PermitTunnel no
      X11Forwarding no
      PermitTTY no
  ```
- 💡 **Explicación sencilla (por qué se hizo y qué significa cada parámetro):**
  * `Subsystem sftp internal-sftp`: Usa el motor interno de OpenSSH. La gran ventaja es que corre dentro del mismo proceso y **no necesita copiar binarios ni librerías dentro de la jaula**. Si usáramos el sftp-server viejo, nos tocaría copiar `/bin/sh` y media instalación de Linux dentro de la carpeta del usuario.
  * `ChrootDirectory /home/sftp_2220335`: Es el **enjaulamiento estricto**. Hace que para ese usuario su carpeta personal sea la raíz (`/`) de todo el planeta. No puede salir a curiosear archivos del sistema (`/etc/passwd`, `/var/log`, etc.).
  * `ForceCommand internal-sftp` y `PermitTTY no`: **Le apaga la terminal de comandos**. El usuario solo tiene permiso de mover archivos; no puede ejecutar comandos ni actuar como administrador en el sistema.
  * `PasswordAuthentication yes` (solo en este bloque): Permite que este usuario entre con contraseña, mientras que el resto del servidor solo acepta llaves SSH por máxima seguridad.

#### Paso 15.2: Verificación de Permisos Estrictos de la Jaula
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Verificar que la raíz del chroot cumpla con los requisitos innegociables de propiedad de OpenSSH (`root:root`).

```bash
ls -ld /home/sftp_2220335 /home/sftp_2220335/archivos
```
- **Salida esperada:**
  ```text
  drwxr-xr-x 3 root         root         4096 ... /home/sftp_2220335
  drwxr-xr-x 2 sftp_2220335 sftp_2220335 4096 ... /home/sftp_2220335/archivos
  ```
- 💡 **Explicación sencilla de seguridad:**
  * OpenSSH tiene una regla de oro estricta: **el dueño de la jaula debe ser `root:root` con permisos 755**. Si el usuario fuera el dueño de su propia jaula, podría cambiarle los permisos, crear accesos directos maliciosos y escapar de la celda.
  * Por eso, para que el usuario pueda guardar cosas sin romper la seguridad, le creamos la subcarpeta `archivos/`, donde él sí es dueño y tiene permiso total de escritura.

#### Paso 15.3: Prueba de Fallo Controlada — Intento de Shell Interactivo SSH (Debe Ser Rechazado)
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que el usuario SFTP no puede abrir terminal interactiva ni ejecutar comandos en el sistema.

```bash
ssh -p 2222 sftp_2220335@192.168.100.3
```
- **Salida esperada:**
  ```text
  sftp_2220335@192.168.100.3's password: (ingresar Sftp2220335!)
  This service allows sftp connections only.
  Connection to 192.168.100.3 closed.
  ```
- 💡 **Explicación sencilla del fallo:** Al intentar entrar por `ssh` interactivo, la directiva `ForceCommand` lo frena en seco diciendo *"Este servicio solo permite conexiones SFTP"* y lo desconecta de inmediato. Demuestra que no hay riesgo de que ejecute comandos en el servidor.

---

### Punto 16: Regla de Reenvío para SFTP en Puerto 2222 (0.3 Pts)

#### Paso 16.1: Mostrar Reglas de Firewall en Servidor 1
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Mostrar cómo se publica el servicio SFTP en el puerto 2222 externo y se enruta al puerto 22 de `srv2`.

```bash
# Regla DNAT en /etc/ufw/before.rules:
grep -E '2222' /etc/ufw/before.rules
# Regla de Filtrado en UFW:
sudo ufw route status | grep 22
```
- **Salida esperada:**
  ```text
  -A PREROUTING -d 192.168.100.3 -p tcp --dport 2222 -j DNAT --to-destination 192.168.50.2:22
  [ 4] 22/tcp ALLOW FWD anywhere to 192.168.50.2 (comment: 'SFTP 2222 -> srv2:22')
  ```

#### Paso 16.2: Prueba de Fallo Controlada — Eliminar Regla de Reenvío UFW
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Deshabilitar temporalmente el paso de tráfico FORWARD hacia el puerto 22 de `srv2`.

```bash
sudo ufw route delete allow proto tcp from any to 192.168.50.2 port 22
```
- **Salida esperada:** `Rule updated`.

#### Paso 16.3: Constatar Bloqueo en el Cliente
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que el firewall bloquea el acceso externo al puerto 2222 al faltar la autorización FORWARD.

```bash
sftp -o ConnectTimeout=3 -P 2222 sftp_2220335@192.168.100.3
```
- **Salida esperada:** `ssh: connect to host 192.168.100.3 port 2222: Connection timed out`.
- 💡 **Explicación sencilla del fallo:** Aunque el router le cambia la dirección al paquete (DNAT), el muro del firewall tiene la orden de no dejar pasar a nadie por defecto (`DROP`). Al borrar la regla de paso (`ufw route`), el firewall tira los paquetes a la basura en silencio y la conexión se muere por tiempo de espera (**Timeout**).

#### Paso 16.4: Restaurar Regla de Reenvío y Constatar Acceso Inmediato
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)** + 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Reactivar el paso de tráfico FORWARD y verificar conectividad instantánea.

```bash
# En srv1:
sudo ufw route allow proto tcp from any to 192.168.50.2 port 22 comment 'SFTP 2222 -> srv2:22'

# En cli:
nc -zv -w 3 192.168.100.3 2222
```
- **Salida esperada en cli:** `Connection to 192.168.100.3 2222 port [tcp] succeeded!`.
- 💡 **Explicación sencilla:** Apenas volvemos a poner la regla en el firewall, el portero abre el paso de inmediato y el puerto 2222 responde al instante.

---

### Punto 17: Conexión SFTP por Terminal y Transferencia de Archivos (0.2 Pts)

#### Paso 17.1: Consultar Huella del Host en el Servidor (Modelo TOFU)
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Obtener la huella Ed25519 oficial del servidor para validar autenticidad en el modelo TOFU (*Trust On First Use*).

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```
- **Salida esperada:** Huella SHA256 Ed25519 de `srv2` (ej. `SHA256:d8/l54QY3c...`).
- 💡 **Explicación sencilla:** SSH utiliza el modelo **TOFU** (*Confía la primera vez*). La primera vez que te conectas, tu cliente guarda la huella digital del servidor en su memoria (`known_hosts`). Si en el futuro un hacker intentara meterse en el medio con otra máquina, el cliente detectará que la huella no coincide y dará una alarma roja de seguridad impidiendo la conexión.

#### Paso 17.2: Iniciar Sesión, Verificar Jaula Chroot y Transferir Archivos
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Interactuar con el subsistema SFTP, confirmar el enjaulamiento en la raíz `/` y realizar subida y descarga de archivos.

```bash
sftp -P 2222 sftp_2220335@192.168.100.3
```
Dentro de la consola interactiva de SFTP:
```text
pwd
cd archivos
put 2220335_sftp.txt
ls -la
get 2220335_sftp.txt 2220335_descargado.txt
bye
```
- **Salida esperada:**
  * `pwd` devuelve `/` (prueba concluyente de que el usuario está dentro de la jaula chroot y no en `/home/sftp_2220335` real).
  * `put`: `Uploading 2220335_sftp.txt to /archivos/2220335_sftp.txt 100% ...`.
  * `get`: `Fetching /archivos/2220335_sftp.txt to 2220335_descargado.txt 100% ...`.
- 💡 **Explicación sencilla:**
  * Al escribir `pwd`, el sistema nos dice `/`. Esta es la prueba reina de que la jaula funciona: el usuario cree que está en el inicio de la máquina, cuando en realidad está encerrado en su carpeta asignada.
  * Los comandos `put` y `get` demuestran que puede subir y descargar archivos con total normalidad dentro de su subcarpeta `archivos/`.

---

### Punto 18: Captura Wireshark de Sesión SFTP Multiplexada (0.3 Pts)

#### Demostración Práctica en Wireshark
> **Terminal a utilizar:** 🪟 **Wireshark GUI (`captures/`)** o captura en vivo en 💻 `cli`  
> **Objetivo:** Demostrar que SFTP opera sobre un único socket TCP (`2222/tcp`) y que el cifrado se negocia antes de transmitir credenciales, sin necesidad de puertos pasivos.

1. **Dónde capturar:**
   * En Host Windows: Seleccionar la interfaz de red host-only (`Ethernet 4`, IP `192.168.100.1`).
   * O en 💻 `cli`: `sudo tshark -i eth1 -f "tcp port 2222" -w /vagrant/captures/p18_sftp_2222.pcapng &`
2. **Filtro de visualización en Wireshark:**
   ```text
   tcp.port == 2222
   ```
3. **Desglose de paquetes a sustentar ante el evaluador:**
   * **Handshake TCP:** Saludo inicial de 3 vías (`SYN`, `SYN-ACK`, `ACK`) hacia el puerto `2222`.
   * **Banner de versión (en claro):** Las máquinas se presentan diciendo `SSH-2.0-OpenSSH_8.9p1`.
   * **Negociación de algoritmos (KEX Init):** Se ponen de acuerdo en qué tipo de candado y cifrado van a usar.
   * **Intercambio Diffie-Hellman / ECDH:** Se pasan claves matemáticas temporales para armar la clave secreta de la sesión.
   * **Activación de Cifrado (`New Keys`):** El paquete que dice: *"A partir de aquí, cerramos el candado"*.
   * **Canal Multiplexado Único:** A partir de `New Keys`, **absolutamente todos los paquetes son `Encrypted packet`**. Las credenciales (`sftp_2220335`), comandos (`ls`, `cd`) y la transferencia de archivos viajan mezclados dentro de **este mismo y único tubo TCP 2222**.
- **Salida esperada:** Demostración visual de que no existe ningún puerto pasivo ni conexiones secundarias efímeras, a diferencia de FTPS.
- 💡 **Explicación sencilla (el gran contraste entre FTPS y SFTP):**
  * **FTPS es engorroso para el firewall:** Requiere un canal para órdenes (puerto 21) y otro canal diferente por cada archivo que se envía (puertos 50000 a 50010). Tuvimos que abrir 12 puertos en el firewall y configurar trucos como `pasv_address`.
  * **SFTP es limpio y superior:** Toda la comunicación (saludo, clave, subida y bajada de archivos) viaja a través de **una sola tubería TCP en el puerto 2222**. Solo abrimos 1 puerto en el firewall, no hay puertos pasivos y no hay enredos de NAT.

---

### Punto 19: Conclusión Técnica y Tabla Comparativa FTPS vs SFTP (0.3 Pts)

#### Tabla Comparativa Oficial para Sustentar

| Dimensión Técnica | FTPS (FTP sobre TLS / RFC 4217) | SFTP (SSH File Transfer Protocol / RFC 4251) |
| :--- | :--- | :--- |
| **Canales TCP** | **2 o más:** Control (`21/tcp`) + datos pasivos (`50000:50010/tcp`). | **1 único socket multiplexado:** Puerto `2222/tcp`. |
| **Autenticación** | Certificados **X.509** dependientes de una CA (PKI). | Claves públicas de host (`ssh_host_*_key`) vía modelo **TOFU**. |
| **Inicio del Cifrado** | Inicia en **texto plano** y se promueve tras `AUTH TLS`. | Cifrado negociado **desde el primer paquete** antes de enviar credenciales. |
| **Complejidad Firewall/NAT** | **Alta:** Requiere abrir rangos pasivos fijos y forzar `pasv_address`. | **Mínima:** Solo requiere reenviar un único puerto TCP (`2222`). |
| **Superficie de Exposición** | **12 puertos abiertos** (21 + 50000:50010). | **1 puerto abierto** (`2222`). |
| **Dictamen Final** | Adecuado si hay clientes legados o requisitos de PKI X.509. | **Solución óptima recomendada para entornos corporativos con firewall estricto.** |

---

### Modificaciones en Vivo y FAQs de la Parte 3

| Petición Docente | Terminal | Procedimiento Rápido | Verificación |
| :--- | :---: | :--- | :--- |
| **Cambiar puerto externo de SFTP a 2200** | 🖥️ `srv1` | En `/etc/ufw/before.rules`: cambiar `--dport 2222` a `--dport 2200` y `sudo ufw reload`. | `sftp -P 2200 ...` conecta exitosamente desde `cli`. |
| **Romper permisos de la jaula (simular fallo)** | 🖧 `srv2` | `sudo chown sftp_2220335 /home/sftp_2220335` | `sftp` rechaza la conexión con `bad ownership for chroot directory`. Restaurar con `chown root:root`. |
| **Bloquear cliente específico por IP** | 🖥️ `srv1` | `sudo ufw route insert 1 deny from 192.168.100.10 to 192.168.50.2` | Conexión desde `cli` da timeout inmediatamente. |

---

## Capítulo 4: Banco Consolidado de Modificaciones en Vivo y Comandos de Inspección

### 4.1 Comandos de Inspección Rápida

#### En Servidor 1 (Firewall / Router)
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Inspeccionar estado de firewall, contadores NAT y logs de tráfico.

```bash
sudo ufw status verbose
sudo iptables -t nat -L -n -v
sudo tail -n 25 /var/log/ufw.log
```
- **Salida esperada:** Estado de políticas, reglas numeradas activas y contadores de paquetes.

#### En Servidor 2 (Servidor Interno)
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Consultar daemons vsftpd/sshd y logs de autenticación.

```bash
systemctl status vsftpd ssh
sudo tail -n 25 /var/log/auth.log
```
- **Salida esperada:** Ambos servicios en estado `active (running)`.

#### En Cliente de Pruebas
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Consultar el estado DoT y suite de verificación end-to-end.

```bash
resolvectl status
bash /vagrant/scripts/verify/cli_checks.sh
```
- **Salida esperada:** Protocolo `+DNSOverTLS` activo y `Resultado: 15 OK / 0 FAIL`.

---

### 4.2 Respuestas Claras a Preguntas Clave del Evaluador (Para Decir en Voz Alta)

1. **¿Por qué fue necesario `net.ipv4.ip_forward=1`?**  
   *UFW es solo el guardia que revisa qué pasa y qué no, pero quien realmente tiene la habilidad de mover paquetes entre dos redes diferentes es el kernel de Linux. Con `ip_forward=1` le damos permiso al sistema operativo de abrir la puerta entre la red pública (`192.168.100.x`) y la red interna (`192.168.50.x`).*

2. **¿Por qué usamos `internal-sftp` y no el binario tradicional `sftp-server`?**  
   *Porque `internal-sftp` vive adentro del propio proceso de OpenSSH en memoria. Si usáramos el binario tradicional, nos tocaría copiar librerías del sistema y programas dentro de la jaula chroot del usuario para que pudiera arrancar. Con `internal-sftp` la jaula queda limpia, segura y sin archivos innecesarios.*

3. **¿Por qué fue necesario MASQUERADE si ya teníamos DNAT?**  
   *Para evitar que el Servidor 2 se confunda de camino (evitar enrutamiento asimétrico). Con MASQUERADE, el Servidor 1 le disfraza el paquete a `srv2` diciéndole: "Respóndeme a mí". Si no estuviera, `srv2` intentaría responderle al cliente por su propia salida de internet común de Vagrant (`eth0`), saldría por una puerta equivocada y la conexión se caería.*

4. **¿Por qué en FTPS vemos dos handshakes TLS en Wireshark y en SFTP solo uno?**  
   *Porque FTPS hereda la arquitectura vieja de FTP que usa dos conexiones TCP separadas: una para dar comandos (puerto 21) y otra para pasar los archivos (puerto pasivo). Cada conexión tiene que negociar su propio candado. En cambio, SFTP es una sola tubería continua (puerto 2222) donde todo viaja multiplexado.*

5. **¿Por qué en Wireshark con TLS 1.3 no podemos ver el certificado del servidor?**  
   *Porque en TLS 1.3 la privacidad aumentó: las dos máquinas primero intercambian llaves matemáticas temporales y a partir de ese instante todo va cifrado, incluyendo el certificado. En TLS 1.2 viejo el certificado viajaba visible para cualquiera.*
