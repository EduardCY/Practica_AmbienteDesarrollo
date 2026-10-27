#!/usr/bin/env bash
# =============================================================================
# SCRIPT DE AUDITORÍA Y PRUEBAS AUTOMATIZADAS CON CURL — PRÁCTICA 9
# =============================================================================
# Valida todos los endpoints CRUD de Usuarios (/api/users) y Productos (/api/products),
# así como el despliegue productivo en Apache2 + mod_wsgi (Puerto 80).

set -e

FLASK_URL="${1:-http://localhost:5000}"
APACHE_URL="${2:-http://localhost}"

echo "=========================================================================="
echo " 1. PRUEBAS CRUD API REST DE USUARIOS (/api/users) — EJERCICIO 3.a"
echo "=========================================================================="

echo -e "\n[1.1] GET /api/users (Listar usuarios):"
curl -i -s "$FLASK_URL/api/users"

echo -e "\n\n[1.2] GET /api/users/1 (Consultar usuario ID 1):"
curl -i -s "$FLASK_URL/api/users/1"

echo -e "\n\n[1.3] POST /api/users (Crear usuario 'Eduard Criollo'):"
curl -i -s -H "Content-Type: application/json" -X POST \
  -d '{"name":"Eduard Criollo","email":"eduard.criollo@uao.edu.co","username":"ecriollo","password":"789"}' \
  "$FLASK_URL/api/users"

echo -e "\n\n[1.4] PUT /api/users/2 (Actualizar usuario ID 2):"
curl -i -s -H "Content-Type: application/json" -X PUT \
  -d '{"name":"Maria Fernanda","email":"maria.fernanda@gmail.com","username":"mariaf","password":"456"}' \
  "$FLASK_URL/api/users/2"

echo -e "\n\n[1.5] DELETE /api/users/3 (Eliminar usuario recién creado):"
curl -i -s -X DELETE "$FLASK_URL/api/users/3"

echo -e "\n\n[1.6] GET /api/users/99 (Validar error 404 Not Found):"
curl -i -s "$FLASK_URL/api/users/99"

echo -e "\n\n=========================================================================="
echo " 2. PRUEBAS CRUD API REST DE PRODUCTOS (/api/products) — EJERCICIO 5.b"
echo "=========================================================================="

echo -e "\n[2.1] GET /api/products (Listar productos):"
curl -i -s "$FLASK_URL/api/products"

echo -e "\n\n[2.2] GET /api/products/1 (Consultar producto ID 1):"
curl -i -s "$FLASK_URL/api/products/1"

echo -e "\n\n[2.3] POST /api/products (Crear producto 'Mouse Inalámbrico Pro'):"
curl -i -s -H "Content-Type: application/json" -X POST \
  -d '{"name":"Mouse Inalambrico Pro","description":"Sensor optico 25K DPI","price":79.99,"stock":30}' \
  "$FLASK_URL/api/products"

echo -e "\n\n[2.4] PUT /api/products/2 (Actualizar producto ID 2):"
curl -i -s -H "Content-Type: application/json" -X PUT \
  -d '{"name":"Monitor UltraWide 34 HDR","description":"Monitor curvo WQHD IPS 165Hz","price":510.00,"stock":12}' \
  "$FLASK_URL/api/products/2"

echo -e "\n\n[2.5] DELETE /api/products/4 (Eliminar producto recién creado):"
curl -i -s -X DELETE "$FLASK_URL/api/products/4"

echo -e "\n\n[2.6] GET /api/products/99 (Validar error 404 Not Found):"
curl -i -s "$FLASK_URL/api/products/99"

echo -e "\n\n=========================================================================="
echo " 3. VERIFICACIÓN DE DESPLIEGUE EN APACHE2 + MOD_WSGI — EJERCICIO 6"
echo "=========================================================================="

echo -e "\n[3.1] GET $APACHE_URL/api/users (Servido por Apache2/mod_wsgi):"
curl -i -s "$APACHE_URL/api/users"

echo -e "\n\n[3.2] GET $APACHE_URL/api/products (Servido por Apache2/mod_wsgi):"
curl -i -s "$APACHE_URL/api/products"

echo -e "\n\n=== AUDITORÍA COMPLETADA EXITOSAMENTE ==="
