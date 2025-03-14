from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-032
sensor_digital = Pin(17, Pin.IN)  # Pin de salida digital del sensor

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky032"
MQTT_BROKER = "172.20.10.2"  # IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic MQTT para detección de obstáculos
KEEP_ALIVE = 30  # Tiempo máximo sin actividad antes de que MQTT cierre la conexión

# Variables de control
ultimo_estado = None  
ultimo_envio = 0  # Último tiempo de publicación
intervalo_envio = 5  # Segundos para reenviar estado si no cambia
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
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, keepalive=KEEP_ALIVE)
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
        # Leer el estado del sensor (0 = obstáculo detectado, 1 = sin obstáculos)
        estado = sensor_digital.value()
        mensaje_estado = "🚧 Obstáculo detectado" if estado == 0 else "✅ Camino libre"

        # Obtener el tiempo actual
        tiempo_actual = time.time()

        # Publicar si el estado cambió o si ha pasado el intervalo de reenvío
        if estado != ultimo_estado or (tiempo_actual - ultimo_envio >= intervalo_envio):
            print(f"Publicando: {mensaje_estado}")
            client.publish(MQTT_TOPIC_PUB, mensaje_estado)
            ultimo_estado = estado  # Guardamos el estado actual
            ultimo_envio = tiempo_actual  # Actualizamos el tiempo del último envío

        # Enviar un "ping" cada cierto tiempo para mantener la conexión MQTT
        client.ping()

    except OSError as e:
        print(f"Error en MQTT: {e}")
        conectar_mqtt()  # Intentar reconectar a MQTT en caso de error

    time.sleep(0.5)  # Leer cada 500 ms para respuesta más rápida
