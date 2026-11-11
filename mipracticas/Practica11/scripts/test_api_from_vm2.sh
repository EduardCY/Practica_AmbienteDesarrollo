#!/usr/bin/env bash
# =============================================================================
# SCRIPT DE AUDITORÍA AUTOMATIZADA — PUNTO 4.a (CONSUMO DESDE VM2 HACIA VM1)
# =============================================================================
# Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
# Estudiante: Eduard Criollo Yule (Código: 2220335)
#
# Uso:
#   ./test_api_from_vm2.sh <IP_DESTINO_VM1> [PUERTO]
#
# Ejemplos:
#   ./test_api_from_vm2.sh 172.31.16.58 5000       # Prueba por IP privada (Gunicorn)
#   ./test_api_from_vm2.sh 52.91.99.132 5000       # Prueba por IP pública (Gunicorn)
#   ./test_api_from_vm2.sh 172.31.16.58 80         # Prueba por IP privada (Proxy Apache)
# =============================================================================

set -eo pipefail

TARGET_IP="${1:-}"
PORT="${2:-5000}"

if [[ -z "$TARGET_IP" ]]; then
    echo "Uso: $0 <IP_DESTINO_VM1> [PUERTO (por defecto: 5000)]" >&2
    echo "Ejemplo: $0 172.31.16.58 5000" >&2
    exit 1
fi

BASE_URL="http://${TARGET_IP}:${PORT}"

echo "======================================================================"
echo "AUDITORÍA PUNTO 4.a: Consumo de API REST desde VM2 hacia VM1"
echo "Destino evaluado: $BASE_URL"
echo "Fecha y hora:     $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "======================================================================"

TOTAL_TESTS=0
PASSED_TESTS=0

run_test() {
    local test_name="$1"
    local expected_code="$2"
    local http_method="$3"
    local endpoint="$4"
    local data="${5:-}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "[$TOTAL_TESTS] $test_name ... "

    local response_file
    response_file="$(mktemp)"

    local http_code
    if [[ -n "$data" ]]; then
        http_code="$(curl -s -o "$response_file" -w "%{http_code}" -X "$http_method" \
            "${BASE_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data" --connect-timeout 5 --max-time 10 || echo "000")"
    else
        http_code="$(curl -s -o "$response_file" -w "%{http_code}" -X "$http_method" \
            "${BASE_URL}${endpoint}" --connect-timeout 5 --max-time 10 || echo "000")"
    fi

    if [[ "$http_code" == "$expected_code" ]]; then
        echo "PASS (HTTP $http_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        cat "$response_file" | jq -C '.' 2>/dev/null || cat "$response_file"
        echo ""
        rm -f "$response_file"
        return 0
    else
        echo "FAIL (Esperado: HTTP $expected_code | Obtenido: HTTP $http_code)"
        cat "$response_file" | head -n 10
        echo ""
        rm -f "$response_file"
        return 1
    fi
}

# 1. Health-check
run_test "GET /api/health (Auditoría de estado)" "200" "GET" "/api/health"

# 2. Listar productos existentes
run_test "GET /api/products (Listar inventario)" "200" "GET" "/api/products"

# 3. Crear nuevo producto vía POST
echo "[Creando producto de prueba vía POST...]"
CREATE_RES="$(curl -s -X POST "${BASE_URL}/api/products" \
    -H "Content-Type: application/json" \
    -d '{"name":"Sensor IoT AWS VM2","description":"Dispositivo auditado desde VM2","price":149.99,"stock":15}')"

NEW_ID="$(echo "$CREATE_RES" | jq -r '.id // empty' 2>/dev/null || echo "")"

if [[ -n "$NEW_ID" && "$NEW_ID" != "null" ]]; then
    echo "-> Producto creado con éxito (ID asignado: $NEW_ID)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "-> [ERROR] No se pudo obtener el ID del producto creado:"
    echo "$CREATE_RES"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

if [[ -n "$NEW_ID" && "$NEW_ID" != "null" ]]; then
    # 4. Consultar producto recién creado
    run_test "GET /api/products/$NEW_ID (Verificar persistencia)" "200" "GET" "/api/products/$NEW_ID"

    # 5. Actualizar producto vía PUT
    run_test "PUT /api/products/$NEW_ID (Modificar stock y precio)" "200" "PUT" "/api/products/$NEW_ID" \
        '{"name":"Sensor IoT AWS VM2 - Modificado","price":179.99,"stock":25}'

    # 6. Eliminar producto vía DELETE
    run_test "DELETE /api/products/$NEW_ID (Eliminación)" "200" "DELETE" "/api/products/$NEW_ID"

    # 7. Validar que retorne 404 tras ser eliminado
    run_test "GET /api/products/$NEW_ID (Confirmar 404 Not Found)" "404" "GET" "/api/products/$NEW_ID"
fi

echo "======================================================================"
echo "RESUMEN DE AUDITORÍA: $PASSED_TESTS de $TOTAL_TESTS pruebas pasadas."
if [[ $PASSED_TESTS -eq $TOTAL_TESTS ]]; then
    echo "RESULTADO: AUDITORÍA PUNTO 4.a EXITOSA (100% PASS)"
    exit 0
else
    echo "RESULTADO: FALLARON ALGUNAS PRUEBAS"
    exit 1
fi
