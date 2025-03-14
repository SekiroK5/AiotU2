from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-02
sensor_pin = Pin(15, Pin.IN, pull=Pin.PULL_UP)

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky02_vibracion"
MQTT_BROKER = "172.20.10.2"  # Cambia a la IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic para enviar datos de vibración

# Variable para almacenar el último estado
ultimo_estado = sensor_pin.value()

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

# Conectar al broker MQTT
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
client.connect()
print(f"Conectado a {MQTT_BROKER}")

# Bucle principal para leer el sensor KY-02
while True:
    try:
        estado_actual = sensor_pin.value()

        # Si el estado cambia, enviamos un mensaje
        if estado_actual != ultimo_estado:
            if estado_actual == 0:
                mensaje = "Vibración detectada"
            else:
                mensaje = "Sin vibración"

            print(f"Publicando: {mensaje}")
            client.publish(MQTT_TOPIC_PUB, mensaje)

            # Actualizamos el estado
            ultimo_estado = estado_actual

    except OSError as e:
        print("Error al leer el sensor:", e)

    time.sleep(0.2)  # Pequeño delay para evitar lecturas erráticas
