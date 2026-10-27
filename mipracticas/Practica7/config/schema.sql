-- =============================================================================
-- ESQUEMA SQL: myflaskapp
-- Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
-- Práctica 7: API REST Flask y Persistencia MySQL
-- Referencia: Contenidos/Recursos API REST/2021 comandosBasicosSQL.pdf
-- =============================================================================

-- 1. Creación de la base de datos con codificación universal UTF-8
CREATE DATABASE IF NOT EXISTS myflaskapp
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE myflaskapp;

-- 2. Creación de la tabla 'books' con llave primaria autoincremental
CREATE TABLE IF NOT EXISTS books (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description VARCHAR(255) DEFAULT '',
  author VARCHAR(255) DEFAULT '',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Inserción de los registros semilla iniciales requeridos en la guía
INSERT INTO books (id, title, description, author) VALUES
  (1, 'La hojarasca', 'Good one', 'Gabo'),
  (2, 'El coronel no tiene quien le escriba', 'Interesting', 'Gabo')
ON DUPLICATE KEY UPDATE
  title = VALUES(title),
  description = VALUES(description),
  author = VALUES(author);

-- 4. Creación de usuario dedicado para la aplicación Flask (Buenas prácticas de seguridad)
CREATE USER IF NOT EXISTS 'flaskuser'@'%' IDENTIFIED WITH mysql_native_password BY 'flaskpassword';
ALTER USER 'flaskuser'@'%' IDENTIFIED WITH mysql_native_password BY 'flaskpassword';
GRANT ALL PRIVILEGES ON myflaskapp.* TO 'flaskuser'@'%';

CREATE USER IF NOT EXISTS 'flaskuser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'flaskpassword';
ALTER USER 'flaskuser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'flaskpassword';
GRANT ALL PRIVILEGES ON myflaskapp.* TO 'flaskuser'@'localhost';
FLUSH PRIVILEGES;
