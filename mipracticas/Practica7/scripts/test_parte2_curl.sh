#!/usr/bin/env bash
# =============================================================================
# PRUEBAS DE ACTUALIZACIÓN CON CURL — PARTE 2: API REST UBIDOTS
# =============================================================================
# Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
# Práctica 7: Punto 3 de la guía oficial
# =============================================================================

TOKEN="${UBIDOTS_TOKEN:-BBFF-demoTokenPlaceholder}"
DEVICE="${UBIDOTS_DEVICE_LABEL:-machine}"
BASE_URL="${UBIDOTS_BASE_URL:-http://industrial.api.ubidots.com}"

echo "======================================================================"
echo " PARTE 2: ENVÍO Y ACTUALIZACIÓN DE VARIABLES EN UBIDOTS CON CURL"
echo " Dispositivo: ${DEVICE}"
echo " Endpoint:    ${BASE_URL}/api/v1.6/devices/${DEVICE}"
echo "======================================================================"

echo -e "\n--- Prueba 1: Actualizar variable 'temperature' vía cabecera X-Auth-Token ---"
curl -i -s --header "Content-Type: application/json" \
  -H "X-Auth-Token: ${TOKEN}" \
  --request POST \
  --data '{"temperature": 28.5}' \
  "${BASE_URL}/api/v1.6/devices/${DEVICE}"

echo -e "\n\n--- Prueba 2: Actualizar múltiples variables (incluyendo las 2 nuevas) ---"
curl -i -s --header "Content-Type: application/json" \
  -H "X-Auth-Token: ${TOKEN}" \
  --request POST \
  --data '{"temperature": 42.0, "humidity": 65, "pressure": 1013.25, "battery_level": 92}' \
  "${BASE_URL}/api/v1.6/devices/${DEVICE}"

echo -e "\n\n--- Prueba 3: Sintaxis alternativa de la guía con token por Query Param (?token=...) ---"
curl -i -s -H "Content-Type: application/json" \
  -X POST \
  -d '{"temperature": 31.0}' \
  "${BASE_URL}/api/v1.6/devices/${DEVICE}/?token=${TOKEN}"

echo -e "\n\n======================================================================"
echo " PRUEBAS CURL HACIA UBIDOTS COMPLETADAS"
echo "======================================================================"
