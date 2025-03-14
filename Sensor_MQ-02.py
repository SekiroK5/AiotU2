from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor MQ-2
sensor_digital = Pin(17, Pin.IN)  # Salida digital del MQ-2 (0 = gas detectado, 1 = sin gas)
sensor_analogico = ADC(Pin(35))   # Salida analógica del MQ-2 (concentración de gas)
sensor_analogico.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_mq2"
MQTT_BROKER = "172.20.10.2"  # IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic MQTT para la detección de gas
KEEP_ALIVE = 30

# Variables de control
ultimo_estado = None  
ultimo_valor = None  
umbral_cambio = 200  # Cambio mínimo en la señal analógica para publicar
ultimo_envio = 0  
intervalo_envio = 5  # Segundos para reenviar estado aunque no cambie
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
        # Leer el estado del sensor (0 = gas detectado, 1 = sin gas)
        estado = sensor_digital.value()
        mensaje_estado = "!Gas detectado!" if estado == 0 else "Aire limpio!!!"

        # Leer la concentración de gas (salida analógica)
        valor_analogico = sensor_analogico.read()

        # Obtener el tiempo actual
        tiempo_actual = time.time()

        # Publicar si hay un cambio en el estado digital o en la concentración de gas
        if (estado != ultimo_estado or 
            (ultimo_valor is None or abs(valor_analogico - ultimo_valor) > umbral_cambio) or 
            (tiempo_actual - ultimo_envio >= intervalo_envio)):

            mensaje = f"{mensaje_estado} - Concentración: {valor_analogico}"
            print(f"Publicando: {mensaje}")
            client.publish(MQTT_TOPIC_PUB, mensaje)

            # Guardamos los valores
            ultimo_estado = estado
            ultimo_valor = valor_analogico
            ultimo_envio = tiempo_actual  # Actualizamos el tiempo del último envío

        # Mantener la conexión MQTT activa
        client.ping()

    except OSError as e:
        print(f"Error en MQTT: {e}")
        conectar_mqtt()  # Intentar reconectar a MQTT en caso de error

    time.sleep(0.5)  # Leer cada 500 ms
