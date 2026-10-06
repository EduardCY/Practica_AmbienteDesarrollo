#!/usr/bin/env bash
# =============================================================================
# cli_checks.sh - (ejecutar en cli) Verificacion automatica end-to-end.
# No reemplaza las evidencias: sirve para comprobar el entorno antes de
# tomar capturas o de la sustentacion.
# Uso: bash /vagrant/scripts/verify/cli_checks.sh
# =============================================================================
set -uo pipefail

# shellcheck source=/dev/null
source "$HOME/.parcial2.env"
IP_SRV2_INT=192.168.50.2
PASS=0; FAIL=0
ok()  { echo "  [OK]   $*"; PASS=$((PASS+1)); }
ko()  { echo "  [FAIL] $*"; FAIL=$((FAIL+1)); }
expect_open()   { nc -z -w 3 "$1" "$2" &>/dev/null && ok "$3" || ko "$3"; }
expect_closed() { nc -z -w 3 "$1" "$2" &>/dev/null && ko "$3" || ok "$3"; }

WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT

echo "== Parte 1: Firewall / alcance"
expect_open   "$IP_PUBLICA" 21   "srv1:21 (DNAT -> srv2 FTPS) accesible"
expect_open   "$IP_PUBLICA" 2222 "srv1:2222 (DNAT -> srv2 SFTP) accesible"
expect_open   "$IP_PUBLICA" 22   "srv1:22 (SSH administracion) accesible"
expect_closed "$IP_PUBLICA" 80   "srv1:80 cerrado (sin puertos adicionales)"
expect_closed "$IP_SRV2_INT" 21  "srv2:21 NO accesible directamente"
expect_closed "$IP_SRV2_INT" 22  "srv2:22 NO accesible directamente"

echo "== Parte 1: FTPS"
S_CLIENT=$(timeout 10 openssl s_client -connect "${IP_PUBLICA}:21" -starttls ftp \
           -CAfile "$HOME/ca.crt" </dev/null 2>/dev/null)
grep -q "Verify return code: 0 (ok)" <<<"$S_CLIENT" && ok "Cadena de confianza valida (code 0)" \
  || ko "Verify return code distinto de 0"
grep -E "^(\s*Protocol|New, )" <<<"$S_CLIENT" | head -n 2 | sed 's/^/         /'

cp "$HOME/${CODIGO}.txt" "$WORK/"
lftp -u "${FTP_USER},${FTP_PASS}" "$IP_PUBLICA" -e \
  "lcd $WORK; put ${CODIGO}.txt; get ${CODIGO}.txt -o ${CODIGO}_descargado.txt; ls; bye" \
  >"$WORK/lftp.log" 2>&1
cmp -s "$WORK/${CODIGO}.txt" "$WORK/${CODIGO}_descargado.txt" \
  && ok "FTPS: subida y descarga de ${CODIGO}.txt (integridad verificada)" \
  || { ko "FTPS: transferencia fallida"; sed 's/^/         /' "$WORK/lftp.log"; }

echo "== Parte 3: SFTP"
SSH_OPTS=(-o StrictHostKeyChecking=accept-new -o BatchMode=no -o UserKnownHostsFile="$WORK/known_hosts" -o ConnectTimeout=5)
cp "$HOME/${CODIGO}_sftp.txt" "$WORK/"
cat > "$WORK/batch" <<EOF
cd archivos
put $WORK/${CODIGO}_sftp.txt
get ${CODIGO}_sftp.txt $WORK/${CODIGO}_sftp_descargado.txt
ls -l
EOF
sshpass -p "$SFTP_PASS" sftp "${SSH_OPTS[@]}" -P 2222 -b "$WORK/batch" \
  "${SFTP_USER}@${IP_PUBLICA}" >"$WORK/sftp.log" 2>&1
cmp -s "$WORK/${CODIGO}_sftp.txt" "$WORK/${CODIGO}_sftp_descargado.txt" \
  && ok "SFTP: put/get (integridad verificada)" \
  || { ko "SFTP: transferencia fallida"; sed 's/^/         /' "$WORK/sftp.log"; }

SHELL_OUT=$(sshpass -p "$SFTP_PASS" ssh "${SSH_OPTS[@]}" -p 2222 \
            "${SFTP_USER}@${IP_PUBLICA}" id 2>&1)
grep -qi "sftp connections only" <<<"$SHELL_OUT" \
  && ok "SSH con shell rechazado para ${SFTP_USER}" \
  || ko "El usuario SFTP obtuvo algo distinto al rechazo: ${SHELL_OUT}"

echo "== Parte 2: DNS sobre TLS"
grep -q "nameserver 127.0.0.53" /etc/resolv.conf && ok "/etc/resolv.conf -> stub 127.0.0.53" \
  || ko "/etc/resolv.conf no apunta al stub"
RESOLVE_OUT=$(resolvectl status 2>/dev/null || true)
grep -Eq '\+DNSOverTLS|DNS over TLS setting: yes' <<<"$RESOLVE_OUT" && ok "DoT activo en resolvectl" \
  || ko "DoT no aparece activo"
for d in uao.edu.co google.com wikipedia.org; do
  resolvectl query "$d" &>/dev/null && ok "Resuelve $d via systemd-resolved" || ko "No resuelve $d"
done

echo
echo "Resultado: ${PASS} OK / ${FAIL} FAIL"
exit $(( FAIL > 0 ))
