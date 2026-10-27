#!/usr/bin/env bash
# =============================================================================
# BATERÍA DE PRUEBAS AUTOMATIZADAS CURL — PARTE 1: API REST FLASK
# =============================================================================
# Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
# Práctica 7: API REST en Python Flask
# =============================================================================

API_HOST="${1:-http://localhost:5000}"

echo "======================================================================"
echo " INICIANDO PRUEBAS DE LA PARTE 1 EN: ${API_HOST}"
echo "======================================================================"

echo -e "\n--- [1] GET /books (Listar todos los libros) ---"
curl -i -s -X GET "${API_HOST}/books"

echo -e "\n\n--- [2] GET /books/2 (Consultar libro existente por ID) ---"
curl -i -s -X GET "${API_HOST}/books/2"

echo -e "\n\n--- [3] GET /books/99 (Probar manejo de 404 Not Found) ---"
curl -i -s -X GET "${API_HOST}/books/99"

echo -e "\n\n--- [4] POST /books (Crear un nuevo libro válido - Esperado: 201 Created) ---"
curl -i -s -H "Content-Type: application/json" \
  -X POST \
  -d '{"title": "Cien años de soledad", "description": "Obra maestra del realismo magico", "author": "Gabriel Garcia Marquez"}' \
  "${API_HOST}/books"

echo -e "\n\n--- [5] POST /books (Probar validación sin título - Esperado: 400 Bad Request) ---"
curl -i -s -H "Content-Type: application/json" \
  -X POST \
  -d '{"description": "Libro sin campo title"}' \
  "${API_HOST}/books"

echo -e "\n\n--- [6] PUT /books/2 (Actualizar libro existente) ---"
curl -i -s -H "Content-Type: application/json" \
  -X PUT \
  -d '{"author": "Jorgito", "description": "Edicion especial revisada"}' \
  "${API_HOST}/books/2"

echo -e "\n\n--- [7] DELETE /books/1 (Eliminar libro por ID) ---"
curl -i -s -X DELETE "${API_HOST}/books/1"

echo -e "\n\n--- [8] GET /books (Verificar estado final de la colección) ---"
curl -i -s -X GET "${API_HOST}/books"

echo -e "\n\n======================================================================"
echo " BATERÍA DE PRUEBAS DE PARTE 1 COMPLETADA CON ÉXITO"
echo "======================================================================"
