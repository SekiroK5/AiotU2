from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración de pines del KY-026
sensor_digital = Pin(17, Pin.IN)  # Salida digital (0 = llama detectada, 1 = sin llama)
sensor_analogico = ADC(Pin(35))  # Salida analógica (intensidad de la llama)
sensor_analogico.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky026_llama"
MQTT_BROKER = "172.20.10.2"  # Cambia esto por la IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic MQTT para la detección de llama

# Variables de control
ultimo_estado = None  # Estado anterior del sensor digital
ultimo_nivel = None   # Última intensidad medida
umbral_cambio = 100   # Diferencia mínima en intensidad para enviar

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
        # Leer el estado del sensor digital (0 = llama detectada, 1 = sin llama)
        estado = sensor_digital.value()
        mensaje_estado = "🔥 Llama detectada" if estado == 0 else "✅ No hay llama"

        # Leer la intensidad de la llama (valor analógico)
        nivel = sensor_analogico.read()

        # Publicar SIEMPRE el estado de la llama
        if estado != ultimo_estado:
            print(f"Publicando: {mensaje_estado}")
            client.publish(MQTT_TOPIC_PUB, mensaje_estado)
            ultimo_estado = estado  # Actualizamos el estado para la próxima iteración

        # Publicar solo si la intensidad cambia significativamente
        if ultimo_nivel is None or abs(nivel - ultimo_nivel) > umbral_cambio:
            mensaje_nivel = f"🔥 Intensidad de la llama: {nivel}"
            print(f"Publicando: {mensaje_nivel}")
            client.publish(MQTT_TOPIC_PUB, mensaje_nivel)
            ultimo_nivel = nivel  # Guardamos el último nivel leído

    except OSError as e:
        print(f"Error al leer el sensor: {e}")
        conectar_mqtt()  # Intentar reconectar en caso de error

    time.sleep(1)  # Leer cada 1 segundo
