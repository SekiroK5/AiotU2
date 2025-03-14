from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor MQ-07
sensor_digital = Pin(17, Pin.IN)  # Salida digital (1 = sin gas, 0 = gas detectado)
sensor_analogico = ADC(Pin(35))  # Salida analógica (nivel de CO)
sensor_analogico.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_mq07"
MQTT_BROKER = "172.20.10.2"  # Cambia esto por la IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic MQTT para el monóxido de carbono

# Variables de control
ultimo_estado = None  # Último estado del sensor digital
ultimo_nivel = None   # Última concentración medida
umbral_cambio = 100   # Cambio mínimo en el nivel analógico para enviar

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
        # Leer el estado del sensor digital (0 = CO detectado, 1 = sin CO)
        estado = sensor_digital.value()
        mensaje_estado = "⚠️ CO Detectado" if estado == 0 else "✅ Aire limpio"

        # Leer la c7oncentración de CO en el aire
        nivel = sensor_analogico.read()

        # Publicar SIEMPRE el estado del sensor digital
        if estado != ultimo_estado:
            print(f"Publicando: {mensaje_estado}")
            client.publish(MQTT_TOPIC_PUB, mensaje_estado)
            ultimo_estado = estado  # Guardamos el estado

        # Publicar solo si la concentración cambia significativamente
        if ultimo_nivel is None or abs(nivel - ultimo_nivel) > umbral_cambio:
            mensaje_nivel = f"🌡 {nivel}"
            print(f"Publicando: {mensaje_nivel}")
            client.publish(MQTT_TOPIC_PUB, mensaje_nivel)
            ultimo_nivel = nivel  # Guardamos el último nivel leído

    except OSError as e:
        print(f"Error al leer el sensor: {e}")
        conectar_mqtt()  # Intentar reconectar a MQTT en caso de error

    time.sleep(1)  # Leer cada 1 segundo
