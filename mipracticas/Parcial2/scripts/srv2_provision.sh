#!/usr/bin/env bash
# =============================================================================
# srv2_provision.sh - Servidor 2 (srv2-<codigo>)
#   1) PKI: reutiliza la CA/certificado del curso (certs/) o los genera
#   2) vsftpd en modo FTPS (TLS explicito) - Parte 1
#   3) OpenSSH con usuario SFTP enjaulado     - Parte 3
# Variables (desde el Vagrantfile): CODIGO IP_PUBLICA IP_SRV2 FTP_USER FTP_PASS
#                                   SFTP_USER SFTP_PASS
# =============================================================================
set -euo pipefail

log()  { echo "=== [srv2] $*"; }
warn() { echo "!!! [srv2] $*" >&2; }

# Why: los archivos del repo pueden llegar con CRLF desde Windows (git autocrlf);
# los demonios Linux fallan con '\r' al final de cada linea.
install_lf() { sed 's/\r$//' "$1" > "$2"; }

CERT_DIR=/vagrant/certs
CONF_DIR=/vagrant/config/srv2
export DEBIAN_FRONTEND=noninteractive

log "Instalando paquetes"
apt-get update -y -qq
apt-get install -y -qq vsftpd openssl openssh-server >/dev/null

# --- Evitar colision de rutas DHCP con la red interna -----------------------
cat <<'EOF' > /etc/netplan/99-fix-dhcp.yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
      dhcp4-overrides:
        use-dns: false
    eth0:
      dhcp4: true
      dhcp4-overrides:
        use-dns: false
EOF
chmod 600 /etc/netplan/99-fix-dhcp.yaml
netplan apply 2>/dev/null || true
ip route del 192.168.50.3 via 10.0.2.2 dev eth0 2>/dev/null || true

# -----------------------------------------------------------------------------
# 1) PKI
# -----------------------------------------------------------------------------
mkdir -p "$CERT_DIR"
if [[ -f $CERT_DIR/ca.crt && -f $CERT_DIR/servidor.crt && -f $CERT_DIR/servidor.key ]]; then
  log "Reutilizando CA y certificado existentes en certs/ (generados en clase)"
else
  log "No se encontro la PKI de clase en certs/; generando CA + certificado de servidor"
  TMP=$(mktemp -d)
  # CA raiz
  openssl req -x509 -new -nodes -newkey rsa:4096 -sha256 -days 3650 \
    -keyout "$TMP/ca.key" -out "$TMP/ca.crt" \
    -subj "/C=CO/ST=Valle del Cauca/L=Cali/O=UAO/OU=Servicios Telematicos/CN=CA Servicios Telematicos ${CODIGO}"
  # Clave + CSR del servidor
  openssl req -new -nodes -newkey rsa:2048 -sha256 \
    -keyout "$TMP/servidor.key" -out "$TMP/servidor.csr" \
    -subj "/C=CO/ST=Valle del Cauca/L=Cali/O=UAO/OU=Servicios Telematicos/CN=srv2-${CODIGO}"
  # Why SAN con la IP publica: el cliente se conecta a srv1 (DNAT); la
  # verificacion de nombre debe coincidir con la direccion que usa el cliente.
  cat > "$TMP/servidor.ext" <<EOF
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=IP:${IP_PUBLICA},DNS:srv2-${CODIGO},DNS:srv1-${CODIGO}
EOF
  openssl x509 -req -in "$TMP/servidor.csr" -CA "$TMP/ca.crt" -CAkey "$TMP/ca.key" \
    -CAcreateserial -out "$TMP/servidor.crt" -days 825 -sha256 -extfile "$TMP/servidor.ext"
  cp "$TMP"/ca.crt "$TMP"/ca.key "$TMP"/servidor.crt "$TMP"/servidor.key "$CERT_DIR"/
  rm -rf "$TMP"
fi

install -m 644 -o root -g root "$CERT_DIR/servidor.crt" /etc/ssl/certs/servidor.crt
install -m 600 -o root -g root "$CERT_DIR/servidor.key" /etc/ssl/private/servidor.key

openssl verify -CAfile "$CERT_DIR/ca.crt" /etc/ssl/certs/servidor.crt \
  || warn "servidor.crt NO esta firmado por ca.crt (revise la PKI de clase)"
openssl x509 -in /etc/ssl/certs/servidor.crt -noout -subject -issuer -dates -fingerprint -sha256 \
  | tee "$CERT_DIR/servidor_fingerprint.txt"

# -----------------------------------------------------------------------------
# 2) vsftpd - FTPS
# -----------------------------------------------------------------------------
log "Creando usuario FTP ${FTP_USER}"
id "$FTP_USER" &>/dev/null || useradd -m -s /bin/bash "$FTP_USER"
echo "${FTP_USER}:${FTP_PASS}" | chpasswd
echo "Archivo de bienvenida en srv2-${CODIGO} (FTPS)" > "/home/${FTP_USER}/bienvenida.txt"
chown "${FTP_USER}:${FTP_USER}" "/home/${FTP_USER}/bienvenida.txt"
echo "$FTP_USER" > /etc/vsftpd.userlist

log "Instalando /etc/vsftpd.conf"
[[ -f /etc/vsftpd.conf.orig ]] || cp /etc/vsftpd.conf /etc/vsftpd.conf.orig
install_lf "$CONF_DIR/vsftpd.conf" /etc/vsftpd.conf
grep -q "^pasv_address=${IP_PUBLICA}$" /etc/vsftpd.conf \
  || warn "pasv_address en vsftpd.conf no coincide con IP_PUBLICA=${IP_PUBLICA}"
mkdir -p /var/run/vsftpd/empty

systemctl enable vsftpd >/dev/null
systemctl restart vsftpd
if ! systemctl is-active --quiet vsftpd; then
  journalctl -u vsftpd --no-pager -n 30 >&2
  warn "vsftpd no arranco; revise el log anterior"; exit 1
fi

# -----------------------------------------------------------------------------
# 3) OpenSSH - SFTP con chroot
# -----------------------------------------------------------------------------
log "Creando usuario SFTP ${SFTP_USER} (sin shell, enjaulado)"
id "$SFTP_USER" &>/dev/null || useradd -m -s /usr/sbin/nologin "$SFTP_USER"
echo "${SFTP_USER}:${SFTP_PASS}" | chpasswd
# Why: sshd exige que la raiz del chroot y sus padres sean root:root y no
# escribibles por otros; la escritura del usuario va en un subdirectorio.
chown root:root "/home/${SFTP_USER}"
chmod 755 "/home/${SFTP_USER}"
mkdir -p "/home/${SFTP_USER}/archivos"
chown "${SFTP_USER}:${SFTP_USER}" "/home/${SFTP_USER}/archivos"
chmod 750 "/home/${SFTP_USER}/archivos"
echo "Archivo de bienvenida en srv2-${CODIGO} (SFTP)" > "/home/${SFTP_USER}/archivos/bienvenida_sftp.txt"
chown "${SFTP_USER}:${SFTP_USER}" "/home/${SFTP_USER}/archivos/bienvenida_sftp.txt"

log "Instalando /etc/ssh/sshd_config (validado antes de reiniciar)"
ssh-keygen -A >/dev/null
mkdir -p /run/sshd
[[ -f /etc/ssh/sshd_config.orig ]] || cp /etc/ssh/sshd_config /etc/ssh/sshd_config.orig
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
install_lf "$CONF_DIR/sshd_config" /etc/ssh/sshd_config
grep -q "^Match User ${SFTP_USER}$" /etc/ssh/sshd_config \
  || warn "sshd_config no contiene 'Match User ${SFTP_USER}' (revise CODIGO)"

# Why: un sshd_config invalido dejaria la VM sin acceso SSH (lockout).
if sshd -t -f /etc/ssh/sshd_config; then
  systemctl restart ssh
else
  warn "sshd_config invalido; restaurando la version anterior"
  cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config
  systemctl restart ssh
  exit 1
fi

# Huellas de las claves de host (para comparar en la primera conexion SFTP, punto 17)
for k in /etc/ssh/ssh_host_*_key.pub; do ssh-keygen -lf "$k"; done | tee "$CERT_DIR/srv2_hostkeys_fingerprint.txt"

log "Listo: vsftpd (21, pasv 50000-50010) y sshd (22) en ${IP_SRV2}"
ss -tlnp | grep -E ':(21|22)\s' || true
