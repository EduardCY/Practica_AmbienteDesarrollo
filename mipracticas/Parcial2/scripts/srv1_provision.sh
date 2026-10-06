#!/usr/bin/env bash
# =============================================================================
# srv1_provision.sh - Servidor 1 (srv1-<codigo>)
#   UFW como unico punto de entrada: deny incoming / deny routed,
#   ip_forward, DNAT (before.rules) y reglas "route" minimas.
# Variables (desde el Vagrantfile): CODIGO IP_PUBLICA IP_SRV2
# =============================================================================
set -euo pipefail

log()  { echo "=== [srv1] $*"; }
warn() { echo "!!! [srv1] $*" >&2; }
install_lf() { sed 's/\r$//' "$1" > "$2"; }

export DEBIAN_FRONTEND=noninteractive

log "Instalando paquetes"
apt-get update -y -qq
apt-get install -y -qq ufw netcat-openbsd >/dev/null

# Why reset primero: "ufw reset" restaura before.rules a la plantilla; por eso
# el archivo del parcial se copia DESPUES del reset.
log "Reiniciando UFW a valores de fabrica"
ufw --force reset >/dev/null

# --- Reenvio IP en el kernel (persistente) -----------------------------------
log "Habilitando net.ipv4.ip_forward"
echo 'net.ipv4.ip_forward=1' > /etc/sysctl.d/99-parcial2-forward.conf
sysctl -q -p /etc/sysctl.d/99-parcial2-forward.conf
# UFW reaplica /etc/ufw/sysctl.conf al habilitarse; si queda comentado lo pondria en 0.
sed -i 's|^#\s*net/ipv4/ip_forward=1|net/ipv4/ip_forward=1|' /etc/ufw/sysctl.conf

# --- Reglas NAT -------------------------------------------------------------
log "Instalando /etc/ufw/before.rules (DNAT 21, 50000:50010, 2222->22)"
install_lf /vagrant/config/srv1/before.rules /etc/ufw/before.rules
chmod 640 /etc/ufw/before.rules
grep -q -- "-d ${IP_PUBLICA} " /etc/ufw/before.rules \
  || warn "before.rules no usa IP_PUBLICA=${IP_PUBLICA}"

# --- Politicas y reglas -----------------------------------------------------
log "Aplicando politicas por defecto y reglas minimas"
ufw default deny incoming
ufw default deny routed          # => DEFAULT_FORWARD_POLICY="DROP"
ufw default allow outgoing
ufw logging low

# Punto 2: unico puerto local abierto en srv1
ufw allow 22/tcp comment 'SSH administracion srv1'
# Punto 2: unicamente lo necesario hacia srv2
ufw route allow proto tcp from any to "${IP_SRV2}" port 21 comment 'FTPS control -> srv2'
ufw route allow proto tcp from any to "${IP_SRV2}" port 50000:50010 comment 'FTPS pasivo -> srv2'
# Punto 16: SFTP publicado en 2222 (tras DNAT el destino real es srv2:22)
ufw route allow proto tcp from any to "${IP_SRV2}" port 22 comment 'SFTP 2222 -> srv2:22'

ufw --force enable
systemctl enable ufw >/dev/null

log "Estado final"
sysctl net.ipv4.ip_forward
ufw status verbose
iptables -t nat -L PREROUTING -n -v --line-numbers
