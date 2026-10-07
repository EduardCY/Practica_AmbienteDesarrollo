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

#### Paso 1.2: Intento de Acceso Directo desde el Cliente (Debe Fallar)
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que el cliente no tiene alcance directo de capa 2/3 hacia la IP interna de `srv2`.

```bash
nc -zv -w 3 192.168.50.2 21
nc -zv -w 3 192.168.50.2 22
```
- **Salida esperada:** `timed out` en ambos intentos.

#### Paso 1.3: Prueba desde el Host Físico de Windows (Debe Fallar)
> **Terminal a utilizar:** 🪟 **Terminal 4 (Host Windows PowerShell)**  
> **Objetivo:** Comprobar que el aislamiento de `srv2` aplica también para el host físico.

```powershell
Test-NetConnection 192.168.50.2 -Port 21
```
- **Salida esperada:** `TcpTestSucceeded : False`.

---

### Punto 2: Política Restrictiva por Defecto y Puertos Locales (0.2 Pts)

#### Paso 2.1: Comprobación de Reglas de Entrada y Reenvío
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Verificar que el único puerto local abierto en `srv1` sea el 22/tcp (SSH) y que los servicios hacia `srv2` se manejen vía `ALLOW FWD`.

```bash
sudo ufw status numbered
```
- **Salida esperada:** Regla 1 `22/tcp ALLOW IN` (administración local), y reglas `ALLOW FWD` para `21/tcp`, `50000:50010/tcp` y `22/tcp` dirigidas a `192.168.50.2`.

#### Paso 2.2: Escaneo de Puertos No Autorizados
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que puertos no autorizados (ej. HTTP 80) están bloqueados por la política deny.

```bash
nc -zv -w 3 192.168.100.3 80
```
- **Salida esperada:** `nc: connect to 192.168.100.3 port 80 (tcp) timed out`.

---

### Punto 3: Control de Acceso Perimetral (ufw allow vs ufw route allow) (0.3 Pts)

#### Paso 3.1: Eliminar Regla de Reenvío en Servidor 1
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Deshabilitar el paso del tráfico FORWARD hacia el puerto 21 de `srv2` para simular denegación perimetral.

```bash
sudo ufw route delete allow proto tcp from any to 192.168.50.2 port 21
```
- **Salida esperada:** `Rule updated`.

#### Paso 3.2: Constatar Bloqueo en el Cliente
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que el tráfico hacia `192.168.100.3:21` queda bloqueado por la política `deny (routed)` en la cadena FORWARD.

```bash
nc -zv -w 3 192.168.100.3 21
```
- **Salida esperada:** `Connection timed out`.

#### Paso 3.3: Restaurar la Regla de Reenvío
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Restablecer el reenvío mediante `ufw route allow` (diferenciándolo de `ufw allow` que aplica a INPUT).

```bash
sudo ufw route allow proto tcp from any to 192.168.50.2 port 21 comment 'FTPS control -> srv2'
```
- **Salida esperada:** `Rule added`.

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
- **Explicación técnica de la configuración decidida:**
  * `-d 192.168.100.3`: Solo traduce paquetes dirigidos explícitamente a la IP pública de `srv1`. El tráfico local de `srv1` no es alterado.
  * `DNAT --dport 21`: Reescribe la IP destino al servidor interno `srv2:21` (canal de control FTPS).
  * `DNAT --dport 50000:50010`: Reescribe los puertos pasivos para permitir la transferencia de datos y listados.
  * `POSTROUTING MASQUERADE`: Reescribe la IP origen a `192.168.50.3`. **Por qué es obligatoria:** Si no existiera, `srv2` vería la IP del cliente y respondería por su gateway por defecto (`eth0` NAT de Vagrant), produciendo una ruta asimétrica y la ruptura del handshake TCP. Con MASQUERADE, `srv2` responde siempre hacia `srv1`.

#### Paso 4.2: Inspeccionar Contadores de Paquetes en iptables
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Constatar en tiempo real los contadores de paquetes y bytes de las cadenas PREROUTING y POSTROUTING.

```bash
sudo iptables -t nat -L -n -v
```
- **Salida esperada:** Tablas PREROUTING y POSTROUTING con contadores de paquetes activos (> 0), demostrando que el tráfico atraviesa las reglas NAT.

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
- **Explicación técnica de la configuración decidida:**
  * `userlist_enable=YES` + `userlist_deny=NO`: **Modo Lista Blanca estricta**. Solo los usuarios listados en `/etc/vsftpd.userlist` (`ftp_2220335`) pueden autenticar; usuarios del sistema como `vagrant` son bloqueados por diseño antes de validar contraseñas.
  * `ssl_enable=YES`: Habilita soporte para FTPS explícito mediante `AUTH TLS` en el puerto 21.
  * `force_local_logins_ssl=YES` y `force_local_data_ssl=YES`: **Seguridad obligatoria**. Rechaza transferencias y autenticación en texto claro.
  * `ssl_tlsv1=YES` con SSLv2/SSLv3 deshabilitados: Mitiga vulnerabilidades conocidas (POODLE, DROWN).

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
- **Explicación técnica de la configuración decidida:**
  * `pasv_min_port=50000` y `pasv_max_port=50010`: Delimita el rango pasivo a exactamente 11 puertos para no tener que abrir miles de puertos efímeros en el firewall.
  * `pasv_address=192.168.100.3`: **Directiva crucial tras NAT**. `vsftpd` está en `192.168.50.2`. Si no se define esta directiva, anunciaría en la respuesta `227 Entering Passive Mode` su IP interna privada, a la cual el cliente externo no puede llegar. Al forzar `192.168.100.3`, el cliente sabe que debe enviar los paquetes de datos a la IP pública de `srv1`.

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
- **Explicación técnica del fallo:** La red `192.168.50.0/24` es una red privada interna de VirtualBox (`intnet_parcial2_2220335`). El Host Windows solo pertenece al adaptador `192.168.100.0/24`. Al no tener ruta ni visibilidad de capa 2/3 hacia la red interna, el paquete TCP SYN nunca recibe respuesta y se produce un **Connection timed out**.

#### Paso 7.3: Prueba de Fallo 2 — Conexión con Usuario No Autorizado (`vagrant` / `vagrant`) (Debe Fallar)
> **Terminal a utilizar:** 🪟 **Terminal 4 (Host Windows — FileZilla GUI)**  
> **Objetivo:** Demostrar la efectividad de la lista blanca (`userlist_deny=NO`) rechazando usuarios del sistema.

1. **Datos en FileZilla:**
   * **Servidor:** `192.168.100.3` | **Usuario:** `vagrant` | **Contraseña:** `vagrant` | **Puerto:** `21`
2. **Hacer clic en "Conexión rápida" (o Aceptar).**
- **Salida esperada en el log de FileZilla:**
  ```text
  Estado: Conectando a 192.168.100.3:21...
  Estado: Conexión establecida, esperando el mensaje de bienvenida...
  Respuesta: 220 (vsFTPd 3.0.5)
  Comando: AUTH TLS
  Respuesta: 234 Using authentication type TLS
  Estado: Inicializando TLS...
  Estado: Conexión TLS establecida.
  Comando: USER vagrant
  Respuesta: 530 Permission denied.
  Error: Error crítico: No se pudo conectar al servidor
  ```
- **Explicación técnica del fallo:** En `/etc/vsftpd.conf`, las directivas `userlist_enable=YES` y `userlist_deny=NO` configuran una lista blanca estricta basada en `/etc/vsftpd.userlist`. Como el usuario `vagrant` no está en este archivo, `vsftpd` emite el código de error `530 Permission denied` de inmediato y rechaza la sesión, impidiendo que usuarios del sistema operativo sin autorización accedan al FTP.

#### Paso 7.4: Prueba de Éxito — Conexión Legítima FTPS y Cotejo de Huella
> **Terminal a utilizar:** 🪟 **Terminal 4 (Host Windows — FileZilla GUI)**  
> **Objetivo:** Establecer sesión FTPS explícita, cotejar la huella SHA-256 para mitigar ataques MITM y transferir archivos satisfactoriamente.

1. **Configuración en Gestor de Sitios (`Ctrl + S`):**
   * **Servidor:** `192.168.100.3` | **Puerto:** `21`
   * **Cifrado:** `Requiere FTP explícito sobre TLS`
   * **Usuario:** `ftp_2220335` | **Contraseña:** `Ftps2220335!`
   * **Ajustes de transferencia:** `Pasivo`
2. **Cotejo de Alerta y Validación de Seguridad:**
   * Al conectar, FileZilla muestra la ventana emergente: *"El certificado del servidor no es conocido"*.
   * Cotejar con el evaluador que la **Huella digital SHA-256** coincide exactamente con la salida obtenida en `srv2` (`88:3D:11:...`). Presionar **Aceptar**.
3. **Transferencia de Archivos:**
   * Subir `2220335.txt` al directorio remoto y descargarlo de nuevo como comprobación.
- **Salida esperada:** Log con comandos `AUTH TLS`, `234 Proceed`, `USER ftp_2220335`, `PASS ****`, `PBSZ 0`, `PROT P`, `227 Entering Passive Mode (192,168,100,3,195,80)` y `Transferencia satisfactoria`.

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

---

### Punto 9: Capturas Wireshark: FTP Plano vs FTPS Cifrado (0.2 Pts)

> [!IMPORTANT]
> **Interfaz a capturar en Wireshark:** Seleccionar **`Ethernet 4`** en Windows (asociada a la IP `192.168.100.1`) o capturar directamente en `cli` sobre **`eth1`**.

#### Paso 9.1: Demostración FTP en Texto Plano (Vulnerabilidad)
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)** + 💻 **Terminal 3 (`cli`)** + 🪟 **Wireshark GUI (`Ethernet 4`)**  
> **Objetivo:** Evidenciar la exposición de credenciales y datos en texto plano.

1. En 🖧 `srv2`: `sudo bash /vagrant/scripts/demo/ftps_tls.sh off`
2. En 🪟 Wireshark: Iniciar captura en `Ethernet 4` con filtro `ftp || ftp-data` (o ejecutar en 💻 `cli`: `sudo tshark -i eth1 -f "host 192.168.100.3" -w /vagrant/captures/p09_ftp_plano.pcapng -c 40 &`).
3. En 💻 `cli`:
   ```bash
   lftp -e "set ftp:ssl-allow no; put /home/vagrant/2220335.txt; ls; bye" -u ftp_2220335,Ftps2220335! 192.168.100.3
   ```
4. En 🪟 Wireshark: Clic derecho sobre paquete `USER` → **Follow → TCP Stream**.
- **Salida esperada:** Usuario `ftp_2220335` y contraseña `Ftps2220335!` visibles en texto claro sin cifrar.

#### Paso 9.2: Demostración FTPS Cifrado (Seguridad TLS 1.3)
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)** + 💻 **Terminal 3 (`cli`)** + 🪟 **Wireshark GUI (`Ethernet 4`)**  
> **Objetivo:** Evidenciar la total confidencialidad e ininteligibilidad del tráfico bajo TLS 1.3.

1. En 🖧 `srv2`: `sudo bash /vagrant/scripts/demo/ftps_tls.sh on`
2. En 🪟 Wireshark: Iniciar nueva captura en `Ethernet 4` con filtro `tcp.port == 21 || tcp.port in {50000..50010} || tls`.
3. En 💻 `cli`:
   ```bash
   lftp -e "put /home/vagrant/2220335.txt; ls; bye" -u ftp_2220335,Ftps2220335! 192.168.100.3
   ```
4. En 🪟 Wireshark: Observar comando inicial `AUTH TLS`, respuesta `234`, transición a `TLSv1.3` y registros `Application Data`.
- **Salida esperada:** Follow TCP Stream en `Application Data` muestra únicamente bytes binarios cifrados. Credenciales y archivos protegidos con AES-256-GCM.

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
- **Explicación técnica de la configuración decidida:**
  * `DNS=1.1.1.1#cloudflare-dns.com`: **Sintaxis IP#nombre**. Es indispensable porque el cliente debe enviar la extensión **SNI** (*Server Name Indication*) durante el handshake TLS y cotejar que el certificado presentado por el resolver contenga dicho nombre en el campo *Subject Alternative Name* (SAN), mitigando la suplantación de resolvers.
  * `Domains=~.`: La tilde punto (`~.`) convierte a estos resolvers seguros en la ruta de enrutamiento por defecto para **todos** los dominios (zona raíz), impidiendo que consultas se filtren hacia resolvers no cifrados entregados por DHCP.
  * `DNSOverTLS=yes`: **Modo Estricto**. Fuerza todas las consultas a través de TLS en el puerto 853. Si el canal cifrado no puede establecerse o es bloqueado, la consulta **falla** deliberadamente. Impide ataques de degradación (*anti-downgrade*).
  * `DNSStubListener=yes`: Mantiene el listener local en `127.0.0.53:53` para que aplicaciones estándar del sistema puedan resolver sin cambios, siendo `systemd-resolved` quien encapsula todo en DoT.

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
- **Explicación técnica del fallo:** Al estar configurado `DNSOverTLS=yes` en `/etc/systemd/resolved.conf`, el sistema operativo aplica una política estricta de seguridad: si el túnel TLS en el puerto 853 no puede negociarse, **la consulta se descarta por completo** en lugar de degradar a texto plano por el puerto 53. Esto protege al usuario contra ataques MitM que intenten forzar la comunicación a canales inseguros mediante denegación de servicio en DoT.

#### Paso 14.3: Comprobar Caída a Texto Claro en Modo Oportunista (`opportunistic`)
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que el modo `opportunistic` sacrifica la privacidad cayendo a texto plano por UDP 53 cuando el puerto 853 está bloqueado.

```bash
sudo bash /vagrant/scripts/demo/dot_mode.sh opportunistic
resolvectl query uao.edu.co
```
- **Salida esperada:** Resuelve exitosamente entregando las IPs, pero la consulta viaja en **texto claro no cifrado** por el puerto 53 UDP, confirmando la vulnerabilidad del modo oportunista.

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
- **Explicación técnica de la configuración decidida:**
  * `Subsystem sftp internal-sftp`: Usa el subsistema interno de OpenSSH que corre en el mismo proceso `sshd`. **Por qué es decisivo:** Un subsistema externo como `/usr/lib/openssh/sftp-server` requeriría copiar `/bin/sh`, bibliotecas dinámicas (`libc`) y archivos de configuración dentro de la jaula; `internal-sftp` no requiere ningún binario dentro de la jaula.
  * `ChrootDirectory /home/sftp_2220335`: Confinamiento estricto. El proceso redefine la raíz (`/`) del sistema de archivos para ese usuario, imposibilitando acceder a `/etc`, `/var`, `/home` u otros directorios del sistema.
  * `ForceCommand internal-sftp` + `PermitTTY no`: Anula cualquier intento de abrir una sesión interactiva de shell o ejecutar comandos remotos.
  * `PasswordAuthentication yes` (en bloque Match): Habilita contraseña exclusivamente para el usuario SFTP, mientras que el resto del servidor solo acepta llaves SSH públicas.

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
- **Explicación técnica de seguridad:** OpenSSH exige que el directorio `ChrootDirectory` sea propiedad exclusiva de `root:root` y que ningún otro usuario tenga permisos de escritura (`755`). Si el usuario tuviera permisos de escritura en la raíz de su chroot, podría crear enlaces simbólicos o bibliotecas maliciosas para escapar de la jaula. Por esto, la escritura se delega al subdirectorio `archivos/`.

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
- **Explicación técnica del fallo:** La directiva `ForceCommand internal-sftp` intercepta el inicio de sesión. Al detectar que la solicitud de SSH fue para un shell PTY interactivo y no una sesión SFTP, imprime el mensaje de restricción y termina inmediatamente la conexión TCP, impidiendo cualquier ejecución de comandos en el servidor.

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
- **Explicación técnica del fallo:** Aunque la tabla `*nat` en PREROUTING sigue traduciendo el puerto `2222` a `192.168.50.2:22`, el paquete debe cruzar la cadena `FORWARD` de la tabla `*filter`. Al haberse eliminado la regla de autorización, la política general de UFW (`DEFAULT_FORWARD_POLICY="DROP"`) descarta el paquete silenciosamente, produciendo timeout.

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

---

### Punto 17: Conexión SFTP por Terminal y Transferencia de Archivos (0.2 Pts)

#### Paso 17.1: Consultar Huella del Host en el Servidor (Modelo TOFU)
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Obtener la huella Ed25519 oficial del servidor para validar autenticidad en el modelo TOFU (*Trust On First Use*).

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```
- **Salida esperada:** Huella SHA256 Ed25519 de `srv2` (ej. `SHA256:d8/l54QY3c...`).

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
   * **Handshake TCP:** Tres vías (`SYN`, `SYN-ACK`, `ACK`) hacia el puerto `2222`.
   * **Banner de versión (en claro):** Paquete con texto `SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.x`.
   * **Negociación de algoritmos (KEX Init):** Intercambio de cifradores simétricos (`chacha20-poly1305`, `aes256-gcm`) y funciones de hash.
   * **Intercambio Diffie-Hellman / ECDH:** Paquetes `Elliptic Curve Diffie-Hellman Key Exchange Init/Reply` con Curve25519 donde se transfiere la clave efímera y la clave pública del host.
   * **Activación de Cifrado (`New Keys`):** Paquete de sincronización que indica el inicio inmediato del cifrado simétrico.
   * **Canal Multiplexado Único:** A partir de `New Keys`, **todos los paquetes subsiguientes son `Encrypted packet`**. Las credenciales (`sftp_2220335`), comandos de listado (`ls`) y transferencia binaria de archivos (`put`/`get`) viajan multiplexados sobre **ese mismo socket TCP 2222**.
- **Salida esperada:** Demostración visual de que no existe ningún puerto pasivo ni conexiones secundarias efímeras, a diferencia de FTPS.

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

### 4.2 Respuestas de 10 Segundos a Preguntas Clave del Evaluador

1. **¿Por qué fue necesario `net.ipv4.ip_forward=1`?**  
   *UFW solo filtra paquetes (Netfilter); el reenvío entre interfaces distintas lo realiza el kernel y requiere `ip_forward=1`.*
2. **¿Por qué `internal-sftp` y no el binario `/usr/lib/openssh/sftp-server`?**  
   *En jaulas chroot no existen bibliotecas compartidas ni binarios; `internal-sftp` corre dentro del propio proceso `sshd` sin requerir archivos dentro de la jaula.*
3. **¿Por qué MASQUERADE si ya hay DNAT?**  
   *Evita enrutamiento asimétrico: si `srv2` viera la IP del cliente respondería por su gateway por defecto (NAT Vagrant `eth0`) y el handshake TCP fallaría.*
4. **¿Por qué en FTPS se observan dos handshakes TLS distintos?**  
   *Por la arquitectura de dos canales de FTP: uno protege el canal de control (puerto 21) y otro el canal de datos pasivo (puerto efímero).*
5. **¿Por qué con TLS 1.3 no se ve el certificado en Wireshark?**  
   *En TLS 1.3 el mensaje `Certificate` viaja cifrado tras el `Server Hello` gracias a las claves efímeras derivadas con Diffie-Hellman.*
