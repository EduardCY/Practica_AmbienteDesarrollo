#!/usr/bin/env bash
# =============================================================================
# dot_mode.sh - (ejecutar en cli) Cambia el modo DNSOverTLS de systemd-resolved.
# Puntos 13 y 14: comparar yes / no / opportunistic.
# Uso: sudo bash /vagrant/scripts/demo/dot_mode.sh {yes|no|opportunistic|status}
# =============================================================================
set -euo pipefail
CONF=/etc/systemd/resolved.conf
MODE="${1:-status}"

case "$MODE" in
  yes|no|opportunistic)
    sed -i "s/^#\?DNSOverTLS=.*/DNSOverTLS=${MODE}/" "$CONF"
    systemctl restart systemd-resolved
    resolvectl flush-caches
    echo ">> DNSOverTLS=${MODE} aplicado y cache limpiada";;
  status) ;;
  *) echo "Uso: $0 {yes|no|opportunistic|status}" >&2; exit 2;;
esac

grep -E '^(DNS|FallbackDNS|DNSOverTLS)=' "$CONF"
resolvectl status | grep -E 'Protocols|DNS over TLS|Current DNS Server|DNS Servers' || true
