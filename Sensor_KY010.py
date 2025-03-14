from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-010
sensor_ky010 = Pin(17, Pin.IN)  # Conectar OUT al GPIO 17 del ESP32

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky010"
MQTT_BROKER = "172.20.10.2"  # Cambia a la IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"

# Variable para almacenar el último estado
ultimo_estado = None  

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.3)
    print("\nWiFi Conectada!")

# Función para conectar a MQTT
def conectar_mqtt():
    global client
    try:
        print("Conectando a MQTT...")
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"Conectado a {MQTT_BROKER}")
    except OSError as e:
        print(f"Error al conectar a MQTT: {e}")
        time.sleep(5)
        conectar_mqtt()

# Conectar a WiFi y MQTT
conectar_wifi()
conectar_mqtt()

# Bucle principal
while True:
    try:
        # Leer el estado del sensor (0 = Objeto bloqueando, 1 = Libre)
        estado = sensor_ky010.value()
        mensaje_estado = "Objeto detectado" if estado == 0 else "Sin objeto"

        # Publicar solo si cambia el estado
        if estado != ultimo_estado:
            print(f"Publicando: {mensaje_estado}")
            client.publish(MQTT_TOPIC_PUB, mensaje_estado)
            ultimo_estado = estado  # Guardamos el estado actual

    except OSError as e:
        print(f"Error al leer el sensor: {e}")
        conectar_mqtt()  # Intentar reconectar a MQTT en caso de error

    time.sleep(0.5)  # Leer cada 500 ms para respuesta rápida
