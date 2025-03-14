from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor MQ-4
sensor_analogico = ADC(Pin(35))  # Lectura de nivel de gas (0-4095)
sensor_analogico.atten(ADC.ATTN_11DB)  # Rango 0 a 3.3V
sensor_digital = Pin(17, Pin.IN)  # Detección binaria de gas

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_mq4"
MQTT_BROKER = "172.20.10.2"  # IP del broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"

# Variables para almacenar los últimos valores enviados
ultimo_nivel = None
ultimo_estado = None
umbral_cambio = 100  # Cambio significativo para enviar dato

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
        # Leer la concentración de gas (0-4095)
        nivel_gas = sensor_analogico.read()
        estado_gas = sensor_digital.value()  # 0 = Gas detectado, 1 = No gas

        mensaje_estado = "🔥 Gas detectado" if estado_gas == 0 else "✅ Aire limpio"
        mensaje_nivel = f"Nivel de gas: {nivel_gas}"

        # Publicar si hay un cambio significativo en el nivel de gas
        if ultimo_nivel is None or abs(nivel_gas - ultimo_nivel) > umbral_cambio:
            print(f"Publicando: {mensaje_nivel}")
            client.publish(MQTT_TOPIC_PUB, mensaje_nivel)
            ultimo_nivel = nivel_gas

        # Publicar si cambia la detección binaria de gas
        if estado_gas != ultimo_estado:
            print(f"Publicando: {mensaje_estado}")
            client.publish(MQTT_TOPIC_PUB, mensaje_estado)
            ultimo_estado = estado_gas

    except OSError as e:
        print(f"Error al leer el sensor: {e}")
        conectar_mqtt()  # Intentar reconectar a MQTT en caso de error

    time.sleep(2)  # Leer cada 2 segundos
