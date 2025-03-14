from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-024
sensor_digital = Pin(17, Pin.IN)  # Salida digital del KY-024
sensor_analogico = ADC(Pin(35))  # Salida analógica del KY-024
sensor_analogico.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky024_hall"
MQTT_BROKER = "172.20.10.2"  # Cambia a la IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic para la detección del campo magnético

# Variables para almacenar los últimos valores enviados
ultimo_estado = None
ultimo_nivel = None
umbral_cambio = 100  # Cambio significativo en el nivel analógico para enviar

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
        time.sleep(5)  # Esperar antes de reintentar
        conectar_mqtt()  # Reintentar la conexión

# Conectar a WiFi y MQTT al inicio
conectar_wifi()
conectar_mqtt()

# Bucle principal
while True:
    try:
        # Leer el estado del sensor (0 = sin campo, 1 = campo detectado)
        estado = sensor_digital.value()
        mensaje_estado = "Campo Magnético Detectado" if estado == 1 else "Sin Campo Magnético"

        # Leer el valor analógico de la intensidad del campo
        nivel = sensor_analogico.read()

        # Solo publicamos si hay un cambio en el estado o en la intensidad
        if estado != ultimo_estado or (ultimo_nivel is None or abs(nivel - ultimo_nivel) > umbral_cambio):
            mensaje = f"{mensaje_estado} - Intensidad: {nivel}"
            print(f"Publicando: {mensaje}")
            client.publish(MQTT_TOPIC_PUB, mensaje)

            # Guardamos los valores para la próxima comparación
            ultimo_estado = estado
            ultimo_nivel = nivel

    except OSError as e:
        print(f"Error de comunicación: {e}")
        conectar_mqtt()  # Reconectar a MQTT en caso de error

    time.sleep(1)  # Leer cada 1 segundo
