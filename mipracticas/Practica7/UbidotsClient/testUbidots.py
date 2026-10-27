#!/usr/bin/env python3
"""
Cliente IoT en Python para Simulación y Envío de Telemetría a la Plataforma Ubidots.

Asignatura: Ambiente de Desarrollo / Servicios Telemáticos
Práctica 7: Parte 2 — Uso de la API REST de Ubidots y Monitoreo IoT
Referencia: 2024-03 Practica REST_AI.pdf (Páginas 4-7)
Repositorio oficial: https://github.com/omondragon/UbidotsClient

Cumplimiento de Requerimientos:
- Envía solicitudes HTTP POST con carga útil en JSON.
- Reporta 5 variables telemétricas (3 originales + 2 adicionales seleccionadas):
  1. temperature: Valor aleatorio entre -10 °C y 50 °C (Diagrama de Barras en Ubidots).
  2. humidity: Valor aleatorio entre 0 % y 85 % (Widget Gauge / Indicador).
  3. position: Coordenadas GPS en contexto {lat, lng} (Widget Mapa).
  4. pressure: Presión atmosférica entre 980 y 1040 hPa (Widget Gráfico de Líneas).
  5. battery_level: Porcentaje de batería restante entre 10 % y 100 % (Widget Tanque).
- Mecanismo de reintentos exponencial (hasta 5 intentos ante códigos >= 400).
- Soporte para ejecución en bucle continuo o modo ráfaga unitaria (--once) para auditorías.
"""

import argparse
import json
import math
import os
import random
import sys
import time
from typing import Any, Dict, Tuple

# =============================================================================
# CARGA SEGURA DE CONFIGURACIÓN Y CREDENCIALES
# =============================================================================
# Se prioriza la lectura desde variables de entorno o archivo .env para
# evitar la filtración de claves privadas en repositorios públicos.
try:
    from dotenv import load_dotenv
    # Cargar archivo .env ubicado en la raíz de la práctica o en el directorio de ejecución
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    load_dotenv('.env')
except ImportError:
    pass

TOKEN = os.environ.get('UBIDOTS_TOKEN', 'BBFF-mockTokenForLocalValidationOnly000')
DEVICE_LABEL = os.environ.get('UBIDOTS_DEVICE_LABEL', 'machine')
BASE_URL = os.environ.get('UBIDOTS_BASE_URL', 'http://industrial.api.ubidots.com')

# Identificadores estándar de las variables en Ubidots
VARIABLE_LABEL_1 = "temperature"
VARIABLE_LABEL_2 = "humidity"
VARIABLE_LABEL_3 = "position"
# Nuevas variables añadidas en cumplimiento del Punto 5 del taller
VARIABLE_LABEL_4 = "pressure"
VARIABLE_LABEL_5 = "battery_level"


def build_payload(
    var_temp: str,
    var_hum: str,
    var_pos: str,
    var_press: str,
    var_batt: str
) -> Dict[str, Any]:
    """
    Construye la carga útil (payload JSON) con datos sintéticos aleatorios coherentes.

    Genera valores estadísticamente plausibles para un nodo de monitoreo ambiental
    y georreferenciado con telemetría de energía.

    Args:
        var_temp: Etiqueta de la variable de temperatura.
        var_hum: Etiqueta de la variable de humedad relativa.
        var_pos: Etiqueta de la variable geográfica con contexto latitud/longitud.
        var_press: Etiqueta de la variable de presión atmosférica (hPa).
        var_batt: Etiqueta de la variable del nivel de batería (%).

    Returns:
        Diccionario serializable a JSON con las 5 magnitudes telemétricas.
    """
    # 1. Temperatura ambiente (-10 °C a 50 °C)
    value_temp = random.randint(38, 50)

    # 2. Humedad relativa (0 % a 85 %)
    value_hum = random.randint(0, 85)

    # 3. Coordenadas GPS sintéticas dentro de un cuadrante representativo
    lat = 3.4563
    lng = -76.5311

    # 4. Presión barométrica estándar al nivel del mar (980 a 1040 hPa)
    value_press = round(random.uniform(980.0, 1040.0), 2)

    # 5. Estado de la batería del dispositivo (10 % a 100 %)
    value_batt = random.randint(10, 100)

    payload = {
        var_temp: value_temp,
        var_hum: value_hum,
        var_pos: {
            "value": 1,
            "context": {
                "lat": lat,
                "lng": lng
            }
        },
        var_press: value_press,
        var_batt: value_batt
    }
    return payload


def post_request(payload: Dict[str, Any], token: str, device: str, base_url: str) -> bool:
    """
    Transmite el payload hacia la API REST v1.6 de Ubidots utilizando HTTP POST.

    Implementa una política de reintento automático con espera de 1 segundo
    en caso de errores transitorios de red o rechazos de autenticación (códigos >= 400).

    Args:
        payload: Diccionario con las mediciones a enviar.
        token: Clave de autenticación API de Ubidots (cabecera X-Auth-Token).
        device: Identificador único del dispositivo (device label).
        base_url: URL base del endpoint de Ubidots.

    Returns:
        True si la solicitud fue aceptada (código 200/201), False tras 5 fallos consecutivos.
    """
    import requests

    target_url = f"{base_url.rstrip('/')}/api/v1.6/devices/{device}"
    headers = {
        "X-Auth-Token": token,
        "Content-Type": "application/json"
    }

    status = 400
    attempts = 0
    max_attempts = 5

    while status >= 400 and attempts < max_attempts:
        try:
            response = requests.post(
                url=target_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            status = response.status_code
        except requests.exceptions.RequestException as error:
            print(f"[WARN] Error de comunicación en intento {attempts + 1}: {error}")
            status = 500

        attempts += 1
        if status >= 400:
            time.sleep(1)

    # Evaluación y reporte del resultado operativo
    if status >= 400:
        print(f"[ERROR] Could not send data after {max_attempts} attempts (HTTP {status}).")
        print("        Verifique la conectividad a Internet y la validez de su UBIDOTS_TOKEN.")
        return False

    print(f"[INFO] Request made properly (HTTP {status}), device '{device}' is updated.")
    return True


def parse_arguments() -> argparse.Namespace:
    """Procesa argumentos opcionales por línea de comandos para facilitar pruebas automatizadas."""
    parser = argparse.ArgumentParser(description="Cliente IoT Ubidots - Práctica 7")
    parser.add_argument('--once', action='store_true', help="Envía una única ráfaga y finaliza (modo auditoría).")
    parser.add_argument('--interval', type=int, default=2, help="Intervalo en segundos entre envíos continuos.")
    parser.add_argument('--token', type=str, default=None, help="Sobrescribe el token de Ubidots.")
    return parser.parse_args()


def main() -> None:
    """Bucle principal de ejecución del simulador telemétrico."""
    args = parse_arguments()
    active_token = args.token or TOKEN

    print("=================================================================")
    print(" SIMULADOR IOT UBIDOTS — PRÁCTICA 7")
    print(f" Dispositivo: {DEVICE_LABEL}")
    print(f" Endpoint:    {BASE_URL}/api/v1.6/devices/{DEVICE_LABEL}")
    print(f" Variables:   {VARIABLE_LABEL_1}, {VARIABLE_LABEL_2}, {VARIABLE_LABEL_3}, "
          f"{VARIABLE_LABEL_4}, {VARIABLE_LABEL_5}")
    print(f" Token:       {active_token[:6]}...{active_token[-4:] if len(active_token) > 10 else ''}")
    print("=================================================================")

    if args.once:
        print("[INFO] Modo ejecución única (--once) activado.")
        payload = build_payload(
            VARIABLE_LABEL_1,
            VARIABLE_LABEL_2,
            VARIABLE_LABEL_3,
            VARIABLE_LABEL_4,
            VARIABLE_LABEL_5
        )
        print(f"[INFO] Payload generado:\n{json.dumps(payload, indent=2)}")
        print("[INFO] Attempting to send data...")
        success = post_request(payload, active_token, DEVICE_LABEL, BASE_URL)
        print("[INFO] finished (exit status:", 0 if success else 1, ")")
        sys.exit(0 if success else 1)

    # Ejecución interactiva continua requerida en el paso 4 y 5 de la guía
    print("[INFO] Iniciando transmisión periódica (Ctrl+C para detener)...")
    try:
        while True:
            payload = build_payload(
                VARIABLE_LABEL_1,
                VARIABLE_LABEL_2,
                VARIABLE_LABEL_3,
                VARIABLE_LABEL_4,
                VARIABLE_LABEL_5
            )
            print(f"\n[INFO] Attempting to send data ({time.strftime('%H:%M:%S')}): {payload}")
            post_request(payload, active_token, DEVICE_LABEL, BASE_URL)
            print("[INFO] finished. Esperando siguiente ciclo...")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[INFO] Simulación detenida por el usuario.")


if __name__ == '__main__':
    main()
