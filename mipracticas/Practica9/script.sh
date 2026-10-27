#!/bin/bash
# =============================================================================
# SCRIPT DE APROVISIONAMIENTO AUTOMATIZADO — SERVIDORWEB (PRÁCTICA 9)
# =============================================================================
# Instala y configura MySQL 8.0, Python Flask + SQLAlchemy, el servicio systemd
# en el puerto 5000 y el servidor productivo Apache2 con mod_wsgi en el puerto 80.

set -e

echo "=== [servidorWeb] 1. Configurando parámetros desatendidos de MySQL ==="
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password root'
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'

echo "=== [servidorWeb] 2. Actualizando índices APT e instalando paquetes del sistema ==="
sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  mysql-server \
  mysql-client \
  python3-dev \
  python3-pip \
  python3-flask \
  python3-pymysql \
  default-libmysqlclient-dev \
  build-essential \
  pkg-config \
  apache2 \
  libapache2-mod-wsgi-py3 \
  dos2unix \
  curl \
  git

echo "=== [servidorWeb] 3. Inicializando servicio MySQL y cargando esquema init.sql ==="
sudo systemctl enable mysql.service
sudo systemctl start mysql.service

# Normalizar finales de línea CRLF -> LF en archivos SQL y scripts
if [ -f "/vagrant/init.sql" ]; then
  sed -i 's/\r$//' /vagrant/init.sql 2>/dev/null || true
  cp /vagrant/init.sql /home/vagrant/init.sql
fi
sed -i 's/\r$//' /home/vagrant/init.sql 2>/dev/null || true

# Cargar base de datos myflaskapp (tablas users y products) y permisos root/flaskuser
sudo mysql < /home/vagrant/init.sql || sudo mysql -h localhost -u root -proot < /home/vagrant/init.sql

echo "=== [servidorWeb] 4. Habilitando acceso remoto en MySQL (0.0.0.0) ==="
sudo sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo systemctl restart mysql.service

echo "=== [servidorWeb] 5. Instalando librerías de Python (Flask, CORS, MySQLdb, SQLAlchemy) ==="
# Se utiliza --ignore-installed blinker para evitar el conflicto distutils en Ubuntu 22.04
sudo pip3 install --ignore-installed blinker \
  Flask==2.3.3 \
  "Werkzeug<3.0.0" \
  flask-cors \
  Flask-MySQLdb \
  Flask-SQLAlchemy \
  PyMySQL \
  cryptography \
  python-dotenv

echo "=== [servidorWeb] 6. Sincronizando código de MiniWebApp en /home/vagrant/webapp y /var/www/webapp ==="
mkdir -p /home/vagrant/webapp
if [ -d "/vagrant/webapp" ]; then
  cp -r /vagrant/webapp/* /home/vagrant/webapp/
fi

# Normalizar saltos de línea en código Python, HTML, JS y WSGI
find /home/vagrant/webapp -type f \( -name "*.py" -o -name "*.wsgi" -o -name "*.html" -o -name "*.js" \) -exec sed -i 's/\r$//' {} + 2>/dev/null || true
sudo chown -R vagrant:vagrant /home/vagrant/webapp

# Copiar aplicación a /var/www/webapp para el despliegue productivo en Apache2 + mod_wsgi (Ejercicio 6)
sudo mkdir -p /var/www/webapp
sudo cp -r /home/vagrant/webapp/* /var/www/webapp/
sudo chown -R vagrant:www-data /var/www/webapp
sudo chmod -R 755 /var/www/webapp

echo "=== [servidorWeb] 7. Configurando servicio systemd webapp.service (Puerto 5000) ==="
if [ -f "/vagrant/config/webapp.service" ]; then
  sed -i 's/\r$//' /vagrant/config/webapp.service 2>/dev/null || true
  sudo cp /vagrant/config/webapp.service /etc/systemd/system/webapp.service
  sudo systemctl daemon-reload
  sudo systemctl enable webapp.service
  sudo systemctl restart webapp.service
fi

echo "=== [servidorWeb] 8. Configurando despliegue en Apache2 con mod_wsgi (Puerto 80 - Ejercicio 6) ==="
if [ -f "/vagrant/config/webapp_apache.conf" ]; then
  sed -i 's/\r$//' /vagrant/config/webapp_apache.conf 2>/dev/null || true
  sudo cp /vagrant/config/webapp_apache.conf /etc/apache2/sites-available/webapp.conf
  sudo a2enmod wsgi
  sudo a2dissite 000-default.conf || true
  sudo a2ensite webapp.conf
  sudo systemctl enable apache2
  sudo systemctl restart apache2
fi

# Normalizar scripts de pruebas si existen
if [ -d "/vagrant/scripts" ]; then
  find /vagrant/scripts -type f -name "*.sh" -exec sed -i 's/\r$//' {} + 2>/dev/null || true
  chmod +x /vagrant/scripts/*.sh 2>/dev/null || true
fi

echo "=== [servidorWeb] Aprovisionamiento finalizado con éxito ==="
echo " - Flask (Puerto 5000):  http://192.168.60.3:5000  |  http://localhost:5000"
echo " - Apache (Puerto 80):   http://192.168.60.3       |  http://localhost:8080"
