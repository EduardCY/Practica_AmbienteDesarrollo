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

#### Paso 4.1: Mostrar Bloque NAT en before.rules
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Inspeccionar las directivas de DNAT (PREROUTING) y MASQUERADE (POSTROUTING) en la configuración persistente.

```bash
sudo sed -n '/^\*nat/,/^COMMIT/p' /etc/ufw/before.rules
```
- **Salida esperada:** Reglas DNAT hacia `192.168.50.2` para puertos 21, 50000:50010 y 2222->22, junto con reglas MASQUERADE para evitar rutas asimétricas.

#### Paso 4.2: Inspeccionar Contadores de Paquetes en iptables
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Constatar en tiempo real los contadores de paquetes y bytes de las cadenas PREROUTING y POSTROUTING.

```bash
sudo iptables -t nat -L -n -v
```
- **Salida esperada:** Tablas PREROUTING y POSTROUTING con contadores de paquetes activos (> 0).

---

### Punto 5: Configuración de vsftpd para FTPS Explícito (0.2 Pts)

#### Paso 5.1: Comprobación de Parámetros TLS en el Servidor
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Verificar que `vsftpd` exija TLS obligatoriamente para autenticación y datos, bloqueando SSLv2/SSLv3.

```bash
grep -E '^(ssl_|force_|rsa_|ssl_ciphers)' /etc/vsftpd.conf
```
- **Salida esperada:** `ssl_enable=YES`, `force_local_logins_ssl=YES`, `force_local_data_ssl=YES`, `ssl_tlsv1=YES`, `ssl_sslv2=NO`, `ssl_sslv3=NO`.

#### Paso 5.2: Verificación de Permisos de Clave y Cadena Criptográfica
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Confirmar que la clave privada tenga permisos restrictivos (0600) y que el certificado esté firmado y validado por la CA.

```bash
sudo ls -l /etc/ssl/private/servidor.key
openssl verify -CAfile /vagrant/certs/ca.crt /etc/ssl/certs/servidor.crt
```
- **Salida esperada:** Permisos `-rw------- 1 root root` en la clave y `/etc/ssl/certs/servidor.crt: OK`.

---

### Punto 6: Configuración del Modo Pasivo tras NAT (0.2 Pts)

#### Paso 6.1: Inspección de Parámetros Pasivos en vsftpd
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Comprobar la delimitación del rango pasivo (50000:50010) y el anuncio forzado de la IP pública (`pasv_address=192.168.100.3`).

```bash
grep -E '^pasv_' /etc/vsftpd.conf
```
- **Salida esperada:**
```ini
pasv_enable=YES
pasv_min_port=50000
pasv_max_port=50010
pasv_address=192.168.100.3
```

---

### Punto 7: Conexión Gráfica con FileZilla y Huella SHA-256 (0.2 Pts)

#### Paso 7.1: Consultar Huella Criptográfica en el Servidor
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Extraer la huella SHA-256 oficial del certificado X.509 para contrastarla en FileZilla.

```bash
openssl x509 -in /etc/ssl/certs/servidor.crt -noout -fingerprint -sha256
```
- **Salida esperada:** `SHA256 Fingerprint=88:3D:11:C7:C4:F5:D6:7F:2B:37:69:9D:9A:86:3C:62:7A:6E:1B:15:23:0B:3E:B0:81:4A:6F:41:BF:0A:B8:3D`.

#### Paso 7.2: Conexión en FileZilla y Cotejo de Certificado
> **Terminal a utilizar:** 🪟 **Terminal 4 (Host Windows — FileZilla GUI)**  
> **Objetivo:** Establecer sesión FTPS explícita, cotejar la huella SHA-256 para mitigar ataques MITM y transferir archivo.

1. **Configuración en Gestor de Sitios (`Ctrl + S`):**
   * **Servidor:** `192.168.100.3` | **Puerto:** `21`
   * **Cifrado:** `Requiere FTP explícito sobre TLS`
   * **Usuario:** `ftp_2220335` | **Contraseña:** `Ftps2220335!`
   * **Ajustes de transferencia:** `Pasivo`
2. **Cotejo de Alerta:**
   * Al conectar, FileZilla muestra ventana: *"Certificado desconocido"*.
   * Cotejar con el docente que la **Huella SHA-256** coincide exactamente con la salida de `srv2`. Presionar **Aceptar**.
3. **Transferencia y Verificación:**
   * Subir `2220335.txt` al directorio remoto y descargarlo como comprobación.
- **Salida esperada:** Log con comandos `AUTH TLS`, `234 Proceed`, `USER`, `PASS`, `PBSZ 0`, `PROT P`, `PASV` (puerto en 50000:50010), y `Transferencia satisfactoria`.

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

#### Paso 10.1: Inspección de Configuración en el Cliente
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Comprobar la parametrización de resolvers con SNI (`IP#nombre`) y la activación del modo estricto `DNSOverTLS=yes`.

```bash
grep -vE '^\s*(#|$)' /etc/systemd/resolved.conf
```
- **Salida esperada:** Servidores `1.1.1.1#cloudflare-dns.com` y `DNSOverTLS=yes`.

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
> **Terminal a utilizar:** 🪟 **Wireshark GUI (`captures/`)**  
> **Objetivo:** Demostrar que en DoT el contenido de la consulta permanece completamente oculto bajo registros TLS, a diferencia de DNS tradicional.

1. **DoT Cifrado (`captures/p13_dot_853.pcapng` — Filtro: `tcp.port == 853`):**
   * Mostrar apretón de manos TLS 1.3 hacia Cloudflare (`853/tcp`) y paquetes `Application Data`. El nombre consultado (`uao.edu.co`) no aparece en el payload.
2. **DNS Convencional (`captures/p13_dns_53.pcapng` — Filtro: `udp.port == 53`):**
   * Mostrar la consulta estándar `Standard query A uao.edu.co` legible en texto plano absoluto.
- **Salida esperada:** Contraste claro entre confidencialidad total en 853/tcp vs vulnerabilidad de intercepción en 53/udp.

---

### Punto 14: Simulación de Bloqueo de DoT y Límites de Privacidad (0.3 Pts)

#### Paso 14.1: Bloquear Puerto 853 en Firewall Local
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Simular un bloqueo perimetral o censura del puerto 853/tcp.

```bash
sudo iptables -I OUTPUT -p tcp --dport 853 -j REJECT
```
- **Salida esperada:** Regla de rechazo insertada en la cadena OUTPUT.

#### Paso 14.2: Comprobar Resistencia a la Degradación en Modo Estricto (`yes`)
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que con `DNSOverTLS=yes` la resolución se bloquea para impedir degradaciones hacia texto claro (*anti-downgrade*).

```bash
resolvectl query uao.edu.co
```
- **Salida esperada:** Fallo de resolución (`resolve call failed`). Demuestra que el sistema rehúsa degradar a texto claro inseguro.

#### Paso 14.3: Comprobar Caída a Texto Claro en Modo Oportunista (`opportunistic`)
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que el modo `opportunistic` cae a texto plano por UDP 53 cuando el puerto 853 está bloqueado.

```bash
sudo bash /vagrant/scripts/demo/dot_mode.sh opportunistic
resolvectl query uao.edu.co
```
- **Salida esperada:** Resuelve exitosamente pero en texto plano inseguro por el puerto 53.

#### Paso 14.4: Restaurar Estado Operativo Estricto
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Eliminar la regla de bloqueo de iptables y reactivar el modo DoT estricto.

```bash
sudo iptables -D OUTPUT -p tcp --dport 853 -j REJECT
sudo bash /vagrant/scripts/demo/dot_mode.sh yes
```
- **Salida esperada:** `DNSOverTLS=yes` reactivado y resolución restaurada por DoT.

---

### Modificaciones en Vivo y FAQs de la Parte 2

| Petición Docente | Terminal | Procedimiento Rápido | Verificación |
| :--- | :---: | :--- | :--- |
| **Cambiar resolver a Quad9** | 💻 `cli` | En `/etc/systemd/resolved.conf`: `DNS=9.9.9.9#dns.quad9.net` y `sudo systemctl restart systemd-resolved`. | `resolvectl status` muestra Quad9 como servidor activo. |
| **Introducir SNI erróneo** | 💻 `cli` | Colocar `DNS=1.1.1.1#servidor-falso.com` con `DNSOverTLS=yes` y reiniciar. | Resolución falla por discrepancia en validación de certificado TLS. |

---

## Capítulo 3: Tercera Parte — Transferencia SFTP Segura Protegida por UFW (1.5 Puntos)

### Punto 15: Usuario Dedicado, Jaula Chroot y Rechazo de Shell (0.4 Pts)

#### Paso 15.1: Inspección de sshd_config en el Servidor
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Comprobar la directiva `Match User` que confina al usuario en chroot y fuerza el subsistema en memoria `internal-sftp`.

```bash
sudo sed -n '/^Match User sftp_2220335/,$p' /etc/ssh/sshd_config
```
- **Salida esperada:** `ChrootDirectory /home/sftp_2220335`, `ForceCommand internal-sftp`, `PasswordAuthentication yes`.

#### Paso 15.2: Verificación de Permisos de la Jaula
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Verificar que la raíz del chroot pertenezca a `root:root` (exigencia de seguridad OpenSSH) y el subdirectorio `archivos/` al usuario.

```bash
ls -ld /home/sftp_2220335 /home/sftp_2220335/archivos
```
- **Salida esperada:** Raíz con `drwxr-xr-x root:root` y `archivos/` perteneciente a `sftp_2220335:sftp_2220335`.

#### Paso 15.3: Intento de Acceso a Shell Interactivo por SSH (Debe Ser Rechazado)
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que el usuario SFTP no puede abrir terminal interactiva ni ejecutar comandos en el sistema.

```bash
ssh -p 2222 sftp_2220335@192.168.100.3
```
- **Salida esperada:** `This service allows sftp connections only.` y desconexión inmediata.

---

### Punto 16: Regla de Reenvío para SFTP en Puerto 2222 (0.3 Pts)

#### Paso 16.1: Eliminar Regla de Reenvío para SFTP
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Deshabilitar temporalmente el paso de tráfico FORWARD hacia el puerto 22 de `srv2`.

```bash
sudo ufw route delete allow proto tcp from any to 192.168.50.2 port 22
```
- **Salida esperada:** `Rule updated`.

#### Paso 16.2: Constatar Bloqueo en el Cliente
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Demostrar que el firewall bloquea el acceso externo al puerto 2222.

```bash
sftp -o ConnectTimeout=3 -P 2222 sftp_2220335@192.168.100.3
```
- **Salida esperada:** `Connection timed out`.

#### Paso 16.3: Restaurar Regla de Reenvío
> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**  
> **Objetivo:** Reactivar el paso de tráfico FORWARD para SFTP.

```bash
sudo ufw route allow proto tcp from any to 192.168.50.2 port 22 comment 'SFTP 2222 -> srv2:22'
```
- **Salida esperada:** `Rule added`.

#### Paso 16.4: Constatar Acceso Inmediato
> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**  
> **Objetivo:** Verificar que el cliente vuelve a conectarse inmediatamente.

```bash
nc -zv -w 3 192.168.100.3 2222
```
- **Salida esperada:** `Connection to 192.168.100.3 2222 port [tcp] succeeded!`.

---

### Punto 17: Conexión SFTP por Terminal y Transferencia de Archivos (0.2 Pts)

#### Paso 17.1: Consultar Huella del Host en el Servidor
> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**  
> **Objetivo:** Obtener la huella Ed25519 oficial del servidor para validar autenticidad en el modelo TOFU (*Trust On First Use*).

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```
- **Salida esperada:** Huella SHA256 Ed25519 de `srv2`.

#### Paso 17.2: Iniciar Sesión y Transferir Archivos
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
- **Salida esperada:** `pwd` muestra `/`, el archivo se sube a `/archivos` y se descarga correctamente con integridad.

---

### Punto 18: Captura Wireshark de Sesión SFTP Multiplexada (0.3 Pts)

#### Demostración Práctica en Wireshark
> **Terminal a utilizar:** 🪟 **Wireshark GUI (`captures/`)**  
> **Objetivo:** Demostrar que SFTP opera sobre un único socket TCP (`2222/tcp`) y que el cifrado se negocia antes de transmitir credenciales.

- Abrir `captures/p18_sftp_2222.pcapng` (Filtro: `tcp.port == 2222`).
- Identificar la secuencia: Handshake TCP, banner SSHv2, `Key Exchange Init`, intercambio Diffie-Hellman / ECDH, paquete `New Keys`, y paquetes subsiguientes `Encrypted packet` (todo sobre el mismo socket).
- **Salida esperada:** Un único canal TCP multiplexado sin necesidad de rangos de puertos pasivos efímeros.

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
