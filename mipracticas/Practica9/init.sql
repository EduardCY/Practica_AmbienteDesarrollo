-- =============================================================================
-- ESQUEMA SQL INICIAL: myflaskapp ( Tablas: users y products )
-- Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
-- Práctica 9: Aplicación Web + API REST en Python Flask + MySQL + Apache WSGI
-- Referencia: 2024-01 Practica REST_MYSQL.pdf (Ejercicios 1 y 5.a)
-- =============================================================================

-- 1. Creación de la base de datos con soporte de codificación universal UTF-8
CREATE DATABASE IF NOT EXISTS myflaskapp
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE myflaskapp;

-- 2. Creación de la tabla 'users' (Ejercicio 1 de la guía)
CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Inserción idempotente de registros iniciales de 'users' (Página 2 de la guía)
INSERT INTO users (id, name, email, username, password) VALUES
    (1, 'juan', 'juan@gmail.com', 'juan', '123'),
    (2, 'maria', 'maria@gmail.com', 'maria', '456')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    email = VALUES(email),
    username = VALUES(username),
    password = VALUES(password);

-- 4. Creación de la tabla 'products' (Ejercicio 5.a: Gestión de Productos)
CREATE TABLE IF NOT EXISTS products (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255) DEFAULT '',
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    stock INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Inserción idempotente de registros semilla en 'products'
INSERT INTO products (id, name, description, price, stock) VALUES
    (1, 'Laptop Pro 15', 'Portátil de alto rendimiento 16GB RAM 512GB NVMe', 1250.00, 15),
    (2, 'Monitor UltraWide 34', 'Monitor curvo WQHD IPS 144Hz para desarrollo', 480.50, 8),
    (3, 'Teclado Mecánico RGB', 'Switches táctiles silenciosos formato TKL', 95.00, 25)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    description = VALUES(description),
    price = VALUES(price),
    stock = VALUES(stock);

-- 6. Configuración de permisos y plugin nativo en MySQL 8.0 (Ubuntu 22.04)
-- Permite que tanto 'mysql -u root -proot' (guía pág. 2) como SQLAlchemy funcionen sin error 1045
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'root';
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'root';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

CREATE USER IF NOT EXISTS 'flaskuser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'flaskpassword';
ALTER USER 'flaskuser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'flaskpassword';
GRANT ALL PRIVILEGES ON myflaskapp.* TO 'flaskuser'@'localhost';

CREATE USER IF NOT EXISTS 'flaskuser'@'%' IDENTIFIED WITH mysql_native_password BY 'flaskpassword';
ALTER USER 'flaskuser'@'%' IDENTIFIED WITH mysql_native_password BY 'flaskpassword';
GRANT ALL PRIVILEGES ON myflaskapp.* TO 'flaskuser'@'%';

FLUSH PRIVILEGES;
