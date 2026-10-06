#!/usr/bin/env bash
# =============================================================================
# cli_provision.sh - Cliente Linux (cli-<codigo>)
#   - Herramientas: openssl, lftp (FTPS), sftp/sshpass, dig, tshark, nc
#   - DNS sobre TLS con systemd-resolved (Parte 2)
#   - Archivos de prueba y entorno para scripts de verificacion
# Variables (desde el Vagrantfile): CODIGO IP_PUBLICA FTP_USER FTP_PASS
#                                   SFTP_USER SFTP_PASS
# =============================================================================
set -euo pipefail

log()  { echo "=== [cli] $*"; }
warn() { echo "!!! [cli] $*" >&2; }
install_lf() { sed 's/\r$//' "$1" > "$2"; }

export DEBIAN_FRONTEND=noninteractive
HOME_V=/home/vagrant

# Why: se instalan paquetes ANTES de activar DoT; si la red bloquea 853/tcp
# (redes institucionales) la instalacion no se ve afectada.
log "Instalando herramientas"
echo "wireshark-common wireshark-common/install-setuid boolean true" | debconf-set-selections
apt-get update -y -qq
apt-get install -y -qq tshark dnsutils lftp openssl netcat-openbsd sshpass curl >/dev/null
usermod -aG wireshark vagrant

# --- CA del curso para validar el certificado FTPS ---------------------------
if [[ -f /vagrant/certs/ca.crt ]]; then
  install -m 644 -o vagrant -g vagrant /vagrant/certs/ca.crt "$HOME_V/ca.crt"
else
  warn "No existe certs/ca.crt; levante primero srv2 (vagrant up srv2) y reprovisione cli"
fi

# lftp: FTPS explicito obligatorio + validacion contra la CA
cat > "$HOME_V/.lftprc" <<EOF
set ftp:ssl-force true
set ftp:ssl-protect-data true
set ftp:ssl-protect-list true
set ftp:passive-mode true
set ssl:ca-file ${HOME_V}/ca.crt
set ssl:verify-certificate yes
EOF
chown vagrant:vagrant "$HOME_V/.lftprc"

# --- Archivos de prueba -------------------------------------------------------
echo "Archivo de prueba del estudiante ${CODIGO} - FTPS - $(date -Is)" > "$HOME_V/${CODIGO}.txt"
echo "Archivo de prueba del estudiante ${CODIGO} - SFTP - $(date -Is)" > "$HOME_V/${CODIGO}_sftp.txt"
chown vagrant:vagrant "$HOME_V/${CODIGO}.txt" "$HOME_V/${CODIGO}_sftp.txt"
mkdir -p /vagrant/captures

# Entorno para scripts/verify (credenciales de laboratorio, solo legible por vagrant)
cat > "$HOME_V/.parcial2.env" <<EOF
CODIGO=${CODIGO}
IP_PUBLICA=${IP_PUBLICA}
FTP_USER=${FTP_USER}
FTP_PASS='${FTP_PASS}'
SFTP_USER=${SFTP_USER}
SFTP_PASS='${SFTP_PASS}'
EOF
chown vagrant:vagrant "$HOME_V/.parcial2.env"; chmod 600 "$HOME_V/.parcial2.env"

# --- DNS sobre TLS ------------------------------------------------------------
# Why: el DHCP de la NAT de VirtualBox entrega un DNS por enlace (10.0.2.3) que
# competiria con los resolvers DoT globales. Se le indica a netplan que lo ignore.
log "Deshabilitando DNS entregado por DHCP en eth0"
cat > /etc/netplan/99-parcial2-no-dhcp-dns.yaml <<'EOF'
network:
  version: 2
  ethernets:
    eth0:
      dhcp4-overrides:
        use-dns: false
EOF
chmod 600 /etc/netplan/*.yaml
netplan apply

log "Instalando /etc/systemd/resolved.conf (DNSOverTLS=yes)"
[[ -f /etc/systemd/resolved.conf.orig ]] || cp /etc/systemd/resolved.conf /etc/systemd/resolved.conf.orig
install_lf /vagrant/config/cli/resolved.conf /etc/systemd/resolved.conf
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
systemctl restart systemd-resolved
resolvectl flush-caches

log "Comprobacion rapida"
grep nameserver /etc/resolv.conf
resolvectl status | sed -n '1,12p'
resolvectl query uao.edu.co || warn "Fallo DoT: la red podria bloquear 853/tcp (ver README, Solucion de problemas)"
