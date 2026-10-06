# Protocolo y Guía de Sustentación Oral — Segundo Parcial (Servicios Telemáticos)

**Materia:** Servicios Telemáticos (Sistemas Operativos y Redes)
**Evaluador:** Prof. Oscar Mondragón
**Fecha:** 6 de octubre de 2026
**Estudiante:** Eduard Criollo Yule
**Código Estudiantil:** `2220335`
**Universidad:** Universidad Autónoma de Occidente (UAO)
**Calificación Objetivo:** 5.0 / 5.0 (100% de cumplimiento)

---

## Convención Operativa de Terminales de Trabajo

| Identificador Visual | Terminal / Entorno                  | Comando de Acceso    | Prompt en Pantalla          | Rol en la Arquitectura                                                             |
| :------------------: | :---------------------------------- | :------------------- | :-------------------------- | :--------------------------------------------------------------------------------- |
|   🖥️**T1**   | **Terminal 1 (`srv1`)**     | `vagrant ssh srv1` | `vagrant@srv1-2220335:~$` | Bastion, Router, Firewall UFW, NAT/iptables (`192.168.100.3` / `192.168.50.1`) |
|    🖧**T2**    | **Terminal 2 (`srv2`)**     | `vagrant ssh srv2` | `vagrant@srv2-2220335:~$` | Servidor interno aislado (`192.168.50.2`), vsftpd FTPS, OpenSSH Chroot SFTP      |
|    💻**T3**    | **Terminal 3 (`cli`)**      | `vagrant ssh cli`  | `vagrant@cli-2220335:~$`  | Cliente de pruebas (`192.168.100.10`), systemd-resolved DoT, lftp, sftp, dig     |
|    🪟**T4**    | **Host Windows (PowerShell)** | PowerShell nativo    | `PS D:\...\Parcial2>`     | Gestión de Vagrant, Test-NetConnection, FileZilla GUI, Wireshark GUI              |

---

## Tabla de Contenidos

1. [Capítulo 0: Preparación Previa y Protocolo de Apertura](#capítulo-0-preparación-previa-y-protocolo-de-apertura)
2. [Capítulo 1: Primera Parte — Servicio FTPS y Seguridad Perimetral UFW (2.0 Puntos)](#capítulo-1-primera-parte--servicio-ftps-y-seguridad-perimetral-ufw-20-puntos)
   - [Punto 1: Servidor 1 como Único Punto de Entrada (0.3 Pts)](#punto-1-servidor-1-como-único-punto-de-entrada-03-pts)
   - [Punto 2: Política Restrictiva por Defecto y Puertos Locales (0.2 Pts)](#punto-2-política-restrictiva-por-defecto-y-puertos-locales-02-pts)
   - [Punto 3: Control de Acceso Perimetral (ufw allow vs ufw route allow) (0.3 Pts)](#punto-3-control-de-acceso-perimetral-ufw-allow-vs-ufw-route-allow-03-pts)
   - [Punto 4: Reglas NAT y Contadores iptables (0.2 Pts)](#punto-4-reglas-nat-y-contadores-iptables-02-pts)
   - [Punto 5: Configuración de vsftpd para FTPS Explícito (0.2 Pts)](#punto-5-configuración-de-vsftpd-para-ftps-explícito-02-pts)
   - [Punto 6: Configuración del Modo Pasivo tras NAT (0.2 Pts)](#punto-6-configuración-del-modo-pasivo-tras-nat-02-pts)
   - [Punto 7: Conexión Gráfica con FileZilla y Huella SHA-256 (0.2 Pts)](#punto-7-conexión-gráfica-con-filezilla-y-huella-sha-256-02-pts)
   - [Punto 8: Conexión openssl s_client y Cadena de Confianza CA (0.2 Pts)](#punto-8-conexión-openssl-s_client-y-cadena-de-confianza-ca-02-pts)
   - [Punto 9: Capturas Wireshark: FTP Plano vs FTPS Cifrado (0.2 Pts)](#punto-9-capturas-wireshark-ftp-plano-vs-ftps-cifrado-02-pts)
   - [Modificaciones en Vivo y FAQs de la Parte 1](#modificaciones-en-vivo-y-faqs-de-la-parte-1)
3. [Capítulo 2: Segunda Parte — Resolución DNS Segura sobre TLS (DoT) (1.5 Puntos)](#capítulo-2-segunda-parte--resolución-dns-segura-sobre-tls-dot-15-puntos)
   - [Punto 10: Configuración de systemd-resolved y Modo Estricto (0.3 Pts)](#punto-10-configuración-de-systemd-resolved-y-modo-estricto-03-pts)
   - [Punto 11: Comprobación del Protocolo Activo +DNSOverTLS (0.2 Pts)](#punto-11-comprobación-del-protocolo-activo-dnsovertls-02-pts)
   - [Punto 12: Demostración de Resolución de Dominios (0.2 Pts)](#punto-12-demostración-de-resolución-de-dominios-02-pts)
   - [Punto 13: Capturas Wireshark: Puerto 853/tcp vs Puerto 53/udp (0.5 Pts)](#punto-13-capturas-wireshark-puerto-853tcp-vs-puerto-53udp-05-pts)
   - [Punto 14: Simulación de Bloqueo de DoT y Límites de Privacidad (0.3 Pts)](#punto-14-simulación-de-bloqueo-de-dot-y-límites-de-privacidad-03-pts)
   - [Modificaciones en Vivo y FAQs de la Parte 2](#modificaciones-en-vivo-y-faqs-de-la-parte-2)
4. [Capítulo 3: Tercera Parte — Transferencia SFTP Segura Protegida por UFW (1.5 Puntos)](#capítulo-3-tercera-parte--transferencia-sftp-segura-protegida-por-ufw-15-puntos)
   - [Punto 15: Usuario Dedicado, Jaula Chroot y Rechazo de Shell (0.4 Pts)](#punto-15-usuario-dedicado-jaula-chroot-y-rechazo-de-shell-04-pts)
   - [Punto 16: Regla de Reenvío para SFTP en Puerto 2222 (0.3 Pts)](#punto-16-regla-de-reenvío-para-sftp-en-puerto-2222-03-pts)
   - [Punto 17: Conexión SFTP por Terminal y Transferencia de Archivos (0.2 Pts)](#punto-17-conexión-sftp-por-terminal-y-transferencia-de-archivos-02-pts)
   - [Punto 18: Captura Wireshark de Sesión SFTP Multiplexada (0.3 Pts)](#punto-18-captura-wireshark-de-sesión-sftp-multiplexada-03-pts)
   - [Punto 19: Conclusión Técnica y Tabla Comparativa FTPS vs SFTP (0.3 Pts)](#punto-19-conclusión-técnica-y-tabla-comparativa-ftps-vs-sftp-03-pts)
   - [Modificaciones en Vivo y FAQs de la Parte 3](#modificaciones-en-vivo-y-faqs-de-la-parte-3)
5. [Capítulo 4: Banco Consolidado de Modificaciones en Vivo y Comandos de Inspección](#capítulo-4-banco-consolidado-de-modificaciones-en-vivo-y-comandos-de-inspección)

---

## Capítulo 0: Preparación Previa y Protocolo de Apertura

### 0.1 Comprobación Pre-Vuelo (5 minutos antes)

> **Terminal a utilizar:** 🪟 **Terminal 4 (Host Windows PowerShell)**
> **Objetivo:** Verificar que el clúster de máquinas virtuales esté activo y que los 15 controles pasen al 100%.

```powershell
cd D:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Parcial2
vagrant status
vagrant ssh cli -c "bash /vagrant/scripts/verify/cli_checks.sh"
```

- 
- **Salida esperada:** `Resultado: 15 OK / 0 FAIL`.

### 0.2 Disposición de Terminales de Trabajo

Abrir 3 ventanas de terminal ordenadas en pantalla:

1. 🖥️ **Terminal 1 (`srv1`):** `vagrant ssh srv1`
2. 🖧 **Terminal 2 (`srv2`):** `vagrant ssh srv2`
3. 💻 **Terminal 3 (`cli`):** `vagrant ssh cli`
4. 🪟 **Herramientas Gráficas:** FileZilla abierto listo para conectar a `192.168.100.3:21`, y Wireshark con capturas listas en [captures/](file:///d:/Documentos/Practica_AmbienteDesarrollo/mipracticas/Parcial2/captures).

---

## Capítulo 1: Primera Parte — Servicio FTPS y Seguridad Perimetral UFW (2.0 Puntos)

### Punto 1: Servidor 1 como Único Punto de Entrada (0.3 Pts)

#### Paso 1.1: Inspección de Políticas en el Firewall

> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**
> **Objetivo:** Comprobar que el reenvío IP esté habilitado a nivel de kernel y que UFW bloquee por defecto todo tráfico enrutado (`deny routed`).

```bash
sudo ufw status verbose
sysctl net.ipv4.ip_forward
```

- **Salida esperada:** `Default: deny (incoming), allow (outgoing), deny (routed)` y `net.ipv4.ip_forward = 1`.

#### Paso 1.2: Intento de Acceso Directo desde el Cliente (Debe Fallar)

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Demostrar que el cliente no tiene alcance directo de capa 2/3 hacia los puertos 21 y 22 de `srv2` en su IP interna.

```bash
nc -zv -w 3 192.168.50.2 21
nc -zv -w 3 192.168.50.2 22
```

- **Salida esperada:** `nc: connect to 192.168.50.2 port 21 (tcp) timed out: Operation now in progress`.

#### Paso 1.3: Prueba desde el Host Físico de Windows (Debe Fallar)

> **Terminal a utilizar:** 🪟 **Terminal 4 (Host Windows PowerShell)**
> **Objetivo:** Comprobar que el aislamiento de `srv2` aplica también para el equipo anfitrión físico.

```powershell
Test-NetConnection 192.168.50.2 -Port 21
```

- **Salida esperada:** `TcpTestSucceeded : False`.

---

### Punto 2: Política Restrictiva por Defecto y Puertos Locales (0.2 Pts)

#### Paso 2.1: Comprobación de Reglas de Entrada y Reenvío

> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**
> **Objetivo:** Verificar que el único puerto local expuesto sea el 22/tcp para administración y que los servicios hacia `srv2` se manejen vía reglas FORWARD (`ALLOW FWD`).

```bash
sudo ufw status numbered
```

- **Salida esperada:**

```text
Status: active
     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    Anywhere                   # SSH administracion srv1
[ 2] 192.168.50.2 21/tcp        ALLOW FWD   Anywhere                   # FTPS control -> srv2
[ 3] 192.168.50.2 50000:50010/tcp ALLOW FWD Anywhere                   # FTPS pasivo -> srv2
[ 4] 192.168.50.2 22/tcp        ALLOW FWD   Anywhere                   # SFTP 2222 -> srv2:22
```

#### Paso 2.2: Escaneo de Puertos No Autorizados

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Demostrar que puertos no autorizados (ej. HTTP 80) están completamente cerrados o bloqueados por la política restrictiva.

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

#### Paso 3.2: Constatar Bloqueo en el Cliente

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Demostrar que el tráfico hacia `192.168.100.3:21` queda bloqueado por la política `deny (routed)` en la cadena FORWARD.

```bash
nc -zv -w 5 192.168.100.3 21
```

- **Salida esperada:** `(UNKNOWN) [192.168.100.3] 21 (ftp) : Connection timed out`.

#### Paso 3.3: Restaurar la Regla de Reenvío

> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**
> **Objetivo:** Restablecer el reenvío de tráfico en la cadena FORWARD mediante `ufw route allow` (diferenciándolo de `ufw allow` que aplica a INPUT).

```bash
sudo ufw route allow proto tcp from any to 192.168.50.2 port 21 comment 'FTPS control -> srv2'
```

#### Paso 3.4: Constatar Conectividad Inmediata

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Verificar que el acceso al servicio FTPS se restaura inmediatamente tras aplicar la regla.

```bash
nc -zv -w 5 192.168.100.3 21
```

- **Salida esperada:** `Connection to 192.168.100.3 21 port [tcp/ftp] succeeded!`.

---

### Punto 4: Reglas NAT y Contadores iptables (0.2 Pts)

#### Paso 4.1: Mostrar Bloque NAT en before.rules

> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**
> **Objetivo:** Inspeccionar las directivas declarativas de DNAT (PREROUTING) y MASQUERADE (POSTROUTING) en la configuración persistente de UFW.

```bash
sudo sed -n '/^\*nat/,/^COMMIT/p' /etc/ufw/before.rules
```

#### Paso 4.2: Inspeccionar Contadores de Paquetes en iptables

> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**
> **Objetivo:** Constatar en tiempo real los contadores de paquetes y bytes de las cadenas PREROUTING y POSTROUTING para confirmar el procesamiento de tráfico.

```bash
sudo iptables -t nat -L -n -v
```

- **Salida esperada:** Reglas activas para puertos 21, 50000:50010 y 2222 con contadores de paquetes en incremento.

---

### Punto 5: Configuración de vsftpd para FTPS Explícito (0.2 Pts)

#### Paso 5.1: Comprobación de Parámetros TLS en el Servidor

> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**
> **Objetivo:** Verificar que `vsftpd` exija TLS de manera obligatoria para login y datos, deshabilitando versiones obsoletas (SSLv2/SSLv3).

```bash
grep -E '^(ssl_|force_|rsa_|ssl_ciphers)' /etc/vsftpd.conf
```

- **Salida esperada:** `ssl_enable=YES`, `force_local_logins_ssl=YES`, `force_local_data_ssl=YES`, `ssl_tlsv1_2=YES`, `ssl_tlsv1_3=YES`, `ssl_sslv2=NO`, `ssl_sslv3=NO`.

#### Paso 5.2: Verificación de Permisos de Clave y Cadena Criptográfica

> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**
> **Objetivo:** Confirmar que la clave privada tenga permisos restrictivos (0600) y que el certificado esté firmado y validado por la CA del laboratorio.

```bash
sudo ls -l /etc/ssl/private/servidor.key
openssl verify -CAfile /vagrant/certs/ca.crt /etc/ssl/certs/servidor.crt
```

- **Salida esperada:** Clave con permisos `-rw------- 1 root root` y `/etc/ssl/certs/servidor.crt: OK`.

---

### Punto 6: Configuración del Modo Pasivo tras NAT (0.2 Pts)

#### Paso 6.1: Inspección de Parámetros Pasivos en vsftpd

> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**
> **Objetivo:** Comprobar la delimitación del rango de puertos pasivos (50000:50010) y el anuncio forzado de la IP pública del firewall (`pasv_address=192.168.100.3`).

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
> **Objetivo:** Extraer la huella SHA-256 oficial del certificado X.509 para contrastarla contra la alerta del cliente gráfico.

```bash
openssl x509 -in /etc/ssl/certs/servidor.crt -noout -subject -issuer -dates -fingerprint -sha256
```

#### Paso 7.2: Conexión Gráfica en FileZilla y Transferencia de Archivos

> **Aplicación / Entorno:** 🪟 **FileZilla Client (Host Windows)**
> **Objetivo:** Establecer una sesión FTPS explícita de extremo a extremo a través del firewall DNAT, realizar el cotejo criptográfico estricto de la huella digital SHA-256 del certificado X.509 para descartar ataques de intermediario (MITM), verificar el establecimiento de los canales de control y datos cifrados (TLS 1.3), y comprobar la subida y descarga del archivo con validación de integridad.

---

##### 1. Preparación Previa del Archivo en el Host Windows

Antes de iniciar FileZilla, asegúrate de contar con el archivo de prueba en una ruta local accesible del host (por ejemplo, en el directorio del proyecto o en el Escritorio):

```powershell
# En PowerShell del Host (T4) dentro de la carpeta del parcial:
"Parcial 2 - Servicios Telematicos - Estudiante Eduard Criollo Yule (2220335)" | Out-File -Encoding utf8 .\2220335.txt
Get-FileHash .\2220335.txt -Algorithm SHA256
```
> **Nota:** Guarda el hash resultante para contrastarlo tras la transferencia y demostrar la integridad perfecta del archivo.

---

##### 2. Configuración en el Gestor de Sitios de FileZilla

> **¿Por qué usar el Gestor de Sitios en lugar de la barra de Conexión Rápida?**  
> La barra rápida utiliza valores predeterminados y no permite garantizar de forma persistente el modo de cifrado explícito ni la configuración del modo pasivo. El *Gestor de Sitios* (`Ctrl + S`) asegura que la negociación cumpla estrictamente con la rúbrica del parcial.

1. Abre **FileZilla Client** en Windows.
2. Ve al menú superior: **Archivo** → **Gestor de sitios...** (o presiona `Ctrl + S`).
3. Haz clic en **Nuevo sitio** y nómbralo: `Parcial2-FTPS-srv1`.
4. En la pestaña **General**, configura exactamente los siguientes parámetros:
   - **Protocolo:** `FTP - Protocolo de transferencia de archivos`
   - **Servidor:** `192.168.100.3` *(IP pública del firewall `srv1`, que redirige por DNAT hacia `srv2`)*
   - **Puerto:** `21` *(Canal de control estándar)*
   - **Cifrado:** Selecciona **`Requiere FTP explícito sobre TLS`** *(CRÍTICO: Nunca seleccionar "FTP plano no seguro")*
   - **Modo de acceso:** `Normal`
   - **Usuario:** `ftp_2220335`
   - **Contraseña:** `Ftp2220335!`
5. En la pestaña **Ajustes de transferencia**:
   - **Modo de transferencia:** Selecciona **`Pasivo`** *(Obligatorio para atravesar la arquitectura con NAT/Firewall)*.
6. Haz clic en el botón **Conectar**.

---

##### 3. Inspección del Diálogo de Alerta y Cotejo Criptográfico (Mitigación MITM)

Inmediatamente tras enviar el comando `AUTH TLS`, FileZilla suspende la conexión y despliega una ventana emergente de seguridad:  
**`El certificado del servidor es desconocido. Por favor, examine cuidadosamente el certificado para confiar en el servidor.`**

###### ¿Por qué aparece esta alerta? (Pregunta frecuente de sustentación)
El certificado de `srv2` fue emitido y firmado por una **Autoridad Certificadora (CA) privada del laboratorio** (`CA Servicios Telematicos 2220335`), la cual **no** forma parte del almacén público de certificados raíz de confianza de Microsoft Windows (*Windows Trusted Root Certification Authorities*). Por tanto, el sistema operativo no puede validar la confianza automáticamente y delega la decisión al operador humano.

###### Procedimiento de Cotejo Criptográfico (Punto 7 de la rúbrica):
1. **NO presiones "Aceptar" inmediatamente.**
2. En la ventana emergente de FileZilla, localiza la sección **Detalles del certificado** y coteja minuciosamente los siguientes campos contra la salida obtenida en `srv2` ([Paso 7.1](#paso-71-consultar-huella-criptográfica-en-el-servidor)):

| Campo en la Ventana de FileZilla | Valor Esperado en Pantalla | Correspondencia en Servidor (`openssl x509`) |
| :--- | :--- | :--- |
| **Nombre común (Sujeto / Host)** | `srv2-2220335` | `subject=... CN = srv2-2220335` |
| **Organización / Unidad** | `UAO` / `Servicios Telematicos` | `O = UAO, OU = Servicios Telematicos` |
| **Nombres alternativos (SAN)** | `IP: 192.168.100.3`, `DNS: srv2-2220335` | `subjectAltName=IP:192.168.100.3,DNS:srv2-...` |
| **Emitido por (CA Emisora)** | `CA Servicios Telematicos 2220335` | `issuer=... CN = CA Servicios Telematicos 2220335` |
| **Periodo de validez** | Fechas activas vigentes | `notBefore` / `notAfter` |
| **Huella digital SHA-256 (Fingerprint)** | `E6:50:AB:1B:E5:17:...` *(O la huella de tu servidor)* | `sha256 Fingerprint=...` (**COINCIDENCIA EXACTA**) |

3. **Justificación Teórica para el Docente:**  
   > *"La coincidencia matemática exacta de la huella digital SHA-256 descarta la presencia de un ataque de intermediario (Man-in-the-Middle). Aunque el tráfico atraviesa el firewall `srv1` (DNAT), la huella demuestra que el certificado proviene intacto y sin suplantación desde el servidor final `srv2`."*
4. Marca la casilla: **`Confiar siempre en este certificado en futuras sesiones`** (opcional, para evitar la alerta en reconexiones).
5. Haz clic en el botón **Aceptar**.

---

##### 4. Interpretación del Registro de Sesión (Log Superior de FileZilla)

Una vez aceptado el certificado, observa la consola de estado en la parte superior de FileZilla. Señala al docente la secuencia de negociación segura:

```text
Estado:      Conectando a 192.168.100.3:21...
Estado:      Conexión establecida, esperando el mensaje de bienvenida...
Respuesta:   220 (vsFTPd 3.0.5)
Comando:     AUTH TLS
Respuesta:   234 Proceed with negotiation.
Estado:      Inicializando TLS...
Estado:      Verificando certificado...
Estado:      Conexión TLS establecida. Cifrado: TLSv1.3, Conjunto de cifrado: TLS_AES_256_GCM_SHA384
Comando:     USER ftp_2220335
Respuesta:   331 Please specify the password.
Comando:     PASS **********
Respuesta:   230 Login successful.
Comando:     PBSZ 0
Respuesta:   200 PBSZ set to 0.
Comando:     PROT P
Respuesta:   200 PROT now Private.
Comando:     PASV
Respuesta:   227 Entering Passive Mode (192,168,100,3,195,84).
Estado:      Conectando a 192.168.100.3:50004...
Comando:     MLSD
Respuesta:   150 Here comes the directory listing.
Respuesta:   226 Directory send OK.
Estado:      Listado de directorios completado
```

> **Aspectos clave para sustentar:**
> - `AUTH TLS` + `234`: Negociación explícita para elevar la conexión de texto plano a TLS.
> - `PBSZ 0` (*Protection Buffer Size*) y `PROT P` (*Data Channel Protection Level = Private*): Obligan a que el canal de datos (puertos pasivos) también viaje cifrado con TLS.
> - `227 Entering Passive Mode (192,168,100,3,X,Y)`: El servidor anuncia la IP pública `192.168.100.3` (gracias a `pasv_address`) y un puerto dinámico calculado como `(X * 256) + Y` (por ejemplo, `(195 * 256) + 84 = 50004`), el cual cae estrictamente dentro del rango `50000..50010` habilitado en UFW.

---

##### 5. Ejecución de la Transferencia de Archivos (Subida y Descarga)

1. **Subida (*Upload*):**
   - En el panel izquierdo (**Sitio local**), navega hasta el directorio donde creaste `2220335.txt`.
   - En el panel derecho (**Sitio remoto**), confirma que estás posicionado en el directorio raíz del usuario (`/home/ftp_2220335`). Verás el archivo inicial `bienvenida.txt`.
   - Arrastra el archivo `2220335.txt` desde el panel izquierdo al panel derecho (o clic derecho → **Subir**).
   - Observa en el log:
     ```text
     Comando:     PASV
     Respuesta:   227 Entering Passive Mode (192,168,100,3,195,85).
     Comando:     STOR 2220335.txt
     Respuesta:   150 Ok to send data.
     Respuesta:   226 Transfer complete.
     Estado:      Transferencia de archivo satisfactoria
     ```
2. **Descarga (*Download*):**
   - En el panel izquierdo local, renombra el archivo local a `2220335_original.txt` para comprobar la recepción limpia.
   - En el panel derecho remoto, haz clic derecho sobre `2220335.txt` → **Descargar**.
   - Observa en el log:
     ```text
     Comando:     PASV
     Respuesta:   227 Entering Passive Mode (192,168,100,3,195,86).
     Comando:     RETR 2220335.txt
     Respuesta:   150 Opening BINARY mode data connection for 2220335.txt.
     Respuesta:   226 Transfer complete.
     Estado:      Transferencia de archivo satisfactoria
     ```
3. **Validación de Integridad:**
   - En la pestaña inferior **Transferencias satisfactorias**, comprueba que la transferencia figure con estado 100% exitoso y 0 transferencias fallidas.
   - Puedes demostrar la integridad comparando el hash criptográfico del archivo descargado en PowerShell:
     ```powershell
     Get-FileHash .\2220335.txt -Algorithm SHA256
     ```
     El hash debe ser idéntico al calculado originalmente en `srv2` (`sha256sum /home/ftp_2220335/2220335.txt`).

---

##### 6. Evidencias Gráficas Asociadas en el Repositorio

Para el informe final y la presentación, este procedimiento está respaldado por las capturas oficiales ubicadas en [images/](images/):
- **[images/12_filezilla_certificado.png](images/12_filezilla_certificado.png):** Ventana de diálogo de certificado desconocido mostrando el emisor, sujeto y huella SHA-256 en FileZilla.
- **[images/13_openssl_fingerprint.png](images/13_openssl_fingerprint.png):** Salida por terminal en `srv2` con la huella oficial contrastada.
- **[images/14_filezilla_transferencia.png](images/14_filezilla_transferencia.png):** Interfaz principal de FileZilla con la sesión TLS activa, los paneles local y remoto sincronizados y el registro de transferencia exitosa.

---

### Punto 8: Conexión openssl s_client y Cadena de Confianza CA (0.2 Pts)

#### Paso 8.1: Validación de Cadena de Confianza por Terminal

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Validar por consola que la negociación STARTTLS resuelva la cadena completa hasta la CA raíz con código `Verify return code: 0 (ok)`.

```bash
openssl s_client -connect 192.168.100.3:21 -starttls ftp -CAfile ~/ca.crt </dev/null | grep -E '(depth|New,|Verify return|Server certificate)'
```

- **Salida esperada:**

```text
depth=1 CN = CA-ServiciosTelematicos-2026
depth=0 CN = srv2-2220335, IP = 192.168.100.3
Server certificate
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Verify return code: 0 (ok)
```

---

### Punto 9: Capturas Wireshark: FTP Plano vs FTPS Cifrado (0.2 Pts)

#### Demostración Práctica Paso a Paso en Wireshark y Terminales

> **Aplicación / Entorno:** 🪟 **Wireshark GUI (Host Windows)** + 💻 **Terminal 3 (`cli`)** + 🖧 **Terminal 2 (`srv2`)**
> **Objetivo:** Demostrar empíricamente la vulnerabilidad crítica de FTP en texto plano (exposición de credenciales y datos ante ataques de interceptación) frente a la estricta confidencialidad que proporciona FTPS explícito con TLS 1.3 (canales de control y de datos cifrados).

---

##### 1. Procedimiento de Captura: Sesión FTP en Plano (`p09_ftp_plano.pcapng`)

###### Paso 1.1: Deshabilitar temporalmente TLS en el Servidor
En **🖧 Terminal 2 (`srv2`)**, desactiva el requisito de cifrado en `vsftpd` utilizando el script auxiliar provisto en el repositorio:

```bash
sudo bash /vagrant/scripts/demo/ftps_tls.sh off
```
- **Salida esperada:** Mensaje `>> TLS DESHABILITADO (FTP plano) - SOLO para la captura del punto 9`, confirmando `ssl_enable=NO` y el reinicio automático del demonio `vsftpd`.

###### Paso 1.2: Capturar tráfico y ejecutar la sesión en texto plano
En **💻 Terminal 3 (`cli`)**, inicia la captura con `tshark` y transmite el archivo de prueba forzando el modo sin TLS:

```bash
# Iniciar captura en segundo plano escuchando la interfaz eth1 hacia el firewall
sudo tshark -i eth1 -f "host 192.168.100.3" -w /vagrant/captures/p09_ftp_plano.pcapng -c 40 &
PID_CAP=$!
sleep 2

# Ejecutar sesión FTP sin TLS subiendo 2220335.txt y listando el directorio
lftp -e "set ftp:ssl-allow no; put /home/vagrant/2220335.txt; ls; bye" -u ftp_2220335,Ftps2220335! 192.168.100.3
wait $PID_CAP
```
- **Resultado:** Se genera el archivo de captura [captures/p09_ftp_plano.pcapng](captures/p09_ftp_plano.pcapng) en la carpeta compartida, accesible inmediatamente desde Windows.

---

##### 2. Procedimiento de Captura: Sesión FTPS Cifrada (`p09_ftps.pcapng`)

###### Paso 2.1: Rehabilitar TLS obligatorio en el Servidor
En **🖧 Terminal 2 (`srv2`)**, restaura la seguridad estricta:

```bash
sudo bash /vagrant/scripts/demo/ftps_tls.sh on
```
- **Salida esperada:** Mensaje `>> TLS HABILITADO (FTPS explicito obligatorio)` con `ssl_enable=YES`, `force_local_logins_ssl=YES` y `force_local_data_ssl=YES`.

###### Paso 2.2: Capturar tráfico y ejecutar la sesión segura
En **💻 Terminal 3 (`cli`)**, captura la sesión FTPS protegida con TLS:

```bash
# Iniciar captura en segundo plano
sudo tshark -i eth1 -f "host 192.168.100.3" -w /vagrant/captures/p09_ftps.pcapng -c 60 &
PID_CAP=$!
sleep 2

# Ejecutar sesión FTPS (lftp negocia TLS automáticamente según ~/.lftprc)
lftp -e "put /home/vagrant/2220335.txt; ls; bye" -u ftp_2220335,Ftps2220335! 192.168.100.3
wait $PID_CAP
```
- **Resultado:** Se genera el archivo de captura [captures/p09_ftps.pcapng](captures/p09_ftps.pcapng).

---

##### 3. Análisis Forense y Demostración en Wireshark (Host Windows)

Abre **Wireshark** en Windows para analizar las dos capturas guardadas en `mipracticas\Parcial2\captures\`:

#### A. Análisis de la Captura Plana (`p09_ftp_plano.pcapng`)
1. En Wireshark, abre el archivo `captures/p09_ftp_plano.pcapng`.
2. En la barra de filtros de visualización superior, escribe:
   ```text
   ftp || ftp-data
   ```
3. **Qué observar en la lista de paquetes:**
   - **Paquete con comando USER:** Se observa en texto ASCII claro: `Request: USER ftp_2220335`.
   - **Paquete con comando PASS:** Se observa la contraseña en texto plano absoluto: `Request: PASS Ftps2220335!`.
   - **Paquete con comando PASV:** El servidor responde `227 Entering Passive Mode (192,168,100,3,X,Y)`.
   - **Paquete con comando STOR:** `Request: STOR 2220335.txt`.
   - **Paquete FTP-DATA:** Paquetes sobre el puerto efímero transportando los bytes del archivo.
4. **Demostración de impacto (Follow TCP Stream):**
   - Haz clic derecho sobre el paquete del comando `USER` → **Follow** → **TCP Stream**.
   - **Ventana emergente:** Señala al docente cómo todo el diálogo entre cliente y servidor aparece en texto legible (rojo para comandos del cliente, azul para respuestas del servidor), demostrando la **falta total de confidencialidad** y la exposición de credenciales ante sniffing.
   - Cierra la ventana y haz clic derecho sobre cualquier paquete de protocolo `FTP-DATA` → **Follow** → **TCP Stream**.
   - **Ventana emergente:** Señala que el contenido del archivo `2220335.txt` es 100% legible en texto claro.

#### B. Análisis de la Captura Cifrada (`p09_ftps.pcapng`)
1. En Wireshark, abre el archivo `captures/p09_ftps.pcapng`.
2. En la barra de filtros de visualización, escribe:
   ```text
   tcp.port == 21 || tcp.port in {50000..50010}
   ```
3. **Qué observar en la lista de paquetes:**
   - **Banner inicial:** `Response: 220 (vsFTPd 3.0.5)`.
   - **Comando de elevación a TLS:** `Request: AUTH TLS` y respuesta del servidor `Response: 234 Proceed with negotiation.`.
   - **Transición inmediata de protocolo:** A partir del siguiente paquete, el protocolo deja de ser `FTP` y pasa a ser **`TLSv1.3`** (o `TLSv1.2` en el `Client Hello`).
   - **Handshake TLS:** Intercambio de claves Diffie-Hellman / ECDHE (`Server Hello`, `Change Cipher Spec`).
   - **Cifrado del canal de control:** Todos los paquetes subsiguientes en el puerto 21 figuran como **`Application Data`**. Las credenciales `USER` y `PASS` nunca aparecen en texto claro.
   - **Cifrado del canal de datos pasivo:** Al abrirse el puerto pasivo (ej. `50004`), ocurre un segundo handshake TLS y los paquetes de datos del archivo también se transmiten como **`Application Data`** gracias a las directivas `force_local_data_ssl=YES` y `PROT P`.
4. **Demostración de impacto (Follow TCP Stream):**
   - Haz clic derecho sobre cualquier paquete clasificado como `Application Data` → **Follow** → **TCP Stream**.
   - **Ventana emergente:** Muestra al evaluador que únicamente son visibles el banner `220` y el comando `AUTH TLS`. A partir de ahí, todo el flujo es una secuencia de **bytes binarios cifrados e ininteligibles**, demostrando confidencialidad e integridad criptográfica total.

---

##### 4. Tabla Comparativa Resumen para la Sustentación

| Característica / Parámetro | FTP Plano (`p09_ftp_plano.pcapng`) | FTPS Cifrado (`p09_ftps.pcapng`) |
| :--- | :--- | :--- |
| **Protocolo en Wireshark** | `FTP` y `FTP-DATA` | `FTP` inicial → `TLSv1.3 (Application Data)` |
| **Credenciales (`USER`/`PASS`)** | Texto plano visible (`Ftps2220335!`) | Cifradas en registro TLS (*Application Data*) |
| **Comando de elevación** | Ninguno (plano nativo) | `AUTH TLS` seguido de respuesta `234` |
| **Canal de Datos (Pasivo)** | Texto plano sin cifrar | Handshake TLS independiente + *Application Data* |
| **Confidencialidad** | Nula (vulnerable a *sniffing* / *MITM*) | Total (cifrado simétrico AES-256-GCM / TLS 1.3) |
| **Integridad** | Ninguna verificación criptográfica | Garantizada por HMAC / Poly1305 / GCM de TLS |

---

##### 5. Preguntas Frecuentes del Docente en este Punto

1. **¿Por qué el banner inicial `220` y `AUTH TLS` viajan en claro en FTPS?**  
   *Respuesta:* Porque estamos utilizando **FTPS Explícito** (RFC 4217) sobre el puerto 21. La sesión inicia como TCP estándar para permitir compatibilidad y luego el cliente solicita explícitamente elevar el socket a TLS mediante el comando `AUTH TLS` (análogo a `STARTTLS` en SMTP o IMAP).
2. **¿Por qué en FTPS se observan dos handshakes TLS distintos?**  
   *Respuesta:* Debido a la arquitectura de dos canales del protocolo FTP. El primer handshake protege el canal de control (puerto 21: comandos y autenticación), y el segundo handshake protege de forma independiente el canal de datos pasivo (puerto 50000..50010: listados de directorios y contenido de archivos transferidos).
3. **¿Por qué con TLS 1.3 no se puede ver el certificado del servidor en Wireshark?**  
   *Respuesta:* En TLS 1.2 el mensaje `Certificate` viajaba en claro tras el `Server Hello`. En TLS 1.3, las claves simétricas efímeras se derivan inmediatamente después del intercambio Diffie-Hellman en el `Server Hello`, por lo que el certificado del servidor y todos los mensajes posteriores viajan completamente cifrados.

---

### Modificaciones en Vivo y FAQs de la Parte 1

| Petición del Docente                             | Terminal / Dónde                                       | Objetivo y Procedimiento Exacto                                                                                                                                                                                                                                                                                                                                                                                    | Verificación Inmediata                                                                                                     |
| :------------------------------------------------ | :------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------- |
| **Cambiar rango pasivo a 50020:50030**      | 🖧**T2 (`srv2`)**+ 🖥️ **T1 (`srv1`)** | **Objetivo:** Modificar el rango efímero pasivo en servidor y firewall.En 🖧 `srv2`: editar `/etc/vsftpd.conf` (`pasv_min_port=50020`, `pasv_max_port=50030`) y `sudo systemctl restart vsftpd`.En 🖥️ `srv1`: actualizar `/etc/ufw/before.rules` (puertos `50020:50030`), ejecutar `sudo ufw reload`, y actualizar `sudo ufw route allow proto tcp to 192.168.50.2 port 50020:50030`. | En 💻`cli` o FileZilla: transferir archivo y comprobar puerto en 5002X en Wireshark.                                      |
| **Romper `pasv_address` (simular fallo)** | 🖧**T2 (`srv2`)**                               | **Objetivo:** Simular la falla de transferencia cuando el servidor anuncia su IP privada inaccesible.`sudo sed -i 's/^pasv_address/#pasv_address/' /etc/vsftpd.conf && sudo systemctl restart vsftpd`                                                                                                                                                                                                      | En 💻`cli`: `lftp` hace login OK pero `ls` da timeout anunciando `192.168.50.2`. Revertir restaurando la directiva. |
| **Simular caída a FTP plano**              | 🖧**T2 (`srv2`)**                               | **Objetivo:** Desactivar temporalmente el cifrado obligatorio para ilustrar el modo sin TLS.`sudo bash /vagrant/scripts/demo/ftps_tls.sh off`                                                                                                                                                                                                                                                              | `lftp` conecta sin TLS. Restaurar con `sudo bash /vagrant/scripts/demo/ftps_tls.sh on`.                                 |

---

## Capítulo 2: Segunda Parte — Resolución DNS Segura sobre TLS (DoT) (1.5 Puntos)

### Punto 10: Configuración de systemd-resolved y Modo Estricto (0.3 Pts)

#### Paso 10.1: Inspección de Configuración en el Cliente

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Comprobar la parametrización de resolvers con SNI (`IP#nombre`) y la activación del modo estricto `DNSOverTLS=yes`.

```bash
grep -vE '^\s*(#|$)' /etc/systemd/resolved.conf
```

- **Salida esperada:**

```ini
[Resolve]
DNS=1.1.1.1#cloudflare-dns.com 1.0.0.1#cloudflare-dns.com 8.8.8.8#dns.google
FallbackDNS=9.9.9.9#dns.quad9.net 8.8.4.4#dns.google
DNSOverTLS=yes
DNSSEC=no
```

#### Paso 10.2: Verificación del Stub Local

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Confirmar que `/etc/resolv.conf` sea un enlace simbólico hacia el stub resolver seguro de systemd (`127.0.0.53`).

```bash
ls -l /etc/resolv.conf
grep nameserver /etc/resolv.conf
```

- **Salida esperada:** `/etc/resolv.conf -> /run/systemd/resolve/stub-resolv.conf` con `nameserver 127.0.0.53`.

---

### Punto 11: Comprobación del Protocolo Activo +DNSOverTLS (0.2 Pts)

#### Paso 11.1: Consultar Estado de Enlaces y Protocolos

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Verificar mediante `resolvectl status` que el indicador de protocolo `+DNSOverTLS` esté habilitado a nivel global.

```bash
resolvectl status
```

- **Salida esperada:** En sección Global: `Protocols: -LLMNR -mDNS +DNSOverTLS DNSSEC=no/unsupported` y servidores activos apuntando a Cloudflare.

---

### Punto 12: Demostración de Resolución de Dominios (0.2 Pts)

#### Paso 12.1: Consultas Resolviendo por DoT

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Comprobar la resolución exitosa de los tres dominios solicitados mediante el resolvedor seguro del sistema.

```bash
resolvectl query uao.edu.co
resolvectl query google.com
resolvectl query wikipedia.org
```

#### Paso 12.2: Demostración con dig Estándar vs dig Forzando Servidor Externo

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Evidenciar que `dig` estándar utiliza el stub seguro (`127.0.0.53#53`) por DoT, mientras que forzar `@8.8.8.8` envía tráfico en texto plano por UDP 53.

```bash
dig wikipedia.org | grep -E 'SERVER:|ANSWER SECTION' -A 2
dig @8.8.8.8 wikipedia.org | grep -E 'SERVER:|ANSWER SECTION' -A 2
```

- **Salida esperada:**
  - `dig wikipedia.org`: `SERVER: 127.0.0.53#53` (resuelve vía DoT).
  - `dig @8.8.8.8 wikipedia.org`: `SERVER: 8.8.8.8#53` (resuelve en texto plano fuera del stub).

---

### Punto 13: Capturas Wireshark: Puerto 853/tcp vs Puerto 53/udp (0.5 Pts)

#### Demostración Práctica en Wireshark

> **Aplicación / Entorno:** 🪟 **Wireshark GUI (Host Windows)**
> **Objetivo:** Demostrar que en DoT el contenido de la consulta permanece completamente oculto bajo registros TLS, a diferencia de DNS tradicional.

1. **DoT Cifrado (`captures/p13_dot_853.pcapng`):**
   - Filtro: `tcp.port == 853`.
   - Mostrar apretón de manos TLS 1.3 con SNI `cloudflare-dns.com` y paquetes `Application Data`. El nombre consultado no aparece en el payload.
2. **DNS Convencional (`captures/p13_dns_53.pcapng`):**
   - Filtro: `udp.port == 53`.
   - Mostrar la consulta estándar `A uao.edu.co` y sus respuestas legibles en texto plano.

---

### Punto 14: Simulación de Bloqueo de DoT y Límites de Privacidad (0.3 Pts)

#### Paso 14.1: Bloquear Puerto 853 en Firewall Local

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Simular un bloqueo perimetral o censura del puerto 853/tcp.

```bash
sudo iptables -I OUTPUT -p tcp --dport 853 -j REJECT
```

#### Paso 14.2: Comprobar Resistencia a la Degradación en Modo Estricto (`yes`)

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Demostrar que con `DNSOverTLS=yes` la resolución se bloquea para impedir degradaciones hacia texto claro (*anti-downgrade*).

```bash
sudo bash /vagrant/scripts/demo/dot_mode.sh yes
resolvectl query uao.edu.co
```

- **Salida esperada:** Fallo en la resolución de nombres.

#### Paso 14.3: Comprobar Caída a Texto Claro en Modo Oportunista (`opportunistic`)

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Demostrar que el modo `opportunistic` cae a texto plano por UDP 53 cuando el puerto 853 es bloqueado.

```bash
sudo bash /vagrant/scripts/demo/dot_mode.sh opportunistic
resolvectl query uao.edu.co
```

- **Salida esperada:** Resuelve exitosamente pero en texto plano sin cifrado.

#### Paso 14.4: Restaurar Estado Operativo Estricto

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Eliminar la regla de bloqueo de iptables y reactivar el modo DoT estricto.

```bash
sudo iptables -D OUTPUT -p tcp --dport 853 -j REJECT
sudo bash /vagrant/scripts/demo/dot_mode.sh yes
```

---

### Modificaciones en Vivo y FAQs de la Parte 2

| Petición del Docente                    | Terminal / Dónde        | Objetivo y Procedimiento Exacto                                                                                                                                                             | Verificación Inmediata                                                                                      |
| :--------------------------------------- | :----------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------- |
| **Cambiar resolver a Quad9**       | 💻**T3 (`cli`)** | **Objetivo:** Cambiar el proveedor upstream DoT.Editar `/etc/systemd/resolved.conf`: `DNS=9.9.9.9#dns.quad9.net` y ejecutar `sudo systemctl restart systemd-resolved`.          | `resolvectl status` muestra Quad9 como servidor primario activo.                                           |
| **Introducir nombre SNI erróneo** | 💻**T3 (`cli`)** | **Objetivo:** Demostrar la validación estricta de certificado por SNI.En `/etc/systemd/resolved.conf`: colocar `DNS=1.1.1.1#sitio-falso.com` con `DNSOverTLS=yes` y reiniciar. | La resolución falla de inmediato debido a que el certificado presentado no coincide con el SNI configurado. |

---

## Capítulo 3: Tercera Parte — Transferencia SFTP Segura Protegida por UFW (1.5 Puntos)

### Punto 15: Usuario Dedicado, Jaula Chroot y Rechazo de Shell (0.4 Pts)

#### Paso 15.1: Inspección de sshd_config en el Servidor

> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**
> **Objetivo:** Comprobar la directiva `Match User` que confina al usuario en chroot y fuerza el subsistema en memoria `internal-sftp`.

```bash
sudo sed -n '/^Match User sftp_2220335/,$p' /etc/ssh/sshd_config
```

- **Salida esperada:**

```sshconfig
Match User sftp_2220335
    ChrootDirectory /home/sftp_2220335
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
    PasswordAuthentication yes
```

#### Paso 15.2: Verificación de Permisos y Propietarios de la Jaula

> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**
> **Objetivo:** Verificar que la raíz del chroot pertenezca a `root:root` (exigencia de seguridad de OpenSSH) y el subdirectorio `archivos/` al usuario.

```bash
ls -ld /home/sftp_2220335
ls -ld /home/sftp_2220335/archivos
```

- **Salida esperada:** `/home/sftp_2220335` con `drwxr-xr-x` de `root:root` y `archivos/` perteneciente a `sftp_2220335:sftp_2220335`.

#### Paso 15.3: Intento de Acceso a Shell Interactivo por SSH (Debe Ser Rechazado)

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Demostrar que el usuario SFTP no puede abrir terminal de comandos ni interactuar con el sistema operativo.

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

#### Paso 16.2: Constatar Bloqueo en el Cliente

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Demostrar que el firewall bloquea el acceso externo al puerto 2222.

```bash
sftp -o ConnectTimeout=5 -P 2222 sftp_2220335@192.168.100.3
```

- **Salida esperada:** `ssh: connect to host 192.168.100.3 port 2222: Connection timed out`.

#### Paso 16.3: Restaurar Regla de Reenvío

> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**
> **Objetivo:** Reactivar el paso de tráfico FORWARD para SFTP.

```bash
sudo ufw route allow proto tcp from any to 192.168.50.2 port 22 comment 'SFTP 2222 -> srv2:22'
```

#### Paso 16.4: Constatar Acceso Inmediato

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Verificar que el cliente vuelve a conectarse inmediatamente.

```bash
sftp -P 2222 sftp_2220335@192.168.100.3
```

---

### Punto 17: Conexión SFTP por Terminal y Transferencia de Archivos (0.2 Pts)

#### Paso 17.1: Consultar Huella del Host en el Servidor

> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**
> **Objetivo:** Obtener la huella Ed25519 oficial del servidor para validar la autenticidad en el modelo TOFU (*Trust On First Use*).

```bash
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

#### Paso 17.2: Iniciar Sesión y Transferir Archivos

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Interactuar con el subsistema SFTP, confirmar el enjaulamiento en la raíz `/` y realizar subida y descarga de archivos.

```bash
sftp -P 2222 sftp_2220335@192.168.100.3
```

Dentro de la consola de SFTP:

```text
pwd
Remote working directory: /
cd archivos
put 2220335_sftp.txt
ls -la
get 2220335_sftp.txt 2220335_descargado.txt
bye
```

---

### Punto 18: Captura Wireshark de Sesión SFTP Multiplexada (0.3 Pts)

#### Demostración Práctica en Wireshark

> **Aplicación / Entorno:** 🪟 **Wireshark GUI (Host Windows)**
> **Objetivo:** Demostrar que SFTP opera sobre un único socket TCP (`2222/tcp`) y que el cifrado se negocia antes de transmitir credenciales.

- Abrir `captures/p18_sftp_2222.pcapng` (Filtro: `tcp.port == 2222`).
- Identificar la secuencia: Handshake TCP, banner SSHv2, `Key Exchange Init`, intercambio Diffie-Hellman / ECDH, paquete `New Keys`, y paquetes posteriores `Encrypted packet` (todo en un solo flujo).

---

### Punto 19: Conclusión Técnica y Tabla Comparativa FTPS vs SFTP (0.3 Pts)

#### Tabla Comparativa Oficial

| Dimensión Técnica                 | FTPS (FTP sobre TLS / RFC 4217)                                                                          | SFTP (SSH File Transfer Protocol / RFC 4251)                                                        |
| :---------------------------------- | :------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------- |
| **Canales TCP**               | **2 o más:** 1 canal de control (`21/tcp`) + puertos de datos pasivos (`50000:50010/tcp`).    | **1 único socket multiplexado:** Control, credenciales y datos sobre el puerto `2222/tcp`. |
| **Autenticación**            | Certificados**X.509** dependientes de una Autoridad Certificadora (PKI).                           | Claves públicas de host (`ssh_host_*_key`) mediante modelo **TOFU**.                       |
| **Inicio del Cifrado**        | En modo explícito inicia en**texto plano** y se promueve tras `AUTH TLS`.                       | Cifrado negociado**desde el primer paquete** antes de enviar credenciales.                    |
| **Complejidad NAT/Firewall**  | **Alta:** Requiere abrir rangos pasivos fijos, deshabilitar ALGs ciegos y forzar `pasv_address`. | **Mínima:** Solo requiere reenviar un único puerto TCP (`22` o `2222`).                 |
| **Superficie de Exposición** | **12 puertos abiertos** (21 + 50000:50010).                                                        | **1 puerto abierto** (`2222`).                                                              |
| **Dictamen Final**            | Desaconsejado salvo requerimiento estricto de clientes legacy o PKI X.509.                               | **Solución recomendada para entornos corporativos con firewall estricto.**                   |

---

### Modificaciones en Vivo y FAQs de la Parte 3

| Petición del Docente                                               | Terminal / Dónde           | Objetivo y Procedimiento Exacto                                                                                                                                                                              | Verificación Inmediata                                                                                                                                                                                  |
| :------------------------------------------------------------------ | :-------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cambiar puerto público de SFTP a 2200**                    | 🖥️**T1 (`srv1`)** | **Objetivo:** Reasignar el puerto externo del servicio en el firewall.En `/etc/ufw/before.rules`: cambiar `--dport 2222` a `--dport 2200` en la regla PREROUTING y ejecutar `sudo ufw reload`. | En 💻`cli`: `sftp -P 2200 ...` conecta exitosamente (la regla `route` se mantiene hacia el puerto interno 22).                                                                                     |
| **Permitir escritura en la raíz del chroot (simular fallo)** | 🖧**T2 (`srv2`)**   | **Objetivo:** Provocar la denegación de conexión por violación de permisos de jaula de OpenSSH.`sudo chown sftp_2220335 /home/sftp_2220335`                                                       | En 💻`cli`: la conexión se cierra. En 🖧 `srv2` con `journalctl -u ssh` se lee `fatal: bad ownership or modes for chroot directory`. Restaurar con `sudo chown root:root /home/sftp_2220335`. |
| **Bloquear a un cliente por IP**                              | 🖥️**T1 (`srv1`)** | **Objetivo:** Filtrar el acceso a nivel de dirección IP origen.`sudo ufw route insert 1 deny from 192.168.100.10 to 192.168.50.2`                                                                   | En 💻`cli`: la conexión da timeout; desde otra IP cliente seguiría permitida.                                                                                                                        |

---

## Capítulo 4: Banco Consolidado de Modificaciones en Vivo y Comandos de Inspección

### 4.1 Comandos de Inspección Rápida durante la Sustentación

#### En Servidor 1 (Firewall / Router)

> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**
> **Objetivo:** Inspeccionar el estado del firewall, contadores NAT de iptables y logs de bloqueos.

```bash
sudo ufw status verbose
sudo iptables -t nat -L -n -v
sudo tail -n 25 /var/log/ufw.log
```

#### En Servidor 2 (Servidor Interno)

> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**
> **Objetivo:** Consultar el estado de los daemons vsftpd y sshd, y revisar logs de autenticación de usuarios.

```bash
systemctl status vsftpd
systemctl status ssh
sudo tail -n 25 /var/log/auth.log
```

#### En Cliente de Pruebas

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Consultar el estado de los resolvedores DoT y ejecutar la verificación automatizada integral.

```bash
resolvectl status
bash /vagrant/scripts/verify/cli_checks.sh
```

### 4.2 Respuestas Rápidas a Preguntas Clave del Evaluador

1. **¿Por qué fue necesario `net.ipv4.ip_forward=1`?** UFW solo filtra paquetes (Netfilter); el reenvío entre interfaces distintas lo realiza el kernel y requiere `ip_forward=1`.
2. **¿Por qué `internal-sftp` y no el binario externo?** En jaulas chroot no existen las bibliotecas ni binarios de `/usr/lib`; `internal-sftp` corre dentro del propio proceso `sshd`.
3. **¿Por qué MASQUERADE si ya hay DNAT?** Evita enrutamiento asimétrico: si `srv2` viera la IP del cliente, respondería por su puerta de enlace por defecto (NAT de Vagrant eth0) y el cliente abortaría la sesión con RST.
4. **¿Por qué DoT requirió aislar la variable en el script de prueba?** Porque con `set -uo pipefail`, `grep -q` cierra la tubería prematuramente provocando una señal `SIGPIPE` (código 141) en `resolvectl status`, lo que invalidaba el test como fallido.
