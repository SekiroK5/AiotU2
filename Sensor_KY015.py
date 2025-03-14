from machine import Pin
import time
import network
import dht
from umqtt.simple import MQTTClient

# Configuración del sensor KY-015 (DHT11)
sensor_dht = dht.DHT11(Pin(16))  # Conectar DATA al GPIO 16 del ESP32

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky015"
MQTT_BROKER = "172.20.10.2"  # Cambia a la IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_TEMP = "ncm/sensor"
MQTT_TOPIC_HUM = "ncm/sensor"

# Variable para reconexión
client = None  

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
        sensor_dht.measure()  # Tomar medición
        temperatura = sensor_dht.temperature()
        humedad = sensor_dht.humidity()

        print(f"Temperatura: {temperatura}°C, Humedad: {humedad}%")

        # Publicar en MQTT
        client.publish(MQTT_TOPIC_TEMP, f"🌡️ Temperatura: {temperatura}°C")
        client.publish(MQTT_TOPIC_HUM, f"💧 Humedad: {humedad}%")

    except OSError as e:
        print(f"Error al leer el sensor: {e}")
        conectar_mqtt()

    time.sleep(5)  # Leer datos cada 5 segundos
