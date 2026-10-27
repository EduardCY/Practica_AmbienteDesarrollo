#!/usr/bin/env bash
# =============================================================================
# DEMOSTRACIÓN COMPLETA PARA SUSTENTACIÓN EN LA VM (servidorWeb — PRÁCTICA 9)
# =============================================================================

set -e

clear
echo "=========================================================================="
echo " GUION DE SUSTENTACIÓN — PRÁCTICA 9 (FLASK + REST + MYSQL + APACHE WSGI)"
echo " Estudiante: Eduard Criollo Yule | Universidad Autónoma de Occidente"
echo "=========================================================================="
sleep 2

echo -e "\n[EJERCICIO 1] VERIFICACIÓN DE MYSQL Y TABLAS CREADAS (users y products)"
echo "--------------------------------------------------------------------------"
sudo systemctl status mysql --no-pager | head -n 12 || true
mysql -u root -proot -e "USE myflaskapp; SHOW TABLES; DESCRIBE users; SELECT * FROM users; DESCRIBE products; SELECT * FROM products;"
sleep 3

echo -e "\n[EJERCICIO 3.a] PRUEBAS CRUD CON CURL — API DE USUARIOS (/api/users)"
echo "--------------------------------------------------------------------------"
echo "1. GET /api/users:"
curl -i -s http://localhost:5000/api/users
echo -e "\n\n2. POST /api/users:"
curl -i -s -H "Content-Type: application/json" -X POST \
  -d '{"name":"Eduard Criollo","email":"eduard.criollo@uao.edu.co","username":"ecriollo","password":"789"}' \
  http://localhost:5000/api/users
echo -e "\n\n3. PUT /api/users/2:"
curl -i -s -H "Content-Type: application/json" -X PUT \
  -d '{"name":"Maria Fernanda","email":"maria.fernanda@gmail.com","username":"mariaf","password":"456"}' \
  http://localhost:5000/api/users/2
sleep 3

echo -e "\n[EJERCICIO 5.b] PRUEBAS CRUD CON CURL — API DE PRODUCTOS (/api/products)"
echo "--------------------------------------------------------------------------"
echo "1. GET /api/products:"
curl -i -s http://localhost:5000/api/products
echo -e "\n\n2. POST /api/products:"
curl -i -s -H "Content-Type: application/json" -X POST \
  -d '{"name":"Mouse Inalambrico Pro","description":"Sensor optico 25K DPI","price":79.99,"stock":30}' \
  http://localhost:5000/api/products
echo -e "\n\n3. PUT /api/products/2:"
curl -i -s -H "Content-Type: application/json" -X PUT \
  -d '{"name":"Monitor UltraWide 34 HDR","description":"Monitor curvo WQHD IPS 165Hz","price":510.00,"stock":12}' \
  http://localhost:5000/api/products/2
sleep 3

echo -e "\n[EJERCICIO 6] VERIFICACIÓN DE DESPLIEGUE EN APACHE2 + MOD_WSGI (PUERTO 80)"
echo "--------------------------------------------------------------------------"
sudo systemctl status apache2 --no-pager | head -n 12 || true
echo -e "\nPetición GET http://localhost/api/products servida por Apache2:"
curl -i -s http://localhost/api/products

echo -e "\n=========================================================================="
echo " DEMOSTRACIÓN EN CONSOLA FINALIZADA CON ÉXITO"
echo "=========================================================================="
