from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-033 (sensor de línea)
sensor_digital = Pin(17, Pin.IN)  # Pin de salida digital del sensor

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky033"
MQTT_BROKER = "172.20.10.2"  # IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic MQTT para detección de línea

# Variable para almacenar el último estado detectado
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

# Conectar a WiFi
conectar_wifi()

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

# Conectar a MQTT
conectar_mqtt()

# Bucle principal
while True:
    try:
        # Leer el estado del sensor (0 = línea detectada, 1 = línea no detectada)
        estado = sensor_digital.value()
        mensaje_estado = "🖤 Línea detectada" if estado == 0 else "⬜ Línea no detectada"

        # Publicar solo si cambia el estado
        if estado != ultimo_estado:
            print(f"Publicando: {mensaje_estado}")
            client.publish(MQTT_TOPIC_PUB, mensaje_estado)
            ultimo_estado = estado  # Guardamos el estado actual

    except OSError as e:
        print(f"Error al leer el sensor: {e}")
        conectar_mqtt()  # Intentar reconectar a MQTT en caso de error

    time.sleep(0.5)  # Leer cada 500 ms para respuesta más rápida
