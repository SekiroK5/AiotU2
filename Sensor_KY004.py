from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del KY-004 (botón pulsador)
boton = Pin(17, Pin.IN, Pin.PULL_UP)  # Botón con resistencia pull-up

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky004"
MQTT_BROKER = "172.20.10.2"  # IP del broker MQTT
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
        # Leer el estado del botón (0 = Presionado, 1 = No presionado)
        estado_boton = boton.value()
        mensaje = "🔘 Botón presionado" if estado_boton == 0 else "⚪ Botón liberado"

        # Publicar solo si cambia el estado
        if estado_boton != ultimo_estado:
            print(f"Publicando: {mensaje}")
            client.publish(MQTT_TOPIC_PUB, mensaje)
            ultimo_estado = estado_boton  # Guardamos el estado actual

    except OSError as e:
        print(f"Error al leer el botón: {e}")
        conectar_mqtt()  # Intentar reconectar a MQTT en caso de error

    time.sleep(0.1)  # Leer cada 100 ms para respuesta rápida
