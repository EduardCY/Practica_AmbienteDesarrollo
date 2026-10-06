# Evidencias (capturas de pantalla)

Guarde aquí las capturas con **exactamente** estos nombres; el `README.md` de la práctica ya las referencia.
En cada captura debe verse el **prompt con el hostname** (`srv1-2220335`, `srv2-2220335`, `cli-2220335`).

| Archivo | Punto | Qué debe mostrar |
| :--- | :---: | :--- |
| `01_vagrant_status.png` | — | `vagrant status` con srv1, srv2 y cli en `running` |
| `02_hostnames_ips.png` | — | `hostnamectl` + `ip -br a` en los tres nodos |
| `03_ufw_status_verbose.png` | 1, 4 | `sudo ufw status verbose` (deny incoming / deny routed) |
| `04_ip_forward_before_rules.png` | 1 | `sysctl net.ipv4.ip_forward` y bloque `*nat` de `/etc/ufw/before.rules` |
| `05_srv2_no_alcanzable.png` | 1, 16 | `nc -zv 192.168.50.2 21/22` y `Test-NetConnection` fallando |
| `06_ufw_status_numbered.png` | 2 | `sudo ufw status numbered` (solo 22 local + 3 reglas route) |
| `07_sin_regla_21_falla.png` | 3 | Regla `route` del 21 eliminada y conexión fallando |
| `08_con_regla_21_exito.png` | 3 | Regla agregada de nuevo y conexión exitosa |
| `09_iptables_nat.png` | 4 | `sudo iptables -t nat -L -n -v` con contadores |
| `10_vsftpd_conf_tls.png` | 5, 6 | Directivas `ssl_*`, `force_*` y `pasv_*` |
| `11_vsftpd_status_puertos.png` | 5 | `systemctl status vsftpd` y `ss -tlnp` |
| `12_filezilla_certificado.png` | 7 | Diálogo de certificado de FileZilla (sujeto, emisor, vigencia, huella) |
| `13_openssl_fingerprint.png` | 7 | `openssl x509 -in servidor.crt -noout -fingerprint -sha256` |
| `14_filezilla_transferencia.png` | 7 | Listado remoto, subida y descarga de `2220335.txt` |
| `15_openssl_s_client.png` | 8 | `Verify return code: 0 (ok)`, protocolo y cipher |
| `16_wireshark_ftp_plano.png` | 9 | USER/PASS y contenido del archivo en texto claro |
| `17_wireshark_ftps.png` | 9 | `AUTH TLS`, handshake TLS en 21 y datos cifrados en 50000-50010 |
| `18_resolved_conf.png` | 10 | `/etc/systemd/resolved.conf` y `ls -l /etc/resolv.conf` |
| `19_resolvectl_status.png` | 11 | Salida completa de `resolvectl status` (+DNSOverTLS) |
| `20_resolvectl_query.png` | 12 | Tres dominios resueltos con `resolvectl query` / `dig` |
| `21_wireshark_dot_853.png` | 13 | `tcp.port == 853` con TLS y Application Data |
| `22_wireshark_dns_53.png` | 13 | `udp.port == 53` con la consulta en texto claro |
| `23_dot_bloqueo_853.png` | 14 | (Opcional) bloqueo de 853 con `yes` vs `opportunistic` |
| `24_sftp_chroot_config.png` | 15 | Bloque `Match User` y permisos del chroot |
| `25_ssh_rechazado.png` | 15 | `ssh -p 2222 sftp_2220335@...` → *sftp connections only* |
| `26_sftp_sin_regla_falla.png` | 16 | Sin la regla route del 22 la conexión SFTP falla |
| `27_sftp_con_regla_exito.png` | 16 | Con la regla, conexión exitosa |
| `28_sftp_hostkey_ls_put_get.png` | 17 | Huella en la primera conexión + `ls`, `put`, `get` |
| `29_wireshark_sftp_2222.png` | 18 | SSH-2.0, KEXINIT/ECDH, NEWKEYS y paquetes cifrados |
| `30_verificacion_automatica.png` | — | Salida de `scripts/verify/cli_checks.sh` |
