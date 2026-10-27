#!/usr/bin/env python3
"""
Servicio Web RESTful en Python Flask con Persistencia en Base de Datos MySQL.

Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
Práctica 7: API REST y Persistencia Relacional
Referencia: Contenidos/Recursos API REST/2021 comandosBasicosSQL.pdf
"""

import os
import sys
from typing import Any, Dict, List, Optional, Tuple
from flask import Flask, jsonify, abort, request, Response
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)

# Configuración de conexión MySQL extraída de variables de entorno o valores por defecto seguros
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_USER = os.environ.get('MYSQL_USER', 'flaskuser')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'flaskpassword')
MYSQL_DB = os.environ.get('MYSQL_DATABASE', 'myflaskapp')


def get_db_connection() -> pymysql.Connection:
    """
    Establece y retorna una conexión activa con el motor de base de datos MySQL.

    Utiliza DictCursor para que los resultados de las consultas se entreguen
    como diccionarios clave-valor nativos, simplificando la serialización JSON.

    Returns:
        pymysql.Connection configurada con autocommit deshabilitado para control transaccional.
    """
    try:
        return pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            charset='utf8mb4',
            cursorclass=DictCursor,
            connect_timeout=5
        )
    except Exception as exc:
        app.logger.error("Error al conectar con la base de datos MySQL: %s", exc)
        raise exc


@app.route('/books', methods=['GET'])
def get_books() -> Tuple[Response, int]:
    """
    Consulta y retorna todos los registros de la tabla 'books' en MySQL.

    Ejecuta: SELECT id, title, description, author FROM books ORDER BY id ASC;
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, description, author FROM books ORDER BY id ASC")
            records = cursor.fetchall()
            return jsonify({'books': records}), 200
    finally:
        conn.close()


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id: int) -> Tuple[Response, int]:
    """
    Consulta un libro por su ID único en la base de datos MySQL.

    Ejecuta: SELECT id, title, description, author FROM books WHERE id = %s;
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, description, author FROM books WHERE id = %s", (book_id,))
            record = cursor.fetchone()
            if not record:
                abort(404, description=f"Libro con ID {book_id} no encontrado en la base de datos.")
            return jsonify({'book': record}), 200
    finally:
        conn.close()


@app.route('/books', methods=['POST'])
def create_book() -> Tuple[Response, int]:
    """
    Inserta un nuevo registro en la tabla 'books' de MySQL.

    Ejecuta: INSERT INTO books (title, description, author) VALUES (%s, %s, %s);
    """
    payload = request.get_json(silent=True)
    if not payload or 'title' not in payload or not str(payload['title']).strip():
        abort(400, description="Petición inválida: 'title' es un campo obligatorio.")

    title = str(payload['title']).strip()
    description = str(payload.get('description', ''))
    author = str(payload.get('author', ''))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = "INSERT INTO books (title, description, author) VALUES (%s, %s, %s)"
            cursor.execute(query, (title, description, author))
            new_id = cursor.lastrowid
            conn.commit()

        new_book = {
            'id': new_id,
            'title': title,
            'description': description,
            'author': author
        }
        return jsonify({'book': new_book}), 201
    except Exception as exc:
        conn.rollback()
        abort(500, description=f"Error durante la inserción en MySQL: {exc}")
    finally:
        conn.close()


@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id: int) -> Tuple[Response, int]:
    """
    Actualiza los datos de un libro existente en MySQL mediante clave primaria.

    Ejecuta: UPDATE books SET title = %s, description = %s, author = %s WHERE id = %s;
    """
    payload = request.get_json(silent=True)
    if not payload or not isinstance(payload, dict):
        abort(400, description="Petición inválida: se requiere un objeto JSON.")

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, description, author FROM books WHERE id = %s", (book_id,))
            existing = cursor.fetchone()
            if not existing:
                abort(404, description=f"Libro con ID {book_id} inexistente.")

            new_title = str(payload.get('title', existing['title'])).strip()
            new_desc = str(payload.get('description', existing['description']))
            new_auth = str(payload.get('author', existing['author']))

            query = "UPDATE books SET title = %s, description = %s, author = %s WHERE id = %s"
            cursor.execute(query, (new_title, new_desc, new_auth, book_id))
            conn.commit()

        updated_book = {
            'id': book_id,
            'title': new_title,
            'description': new_desc,
            'author': new_auth
        }
        return jsonify({'book': updated_book}), 200
    except Exception as exc:
        conn.rollback()
        abort(500, description=f"Error al actualizar registro en MySQL: {exc}")
    finally:
        conn.close()


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id: int) -> Tuple[Response, int]:
    """
    Elimina físicamente un libro de la tabla 'books' por ID.

    Ejecuta: DELETE FROM books WHERE id = %s;
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM books WHERE id = %s", (book_id,))
            if not cursor.fetchone():
                abort(404, description=f"Libro con ID {book_id} no existe.")

            cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
            conn.commit()
            return jsonify({'result': True}), 200
    except Exception as exc:
        conn.rollback()
        abort(500, description=f"Error al eliminar registro en MySQL: {exc}")
    finally:
        conn.close()


@app.errorhandler(400)
def handle_bad_request(error: Any) -> Tuple[Response, int]:
    return jsonify({'error': 'Bad Request', 'message': str(getattr(error, 'description', error))}), 400


@app.errorhandler(404)
def handle_not_found(error: Any) -> Tuple[Response, int]:
    return jsonify({'error': 'Not Found', 'message': str(getattr(error, 'description', error))}), 404


@app.errorhandler(500)
def handle_internal_error(error: Any) -> Tuple[Response, int]:
    return jsonify({'error': 'Internal Server Error', 'message': str(getattr(error, 'description', error))}), 500


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
