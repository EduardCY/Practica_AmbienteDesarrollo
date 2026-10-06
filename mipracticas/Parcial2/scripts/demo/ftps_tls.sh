#!/usr/bin/env bash
# =============================================================================
# ftps_tls.sh - (ejecutar en srv2) Activa/desactiva TLS en vsftpd.
# Punto 9: capturar primero una sesion FTP PLANA y luego una FTPS.
# Uso: sudo bash /vagrant/scripts/demo/ftps_tls.sh {on|off|status}
# =============================================================================
set -euo pipefail
CONF=/etc/vsftpd.conf

case "${1:-status}" in
  off) sed -i 's/^ssl_enable=.*/ssl_enable=NO/' "$CONF"
       echo ">> TLS DESHABILITADO (FTP plano) - SOLO para la captura del punto 9";;
  on)  sed -i 's/^ssl_enable=.*/ssl_enable=YES/' "$CONF"
       echo ">> TLS HABILITADO (FTPS explicito obligatorio)";;
  status) ;;
  *) echo "Uso: $0 {on|off|status}" >&2; exit 2;;
esac

[[ ${1:-status} == status ]] || systemctl restart vsftpd
grep -E '^(ssl_enable|force_local_logins_ssl|force_local_data_ssl|pasv_(min|max)_port|pasv_address)=' "$CONF"
systemctl is-active vsftpd
