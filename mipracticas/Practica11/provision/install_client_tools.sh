#!/usr/bin/env bash
# =============================================================================
# SCRIPT DE APROVISIONAMIENTO DESATENDIDO — VM2: CLIENTE / AUDITOR
# =============================================================================
# Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
# Estudiante: Eduard Criollo Yule (Código: 2220335)
# Universidad Autónoma de Occidente
#
# Diseñado para ejecutarse como User Data en AWS EC2 o ejecutarse manualmente:
#   sudo bash install_client_tools.sh
# =============================================================================

set -Eeuo pipefail

LOG_FILE="/var/log/practica11-provision.log"
exec > >(tee -a "$LOG_FILE") 2>&1

trap 'echo "[ERROR] Falló en línea $LINENO durante la ejecución del comando: $BASH_COMMAND" >&2; exit 1' ERR

START_TIME=$SECONDS

echo "======================================================================"
echo "[PRÁCTICA 11] Iniciando aprovisionamiento en VM2 (Cliente / Auditor)..."
echo "Fecha y hora: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "======================================================================"

REPO_URL="${REPO_URL:-https://github.com/EduardCY/Practica_AmbienteDesarrollo.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"

export DEBIAN_FRONTEND=noninteractive

echo "[1/4] Instalando herramientas de diagnóstico y auditoría (net-tools, curl, jq, git)..."
apt-get -o DPkg::Lock::Timeout=120 -qq update
apt-get -o DPkg::Lock::Timeout=120 -qq install -y --no-install-recommends \
    net-tools \
    curl \
    jq \
    git \
    apache2-utils

# Opcional: Apache en VM2 para paridad con la guía
if [[ "${INSTALL_APACHE:-1}" == "1" ]]; then
    apt-get -o DPkg::Lock::Timeout=120 -qq install -y --no-install-recommends apache2
fi

# -----------------------------------------------------------------------------
# 2. Descarga del repositorio de scripts en el home de ubuntu
# -----------------------------------------------------------------------------
echo "[2/4] Preparando scripts de pruebas y auditoría para el usuario ubuntu..."
UBUNTU_HOME="/home/ubuntu"
TARGET_DIR="$UBUNTU_HOME/Practica11"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo "/nonexistent")"

if [[ -d "$SCRIPT_DIR/../scripts" ]]; then
    echo "-> Modo B detectado: Copiando scripts desde directorio local..."
    mkdir -p "$TARGET_DIR"
    cp -rT "$SCRIPT_DIR/.." "$TARGET_DIR"
else
    echo "-> Modo A detectado: Descargando scripts desde GitHub ($REPO_URL)..."
    TMP_DIR="$(mktemp -d)"
    git clone --depth 1 --filter=blob:none --sparse -b "$REPO_BRANCH" "$REPO_URL" "$TMP_DIR/repo"
    git -C "$TMP_DIR/repo" sparse-checkout set mipracticas/Practica11
    mkdir -p "$TARGET_DIR"
    cp -rT "$TMP_DIR/repo/mipracticas/Practica11" "$TARGET_DIR"
fi

if id -u ubuntu &>/dev/null; then
    chown -R ubuntu:ubuntu "$TARGET_DIR"
    chmod +x "$TARGET_DIR"/scripts/*.sh 2>/dev/null || true
fi

# -----------------------------------------------------------------------------
# 3. Metadatos IMDSv2 y Landing de Apache para VM2 (si Apache está instalado)
# -----------------------------------------------------------------------------
if dpkg -s apache2 &>/dev/null; then
    echo "[3/4] Generando landing page informativa de Apache en VM2..."
    INSTANCE_ID="i-local"
    AZ="local-az"
    PRIVATE_IP="$(hostname -I | awk '{print $1}')"
    PUBLIC_IP="$PRIVATE_IP"

    TOKEN="$(curl -fsS -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60" --max-time 1 2>/dev/null || echo "")"
    if [[ -n "$TOKEN" ]]; then
        INSTANCE_ID="$(curl -fsS -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/instance-id" --max-time 1 2>/dev/null || echo "i-ec2")"
        AZ="$(curl -fsS -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/placement/availability-zone" --max-time 1 2>/dev/null || echo "us-east-1")"
        PRIVATE_IP="$(curl -fsS -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/local-ipv4" --max-time 1 2>/dev/null || echo "$PRIVATE_IP")"
        PUBLIC_IP="$(curl -fsS -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/public-ipv4" --max-time 1 2>/dev/null || echo "$PRIVATE_IP")"
    fi

    LANDING_SRC="$TARGET_DIR/provision/index.html"
    if [[ -f "$LANDING_SRC" ]]; then
        sed -e "s|{{ROLE}}|VM2 — Cliente / Auditor (Apache Web Server)|g" \
            -e "s|{{INSTANCE_ID}}|$INSTANCE_ID|g" \
            -e "s|{{AZ}}|$AZ|g" \
            -e "s|{{PRIVATE_IP}}|$PRIVATE_IP|g" \
            -e "s|{{PUBLIC_IP}}|$PUBLIC_IP|g" \
            "$LANDING_SRC" > /var/www/html/index.html
    fi

    systemctl restart apache2
else
    echo "[3/4] Apache2 no instalado en VM2, omitiendo configuración de landing."
fi

ELAPSED=$((SECONDS - START_TIME))
echo "======================================================================"
echo "PROVISION_OK elapsed=${ELAPSED}s"
echo "VM2 Cliente y herramientas listos en ${ELAPSED} segundos."
echo "Para auditar VM1 ejecute: $TARGET_DIR/scripts/test_api_from_vm2.sh <IP_VM1> [PUERTO]"
echo "======================================================================"
exit 0
