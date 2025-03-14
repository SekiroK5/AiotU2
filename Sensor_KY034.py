from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del pin para controlar el LED RGB (KY-034)
led_pin = Pin(17, Pin.OUT)  # Pin de control del LED RGB de 7 colores

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_led_7colores"
MQTT_BROKER = "172.20.10.2"  # IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic para el estado del LED

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

# Función para cambiar el color del LED RGB (7 colores)
def cambiar_color():
    colores = ["Rojo", "Azul", "Amarillo", "Cyan", "Magenta", "Blanco"]
    
    # Loop para cambiar de color
    for color in colores:
        # Enviar señal HIGH para cambiar color
        led_pin.value(1)  # Enviar HIGH
        print(f"Color: {color}")
        client.publish(MQTT_TOPIC_PUB, color)  # Publicar el color en el broker MQTT
        time.sleep(2)  # Esperar 2 segundos antes de cambiar al siguiente color

        # Enviar señal LOW para mantener el color
        led_pin.value(0)  # Enviar LOW
        time.sleep(1)  # Esperar 1 segundo

# Conectar a WiFi
conectar_wifi()

# Conectar al broker MQTT
conectar_mqtt()

# Bucle principal para cambiar de color
while True:
    try:
        cambiar_color()  # Cambiar de color en el LED RGB de 7 colores
    except OSError as e:
        print(f"Error al leer el sensor o al publicar el mensaje: {e}")
        conectar_mqtt()  # Intentar reconectar a MQTT en caso de error

    time.sleep(1)  # Esperar antes de cambiar de color nuevamente
