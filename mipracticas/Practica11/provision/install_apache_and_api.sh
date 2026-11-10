#!/usr/bin/env bash
# =============================================================================
# SCRIPT DE APROVISIONAMIENTO DESATENDIDO — VM1: APACHE + API REST FLASK
# =============================================================================
# Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
# Estudiante: Eduard Criollo Yule (Código: 2220335)
# Universidad Autónoma de Occidente
#
# Diseñado para ejecutarse como User Data en AWS EC2 (cloud-init, usuario root)
# o ejecutarse manualmente tras la instalación guiada de Apache mediante:
#   sudo bash install_apache_and_api.sh
# Tiempo estimado de ejecución en EC2 t2.micro: ~25 a 45 segundos (< 60s).
# =============================================================================

# Por qué set -Eeuo pipefail:
# Aborta inmediatamente ante cualquier comando que falle, variable no definida
# o fallo en pipelines, evitando dejar el servidor en un estado inconsistente.
set -Eeuo pipefail

LOG_FILE="/var/log/practica11-provision.log"
exec > >(tee -a "$LOG_FILE") 2>&1

trap 'echo "[ERROR] Falló en línea $LINENO durante la ejecución del comando: $BASH_COMMAND" >&2; exit 1' ERR

START_TIME=$SECONDS

echo "======================================================================"
echo "[PRÁCTICA 11] Iniciando aprovisionamiento del API REST en VM1..."
echo "Fecha y hora: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "======================================================================"

# Parámetros del repositorio (sobreescribibles por variables de entorno)
REPO_URL="${REPO_URL:-https://github.com/EduardCY/Practica_AmbienteDesarrollo.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"
APP_ROOT="/opt/practica11"
DATA_DIR="/var/lib/practica11"
SVC_USER="practica11"

export DEBIAN_FRONTEND=noninteractive

# Por qué DPkg::Lock::Timeout=120:
# En el primer arranque de una instancia Ubuntu en AWS, el servicio unattended-upgrades
# o apt-daily suele bloquear temporalmente /var/lib/dpkg/lock-frontend.
echo "[1/7] Verificando dependencias base (Apache2, net-tools, Python3, venv, curl, jq)..."
apt-get -o DPkg::Lock::Timeout=120 -qq update
apt-get -o DPkg::Lock::Timeout=120 -qq install -y --no-install-recommends \
    apache2 \
    net-tools \
    python3-venv \
    python3-pip \
    git \
    curl \
    jq

if dpkg -s apache2 &>/dev/null; then
    echo "-> Servidor Apache2 detectado y verificado (instalación manual o empaquetada confirmada)."
fi

# -----------------------------------------------------------------------------
# 2. Obtención de los artefactos de la aplicación (Modo Híbrido: Local o Git)
# -----------------------------------------------------------------------------
echo "[2/7] Obteniendo código fuente de la Práctica 11..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo "/nonexistent")"

if [[ -d "$SCRIPT_DIR/../api" ]]; then
    echo "-> Modo B detectado: Utilizando código fuente copiado localmente ($SCRIPT_DIR/..)"
    SRC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
else
    echo "-> Modo A detectado: Descargando desde repositorio remoto ($REPO_URL | rama: $REPO_BRANCH)"
    TMP_DIR="$(mktemp -d)"
    git clone --depth 1 --filter=blob:none --sparse -b "$REPO_BRANCH" "$REPO_URL" "$TMP_DIR/repo"
    git -C "$TMP_DIR/repo" sparse-checkout set mipracticas/Practica11
    SRC_DIR="$TMP_DIR/repo/mipracticas/Practica11"
fi

# -----------------------------------------------------------------------------
# 3. Creación de usuario de servicio y despliegue del entorno virtual
# -----------------------------------------------------------------------------
echo "[3/7] Configurando usuario de servicio, permisos y entorno virtual Python..."
if ! id -u "$SVC_USER" &>/dev/null; then
    # Usuario de sistema sin login ni home para cumplir con principio de mínimo privilegio
    useradd --system --no-create-home --shell /usr/sbin/nologin "$SVC_USER"
fi

install -d -o "$SVC_USER" -g "$SVC_USER" -m 0750 "$DATA_DIR"
install -d -o root -g root -m 0755 "$APP_ROOT"

# Desplegar árbol de la API
rm -rf "$APP_ROOT/api"
cp -rT "$SRC_DIR/api" "$APP_ROOT/api"
chown -R root:root "$APP_ROOT/api"

# Crear entorno virtual e instalar dependencias
if [[ ! -d "$APP_ROOT/venv" ]]; then
    python3 -m venv "$APP_ROOT/venv"
fi

echo "-> Instalando dependencias de Python (Flask, Gunicorn, SQLAlchemy)..."
"$APP_ROOT/venv/bin/pip" install -q --no-cache-dir --disable-pip-version-check -r "$APP_ROOT/api/requirements.txt"

# -----------------------------------------------------------------------------
# 4. Configuración del servicio systemd para Gunicorn
# -----------------------------------------------------------------------------
echo "[4/7] Instalando y activando servicio systemd (practica11-api)..."
install -m 0644 "$SRC_DIR/provision/practica11-api.service" /etc/systemd/system/practica11-api.service

systemctl daemon-reload
systemctl enable practica11-api.service
systemctl restart practica11-api.service

# -----------------------------------------------------------------------------
# 5. Configuración de Apache 2.4 y Proxy Inverso
# -----------------------------------------------------------------------------
echo "[5/7] Configurando servidor web Apache y módulos de proxy inverso..."
a2enmod -q proxy proxy_http headers

install -m 0644 "$SRC_DIR/provision/000-default.conf" /etc/apache2/sites-available/000-default.conf

# -----------------------------------------------------------------------------
# 6. Extracción de metadatos IMDSv2 y generación de la página de inicio
# -----------------------------------------------------------------------------
echo "[6/7] Consultando metadatos de AWS EC2 vía IMDSv2 y generando landing..."

INSTANCE_ID="i-local"
AZ="local-az"
PRIVATE_IP="$(hostname -I | awk '{print $1}')"
PUBLIC_IP="$PRIVATE_IP"

# Intentar consultar IMDSv2 con timeout corto (1 segundo)
TOKEN="$(curl -fsS -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60" --max-time 1 2>/dev/null || echo "")"
if [[ -n "$TOKEN" ]]; then
    INSTANCE_ID="$(curl -fsS -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/instance-id" --max-time 1 2>/dev/null || echo "i-ec2")"
    AZ="$(curl -fsS -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/placement/availability-zone" --max-time 1 2>/dev/null || echo "us-east-1")"
    PRIVATE_IP="$(curl -fsS -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/local-ipv4" --max-time 1 2>/dev/null || echo "$PRIVATE_IP")"
    PUBLIC_IP="$(curl -fsS -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/public-ipv4" --max-time 1 2>/dev/null || echo "$PRIVATE_IP")"
fi

sed -e "s|{{ROLE}}|VM1 — Servidor Web Apache + API REST Flask|g" \
    -e "s|{{INSTANCE_ID}}|$INSTANCE_ID|g" \
    -e "s|{{AZ}}|$AZ|g" \
    -e "s|{{PRIVATE_IP}}|$PRIVATE_IP|g" \
    -e "s|{{PUBLIC_IP}}|$PUBLIC_IP|g" \
    "$SRC_DIR/provision/index.html" > /var/www/html/index.html

systemctl restart apache2

# -----------------------------------------------------------------------------
# 7. Verificación de salud del microservicio (Health-Check)
# -----------------------------------------------------------------------------
echo "[7/7] Verificando disponibilidad del microservicio en http://127.0.0.1:5000/api/health..."
HEALTHY=0
for i in {1..15}; do
    if curl -fsS "http://127.0.0.1:5000/api/health" &>/dev/null; then
        HEALTHY=1
        break
    fi
    sleep 1
done

if [[ $HEALTHY -eq 0 ]]; then
    echo "[ERROR] El microservicio no respondió al health-check tras 15 segundos." >&2
    systemctl status practica11-api.service --no-pager >&2 || true
    journalctl -u practica11-api.service -n 20 --no-pager >&2 || true
    exit 1
fi

ELAPSED=$((SECONDS - START_TIME))
echo "======================================================================"
echo "PROVISION_OK elapsed=${ELAPSED}s"
echo "VM1 Servidor Web y API REST configurados exitosamente en ${ELAPSED} segundos."
echo "API nativa:   http://0.0.0.0:5000/api/products"
echo "Proxy Apache: http://0.0.0.0:80/api/products"
echo "======================================================================"
exit 0
