from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-031
sensor_ky031 = Pin(17, Pin.IN)  # Conectar S al GPIO 17 (entrada digital)

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky031"
MQTT_BROKER = "172.20.10.2"  # IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"

# Variable para almacenar el último estado enviado
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
        # Leer el estado del sensor (0 = Impacto detectado, 1 = Sin impacto)
        estado = sensor_ky031.value()
        mensaje_estado = "💥 Impacto detectado" if estado == 0 else "✅ Sin impacto"

        # Publicar solo si hay un cambio en el estado
        if estado != ultimo_estado:
            print(f"Publicando: {mensaje_estado}")
            client.publish(MQTT_TOPIC_PUB, mensaje_estado)
            ultimo_estado = estado  # Guardar el estado actual

    except OSError as e:
        print(f"Error al leer el sensor: {e}")
        conectar_mqtt()  # Intentar reconectar a MQTT en caso de error

    time.sleep(0.3)  # Leer cada 300 ms para una respuesta rápida
