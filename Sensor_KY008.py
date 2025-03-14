from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del módulo láser KY-008
laser = Pin(17, Pin.OUT)  # Pin donde está conectado el láser

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky008"
MQTT_BROKER = "172.20.10.2"  # IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic para el estado del láser
MQTT_TOPIC_SUB = "ncm/sensor"  # Topic para recibir comandos

client = None  # Cliente MQTT

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
        client.set_callback(mqtt_callback)  # Asignar función de recepción
        client.connect()
        client.subscribe(MQTT_TOPIC_SUB)  # Suscribirse para recibir comandos
        print(f"Conectado a {MQTT_BROKER} y suscrito a {MQTT_TOPIC_SUB}")
    except OSError as e:
        print(f"Error al conectar a MQTT: {e}")
        time.sleep(5)
        conectar_mqtt()

# Función para manejar los mensajes MQTT
def mqtt_callback(topic, msg):
    mensaje = msg.decode("utf-8")
    print(f"Mensaje recibido: {mensaje}")

    if mensaje == "ON":
        laser.value(1)
        client.publish(MQTT_TOPIC_PUB, "🔴 Láser encendido")
    elif mensaje == "OFF":
        laser.value(0)
        client.publish(MQTT_TOPIC_PUB, "⚫ Láser apagado")

# Conectar a WiFi y MQTT
conectar_wifi()
conectar_mqtt()

# Bucle principal
while True:
    try:
        client.check_msg()  # Comprobar si hay mensajes nuevos en MQTT
        time.sleep(0.5)  # Leer cada 500ms
    except OSError as e:
        print(f"Error en MQTT: {e}")
        conectar_mqtt()
