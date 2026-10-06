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
PS D:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Parcial2> cd D:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Parcial2
PS D:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Parcial2> vagrant status
PS D:\Documentos\Practica_AmbienteDesarrollo\mipracticas\Parcial2> vagrant ssh cli -c "bash /vagrant/scripts/verify/cli_checks.sh"
```

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
sysctl net.



ipv4.ip_forward
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
sudo 
iptables -t nat -L -n -v
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

#### Paso 7.2: Conexión Gráfica en FileZilla y Transferencia

> **Aplicación / Entorno:** 🪟 **FileZilla Client (Host Windows)**
> **Objetivo:** Establecer sesión FTPS explícita, cotejar la huella SHA-256 y comprobar subida/descarga del archivo obligatorio `2220335.txt`.

1. Conectar a Host: `192.168.100.3`, Puerto: `21`, Cifrado: *"Requiere FTP explícito sobre TLS"*, Usuario: `ftp_2220335`, Clave: `Ftp2220335!`.
2. Validar que la huella SHA-256 en pantalla coincida exactamente con la de `srv2`.
3. Aceptar el certificado, listar el directorio, subir `2220335.txt` y descargarlo.

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
depth=0 CN = srv2-2220335, 















IP = 192.168.100.3
Server certificate
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Verify return code: 0 (ok)
```

---

### Punto 9: Capturas Wireshark: FTP Plano vs FTPS Cifrado (0.2 Pts)

#### Demostración Práctica en Wireshark

> **Aplicación / Entorno:** 🪟 **Wireshark GUI (Host Windows)**
> **Objetivo:** Evidenciar visualmente la exposición de credenciales y datos en FTP plano frente a la total confidencialidad en FTPS.

1. **FTP Plano (`captures/p09_ftp_plano.pcapng`):**
   - Filtro: `ftp || ftp-data`.
   - Aplicar *Follow TCP Stream* en `USER`: credenciales `ftp_2220335`/`Ftp2220335!` y contenido de archivo visibles en texto plano.
2. **FTPS Cifrado (`captures/p09_ftps.pcapng`):**
   - Filtro: `tcp.port == 21 || tcp.port in {50000..50010}`.
   - Constatar: Comando `AUTH TLS`, respuesta `234` y registros subsiguientes categorizados como `Application Data` cifrados con TLS 1.3.

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
vagrant@cli-2220335:~$ grep -vE '^\s*(#|$)' /etc/systemd/resolved.conf
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
vagrant@cli-2220335:~$ ls -l /etc/resolv.conf
vagrant@cli-2220335:~$ grep nameserver /etc/resolv.conf
```

- **Salida esperada:** `/etc/resolv.conf -> /run/systemd/resolve/stub-resolv.conf` con `nameserver 127.0.0.53`.

---

### Punto 11: Comprobación del Protocolo Activo +DNSOverTLS (0.2 Pts)

#### Paso 11.1: Consultar Estado de Enlaces y Protocolos

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Verificar mediante `resolvectl status` que el indicador de protocolo `+DNSOverTLS` esté habilitado a nivel global.

```bash
vagrant@cli-2220335:~$ resolvectl status
```

- **Salida esperada:** En sección Global: `Protocols: -LLMNR -mDNS +DNSOverTLS DNSSEC=no/unsupported` y servidores activos apuntando a Cloudflare.

---

### Punto 12: Demostración de Resolución de Dominios (0.2 Pts)

#### Paso 12.1: Consultas Resolviendo por DoT

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Comprobar la resolución exitosa de los tres dominios solicitados mediante el resolvedor seguro del sistema.

```bash
vagrant@cli-2220335:~$ resolvectl query uao.edu.co
vagrant@cli-2220335:~$ resolvectl query google.com
vagrant@cli-2220335:~$ resolvectl query wikipedia.org
```

#### Paso 12.2: Demostración con dig Estándar vs dig Forzando Servidor Externo

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Evidenciar que `dig` estándar utiliza el stub seguro (`127.0.0.53#53`) por DoT, mientras que forzar `@8.8.8.8` envía tráfico en texto plano por UDP 53.

```bash
vagrant@cli-2220335:~$ dig wikipedia.org | grep -E 'SERVER:|ANSWER SECTION' -A 2
vagrant@cli-2220335:~$ dig @8.8.8.8 wikipedia.org | grep -E 'SERVER:|ANSWER SECTION' -A 2
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
vagrant@cli-2220335:~$ sudo iptables -I OUTPUT -p tcp --dport 853 -j REJECT
```

#### Paso 14.2: Comprobar Resistencia a la Degradación en Modo Estricto (`yes`)

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Demostrar que con `DNSOverTLS=yes` la resolución se bloquea para impedir degradaciones hacia texto claro (*anti-downgrade*).

```bash
vagrant@cli-2220335:~$ sudo bash /vagrant/scripts/demo/dot_mode.sh yes
vagrant@cli-2220335:~$ resolvectl query uao.edu.co
```

- **Salida esperada:** Fallo en la resolución de nombres.

#### Paso 14.3: Comprobar Caída a Texto Claro en Modo Oportunista (`opportunistic`)

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Demostrar que el modo `opportunistic` cae a texto plano por UDP 53 cuando el puerto 853 es bloqueado.

```bash
vagrant@cli-2220335:~$ sudo bash /vagrant/scripts/demo/dot_mode.sh opportunistic
vagrant@cli-2220335:~$ resolvectl query uao.edu.co
```

- **Salida esperada:** Resuelve exitosamente pero en texto plano sin cifrado.

#### Paso 14.4: Restaurar Estado Operativo Estricto

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Eliminar la regla de bloqueo de iptables y reactivar el modo DoT estricto.

```bash
vagrant@cli-2220335:~$ sudo iptables -D OUTPUT -p tcp --dport 853 -j REJECT
vagrant@cli-2220335:~$ sudo bash /vagrant/scripts/demo/dot_mode.sh yes
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
vagrant@srv2-2220335:~$ sudo sed -n '/^Match User sftp_2220335/,$p' /etc/ssh/sshd_config
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
vagrant@srv2-2220335:~$ ls -ld /home/sftp_2220335
vagrant@srv2-2220335:~$ ls -ld /home/sftp_2220335/archivos
```

- **Salida esperada:** `/home/sftp_2220335` con `drwxr-xr-x` de `root:root` y `archivos/` perteneciente a `sftp_2220335:sftp_2220335`.

#### Paso 15.3: Intento de Acceso a Shell Interactivo por SSH (Debe Ser Rechazado)

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Demostrar que el usuario SFTP no puede abrir terminal de comandos ni interactuar con el sistema operativo.

```bash
vagrant@cli-2220335:~$ ssh -p 2222 sftp_2220335@192.168.100.3
```

- **Salida esperada:** `This service allows sftp connections only.` y desconexión inmediata.

---

### Punto 16: Regla de Reenvío para SFTP en Puerto 2222 (0.3 Pts)

#### Paso 16.1: Eliminar Regla de Reenvío para SFTP

> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**
> **Objetivo:** Deshabilitar temporalmente el paso de tráfico FORWARD hacia el puerto 22 de `srv2`.

```bash
vagrant@srv1-2220335:~$ sudo ufw route delete allow proto tcp from any to 192.168.50.2 port 22
```

#### Paso 16.2: Constatar Bloqueo en el Cliente

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Demostrar que el firewall bloquea el acceso externo al puerto 2222.

```bash
vagrant@cli-2220335:~$ sftp -o ConnectTimeout=5 -P 2222 sftp_2220335@192.168.100.3
```

- **Salida esperada:** `ssh: connect to host 192.168.100.3 port 2222: Connection timed out`.

#### Paso 16.3: Restaurar Regla de Reenvío

> **Terminal a utilizar:** 🖥️ **Terminal 1 (`srv1`)**
> **Objetivo:** Reactivar el paso de tráfico FORWARD para SFTP.

```bash
vagrant@srv1-2220335:~$ sudo ufw route allow proto tcp from any to 192.168.50.2 port 22 comment 'SFTP 2222 -> srv2:22'
```

#### Paso 16.4: Constatar Acceso Inmediato

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Verificar que el cliente vuelve a conectarse inmediatamente.

```bash
vagrant@cli-2220335:~$ sftp -P 2222 sftp_2220335@192.168.100.3
```

---

### Punto 17: Conexión SFTP por Terminal y Transferencia de Archivos (0.2 Pts)

#### Paso 17.1: Consultar Huella del Host en el Servidor

> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**
> **Objetivo:** Obtener la huella Ed25519 oficial del servidor para validar la autenticidad en el modelo TOFU (*Trust On First Use*).

```bash
vagrant@srv2-2220335:~$ ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

#### Paso 17.2: Iniciar Sesión y Transferir Archivos

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Interactuar con el subsistema SFTP, confirmar el enjaulamiento en la raíz `/` y realizar subida y descarga de archivos.

```bash
vagrant@cli-2220335:~$ sftp -P 2222 sftp_2220335@192.168.100.3
```

Dentro de la consola de SFTP:

```text
sftp> pwd
Remote working directory: /
sftp> cd archivos
sftp> put 2220335_sftp.txt
sftp> ls -la
sftp> get 2220335_sftp.txt 2220335_descargado.txt
sftp> bye
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
vagrant@srv1-2220335:~$ sudo ufw status verbose
vagrant@srv1-2220335:~$ sudo iptables -t nat -L -n -v
vagrant@srv1-2220335:~$ sudo tail -n 25 /var/log/ufw.log
```

#### En Servidor 2 (Servidor Interno)

> **Terminal a utilizar:** 🖧 **Terminal 2 (`srv2`)**
> **Objetivo:** Consultar el estado de los daemons vsftpd y sshd, y revisar logs de autenticación de usuarios.

```bash
vagrant@srv2-2220335:~$ systemctl status vsftpd
vagrant@srv2-2220335:~$ systemctl status ssh
vagrant@srv2-2220335:~$ sudo tail -n 25 /var/log/auth.log
```

#### En Cliente de Pruebas

> **Terminal a utilizar:** 💻 **Terminal 3 (`cli`)**
> **Objetivo:** Consultar el estado de los resolvedores DoT y ejecutar la verificación automatizada integral.

```bash
vagrant@cli-2220335:~$ resolvectl status
vagrant@cli-2220335:~$ bash /vagrant/scripts/verify/cli_checks.sh
```

### 4.2 Respuestas Rápidas a Preguntas Clave del Evaluador

1. **¿Por qué fue necesario `net.ipv4.ip_forward=1`?** UFW solo filtra paquetes (Netfilter); el reenvío entre interfaces distintas lo realiza el kernel y requiere `ip_forward=1`.
2. **¿Por qué `internal-sftp` y no el binario externo?** En jaulas chroot no existen las bibliotecas ni binarios de `/usr/lib`; `internal-sftp` corre dentro del propio proceso `sshd`.
3. **¿Por qué MASQUERADE si ya hay DNAT?** Evita enrutamiento asimétrico: si `srv2` viera la IP del cliente, respondería por su puerta de enlace por defecto (NAT de Vagrant eth0) y el cliente abortaría la sesión con RST.
4. **¿Por qué DoT requirió aislar la variable en el script de prueba?** Porque con `set -uo pipefail`, `grep -q` cierra la tubería prematuramente provocando una señal `SIGPIPE` (código 141) en `resolvectl status`, lo que invalidaba el test como fallido.
