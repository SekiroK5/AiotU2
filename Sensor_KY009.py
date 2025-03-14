from machine import Pin, PWM
import time
import network
import random
from umqtt.simple import MQTTClient

# Pines del módulo KY-009 (RGB)
pin_rojo = PWM(Pin(15), freq=1000)   # Rojo
pin_verde = PWM(Pin(2), freq=1000)   # Verde
pin_azul = PWM(Pin(4), freq=1000)    # Azul

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky009_rgb"
MQTT_BROKER = "172.20.10.2"  # Cambia a la IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic para enviar el color actual

# Tabla de colores aproximados con sus valores RGB
colores_aproximados = {
    "Rojo": (255, 0, 0),
    "Verde": (0, 255, 0),
    "Azul": (0, 0, 255),
    "Amarillo": (255, 255, 0),
    "Cian": (0, 255, 255),
    "Magenta": (255, 0, 255),
    "Blanco": (255, 255, 255),
    "Naranja": (255, 165, 0)
}

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

# Función para establecer un color RGB en el LED
def set_color(r, g, b):
    pin_rojo.duty(int(r * 4.01))   # 255 * 4.01 ≈ 1023
    pin_verde.duty(int(g * 4.01))
    pin_azul.duty(int(b * 4.01))

# Función para encontrar el nombre del color más cercano
def color_mas_cercano(r, g, b):
    def distancia(c1, c2):
        return sum((a - b) ** 2 for a, b in zip(c1, c2))
    
    return min(colores_aproximados, key=lambda c: distancia((r, g, b), colores_aproximados[c]))

# Función para generar un color aleatorio
def color_aleatorio():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

# Conectar a WiFi
conectar_wifi()

# Conectar al broker MQTT
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
client.connect()
print(f"Conectado a {MQTT_BROKER}")

# Bucle principal
while True:
    try:
        # Generar un nuevo color aleatorio
        r, g, b = color_aleatorio()
        set_color(r, g, b)

        # Determinar el color más cercano por nombre
        color_nombre = color_mas_cercano(r, g, b)

        # Enviar el color actual por MQTT
        print(f"Publicando nuevo color: {color_nombre}")
        client.publish(MQTT_TOPIC_PUB, color_nombre)

    except OSError as e:
        print("Error al actualizar el color:", e)

    time.sleep(5)  # Cambiar de color cada 5 segundos
