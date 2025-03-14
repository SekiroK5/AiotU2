from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración de pines del KY-029
pin_rojo = Pin(26, Pin.OUT)  # LED Rojo
pin_azul = Pin(27, Pin.OUT)  # LED Azul

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky029_led"
MQTT_BROKER = "172.20.10.2"  # IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic para enviar el color del LED

# Variable para rastrear el color actual
ultimo_color = None
colores = ["Apagado", "Rojo", "Amarillo"]

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

# Función para conectar a MQTT con reconexión automática
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

# Función para cambiar el color del LED
def cambiar_color():
    global ultimo_color
    estado = (ultimo_color + 1) % 3  # Cambia entre 0 (Apagado), 1 (Rojo), 2 (Azul)

    if estado == 0:
        pin_rojo.value(0)
        pin_azul.value(0)
    elif estado == 1:
        pin_rojo.value(1)
        pin_azul.value(0)
    elif estado == 2:
        pin_rojo.value(0)
        pin_azul.value(1)

    # Publicar el color actual en MQTT solo si ha cambiado
    if estado != ultimo_color:
        mensaje = f"Color: {colores[estado]}"
        print(f"Publicando: {mensaje}")
        client.publish(MQTT_TOPIC_PUB, mensaje)
        ultimo_color = estado

# Conectar a WiFi y MQTT
conectar_wifi()
conectar_mqtt()

# Inicializar en "Apagado"
ultimo_color = 0
cambiar_color()

# Bucle principal: cambiar de color cada 2 segundos
while True:
    try:
        cambiar_color()
    except OSError as e:
        print(f"Error de comunicación: {e}")
        conectar_mqtt()  # Intentar reconectar en caso de fallo

    time.sleep(2)  # Esperar 2 segundos antes de cambiar el color nuevamente
