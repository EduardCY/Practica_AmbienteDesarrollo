#!/usr/bin/env bash
# =============================================================================
# DEMOSTRACIÓN COMPLETA PARA SUSTENTACIÓN (GUEST LINUX)
# =============================================================================
# Recorre ordenadamente los archivos de configuración y los puntos de evaluación.
# =============================================================================

set -e

clear
echo "=========================================================================="
echo " GUION DE SUSTENTACIÓN — PRÁCTICA 7 (SERVICIOS WEB REST E IOT UBIDOTS)"
echo " Estudiante: Eduard Criollo Yule | Universidad Autónoma de Occidente"
echo "=========================================================================="
sleep 2

echo -e "\n[FASE 0] EXPOSICIÓN DE ARCHIVOS DE CONFIGURACIÓN E INFRAESTRUCTURA"
echo "--------------------------------------------------------------------------"
echo "1. Inspección de Vagrantfile (Red Privada 192.168.50.3 + Port Forward 5000):"
head -n 25 /vagrant/Vagrantfile || true
sleep 3

echo -e "\n2. Inspección del Servicio systemd apirest.service:"
cat /vagrant/config/apirest.service || true
sleep 3

echo -e "\n3. Estado del demonio apirest en el sistema:"
systemctl status apirest.service --no-pager || true
sleep 3

echo -e "\n[FASE 1] SUSTENTACIÓN DE LA PARTE 1 — API REST FLASK (EN MEMORIA)"
echo "--------------------------------------------------------------------------"
echo "Petición 1: Listar colección completa (GET /books)"
curl -i -s http://localhost:5000/books
sleep 2

echo -e "\n\nPetición 2: Crear nuevo recurso (POST /books)"
curl -i -s -H "Content-Type: application/json" -X POST \
  -d '{"title": "Cien anos de soledad", "author": "Gabo", "description": "Magia pura"}' \
  http://localhost:5000/books
sleep 2

echo -e "\n\nPetición 3: Modificar recurso por ID (PUT /books/2)"
curl -i -s -H "Content-Type: application/json" -X PUT \
  -d '{"author": "Jorgito"}' \
  http://localhost:5000/books/2
sleep 2

echo -e "\n\nPetición 4: Eliminar recurso (DELETE /books/1)"
curl -i -s -X DELETE http://localhost:5000/books/1
sleep 2

echo -e "\n\nPetición 5: Probar manejo semántico de error 404 (GET /books/99)"
curl -i -s http://localhost:5000/books/99
sleep 3

echo -e "\n[FASE 2] SUSTENTACIÓN DE LA PERSISTENCIA RELACIONAL MYSQL"
echo "--------------------------------------------------------------------------"
echo "Comprobando tabla 'books' en MySQL (myflaskapp):"
mysql -u flaskuser -pflaskpassword -e "USE myflaskapp; SELECT * FROM books;" || true
sleep 3

echo -e "\n[FASE 3] SUSTENTACIÓN DE LA PARTE 2 — CLIENTE IOT Y UBIDOTS"
echo "--------------------------------------------------------------------------"
echo "Ejecutando ráfaga telemétrica con las 5 variables (testUbidots.py --once):"
python3 /vagrant/UbidotsClient/testUbidots.py --once || true
sleep 2

echo -e "\nActualización manual de variable 'temperature' mediante cURL:"
UBI_TOKEN=$(grep -E "^UBIDOTS_TOKEN=" /vagrant/.env 2>/dev/null | cut -d '=' -f2 | tr -d '\r' || true)
if [ -z "$UBI_TOKEN" ]; then UBI_TOKEN="BBUS-qZdFGWNPNLOvb8S9q0yqAo4Bk4GLPs"; fi
curl -i -s -H "Content-Type: application/json" -H "X-Auth-Token: $UBI_TOKEN" \
  -X POST -d '{"temperature": 45.0}' \
  http://industrial.api.ubidots.com/api/v1.6/devices/machine || true

echo -e "\n=========================================================================="
echo " DEMOSTRACIÓN FINALIZADA. PROCEDA A MOSTRAR EL DASHBOARD EN EL NAVEGADOR."
echo "=========================================================================="
