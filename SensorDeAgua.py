from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor de nivel de agua
sensor_pin = Pin(35, Pin.IN)  # Pin donde conectaste el sensor de nivel de agua
led_pin = Pin(16, Pin.OUT)  # Pin donde conectaste el LED

# Configuración WiFi (tu red doméstica)
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_nivel_agua"
MQTT_BROKER = "172.20.10.2"  # Cambia a la IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic para el sensor de nivel de agua
MQTT_TOPIC_SUB = "led/control"

# Variables para almacenar el último estado del sensor
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

# Función para suscribirse al broker MQTT
def subscribir():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(llegada_mensaje)
    client.connect()
    client.subscribe(MQTT_TOPIC_SUB)
    print(f"Conectado a {MQTT_BROKER}, suscrito a {MQTT_TOPIC_SUB}")
    return client

# Función para recibir mensajes MQTT y controlar el LED
def llegada_mensaje(topic, msg):
    print(f"Mensaje recibido en {topic}: {msg}")
    if msg == b"true":
        led_pin.value(1)  # Encender LED
    elif msg == b"false":
        led_pin.value(0)  # Apagar LED

# Conectar a WiFi
conectar_wifi()

# Conectar al broker MQTT
client = subscribir()

# Ciclo infinito para leer el sensor de nivel de agua y enviar datos solo cuando cambie
while True:
    client.check_msg()  # Revisar si hay mensajes en el topic de control
    try:
        estado = sensor_pin.value()  # Lectura del sensor de nivel de agua
        led_pin.value(estado)  # Encender o apagar el LED según el estado del sensor
        
        # Convertir el estado en mensaje comprensible
        if estado == 1:
            mensaje = "Agua detectada"
        else:
            mensaje = "No hay agua"

        # Solo publicamos si el estado ha cambiado
        if mensaje != ultimo_estado:
            print(f"Publicando: {mensaje}")
            client.publish(MQTT_TOPIC_PUB, mensaje)  # Publicamos el estado en el topic
            ultimo_estado = mensaje  # Actualizamos el último estado

    except OSError as e:
        print("Error al leer el sensor:", e)

    time.sleep(1)  # Esperamos 1 segundo antes de leer nuevamente el sensor
