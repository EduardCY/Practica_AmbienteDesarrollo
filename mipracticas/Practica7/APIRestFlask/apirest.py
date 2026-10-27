#!/usr/bin/env python3
"""
Servicio Web RESTful en Python Flask — Colección de Libros (En Memoria).

Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
Práctica 7: API REST y Simulación IoT
Referencia: 2024-03 Practica REST_AI.pdf y video_3_C9QBlpqutUM.txt
Repositorio oficial: https://github.com/omondragon/APIRestFlask
"""

import os
import sys
from typing import Any, Dict, List, Tuple
from flask import Flask, jsonify, abort, request, Response

app = Flask(__name__)

# =============================================================================
# MODELO DE DATOS EN MEMORIA
# =============================================================================
# Colección de libros simulada en memoria. Permite ilustrar de forma didáctica
# la manipulación de recursos y el desacoplamiento cliente-servidor sin
# dependencias de bases de datos externas en la Parte 1.
books: List[Dict[str, Any]] = [
    {
        'id': 1,
        'title': 'La hojarasca',
        'description': 'Good one',
        'author': 'Gabo'
    },
    {
        'id': 2,
        'title': 'El coronel no tiene quien le escriba',
        'description': 'Interesting',
        'author': 'Gabo'
    }
]


# =============================================================================
# CONTROLADORES DE RUTA / ENDPOINTS RESTFUL
# =============================================================================

@app.route('/books', methods=['GET'])
def get_books() -> Tuple[Response, int]:
    """
    Recupera la colección completa de libros registrados.

    Método: GET /books
    Idempotente: Sí. Operación de sólo lectura sin alteración de estado del recurso.
    Código HTTP: 200 OK implícito/explícito con payload JSON.

    Returns:
        Tupla con respuesta JSON estructurada y código HTTP 200.
    """
    # Se utiliza jsonify para serializar la estructura nativa de Python a formato JSON
    # conforme a la especificación estándar RFC 8259.
    return jsonify({'books': books}), 200


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id: int) -> Tuple[Response, int]:
    """
    Obtiene los detalles de un libro específico identificado por su ID numérico.

    Método: GET /books/<int:book_id>
    Parámetro de ruta: book_id (entero único asignado al recurso).

    Args:
        book_id: Identificador numérico del libro en la colección.

    Returns:
        JSON con los datos del libro encontrado y código HTTP 200,
        o código HTTP 404 (Not Found) si el recurso no existe.
    """
    # Filtro funcional sobre la lista para localizar el recurso por clave primaria 'id'
    match = [b for b in books if b['id'] == book_id]
    if len(match) == 0:
        # Se interrumpe el flujo retornando 404 para cumplir con la semántica REST
        # cuando el URI solicitado apunta a una entidad inexistente.
        abort(404, description=f"Libro con ID {book_id} no encontrado en el sistema.")
    return jsonify({'book': match[0]}), 200


@app.route('/books', methods=['POST'])
def create_book() -> Tuple[Response, int]:
    """
    Crea y registra un nuevo libro en la colección en memoria.

    Método: POST /books
    Payload esperado: JSON con al menos el atributo obligatorio 'title'.
    Atributos opcionales: 'description', 'author'.

    Returns:
        JSON con el recurso recién creado y código HTTP 201 (Created),
        o código HTTP 400 (Bad Request) si el payload no es JSON o carece de 'title'.
    """
    # Se utiliza get_json(silent=True) para evitar excepciones de tipo no controladas
    # si el cliente omite la cabecera Content-Type: application/json.
    payload = request.get_json(silent=True)
    if not payload or 'title' not in payload or not str(payload['title']).strip():
        # Validación de integridad de entrada: el título es el atributo semántico mínimo.
        abort(400, description="Petición inválida: el cuerpo debe ser JSON y contener un campo 'title' no vacío.")

    # Generación segura de ID autoincremental, contemplando listas vacías si se eliminaron elementos previamente.
    new_id = books[-1]['id'] + 1 if len(books) > 0 else 1

    book = {
        'id': new_id,
        'title': str(payload['title']).strip(),
        'description': str(payload.get('description', '')),
        'author': str(payload.get('author', ''))
    }
    books.append(book)

    # Retorno con código de estado HTTP 201 conforme a los lineamientos RFC 7231
    return jsonify({'book': book}), 201


@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id: int) -> Tuple[Response, int]:
    """
    Actualiza parcialmente o totalmente los atributos de un libro existente.

    Método: PUT /books/<int:book_id>
    Payload: Objeto JSON con los atributos a modificar ('title', 'description', 'author').

    Args:
        book_id: Identificador numérico del libro a modificar.

    Returns:
        JSON con el estado actualizado del libro y código HTTP 200,
        o código HTTP 404 si el recurso no existe,
        o código HTTP 400 si el payload no es JSON válido.
    """
    match = [b for b in books if b['id'] == book_id]
    if len(match) == 0:
        abort(404, description=f"No se puede actualizar: libro con ID {book_id} inexistente.")

    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict):
        abort(400, description="Petición inválida: se requiere un objeto JSON con los campos a actualizar.")

    target = match[0]
    # Se preservan los valores previos si el cliente no proporciona un campo específico
    if 'title' in payload:
        target['title'] = str(payload['title']).strip()
    if 'description' in payload:
        target['description'] = str(payload['description'])
    if 'author' in payload:
        target['author'] = str(payload['author'])

    return jsonify({'book': target}), 200


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id: int) -> Tuple[Response, int]:
    """
    Elimina permanentemente un libro de la colección en memoria.

    Método: DELETE /books/<int:book_id>
    Idempotente: Sí.

    Args:
        book_id: Identificador del libro que se desea dar de baja.

    Returns:
        JSON {'result': True} y código HTTP 200 si la eliminación fue exitosa,
        o código HTTP 404 si el libro ya no existe.
    """
    match = [b for b in books if b['id'] == book_id]
    if len(match) == 0:
        abort(404, description=f"No se puede eliminar: libro con ID {book_id} inexistente.")

    books.remove(match[0])
    return jsonify({'result': True}), 200


# =============================================================================
# MANEJADORES DE ERROR PERSONALIZADOS (RESPUESTAS JSON HOMOGÉNEAS)
# =============================================================================

@app.errorhandler(400)
def bad_request(error: Any) -> Tuple[Response, int]:
    """Captura errores 400 y asegura una respuesta serializada en JSON."""
    return jsonify({'error': 'Bad Request', 'message': str(getattr(error, 'description', error))}), 400


@app.errorhandler(404)
def not_found(error: Any) -> Tuple[Response, int]:
    """Captura errores 404 y asegura una respuesta serializada en JSON."""
    return jsonify({'error': 'Not Found', 'message': str(getattr(error, 'description', error))}), 404


@app.errorhandler(500)
def internal_server_error(error: Any) -> Tuple[Response, int]:
    """Captura excepciones no controladas evitando fugas de información interna."""
    return jsonify({'error': 'Internal Server Error', 'message': 'Ocurrió un error inesperado en el servidor.'}), 500


# =============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# =============================================================================

if __name__ == '__main__':
    # Se escucha en 0.0.0.0 para aceptar peticiones desde el anfitrión Windows
    # y desde la red privada Host-Only (192.168.50.3)
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1')
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
