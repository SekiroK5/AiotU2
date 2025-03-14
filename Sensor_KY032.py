from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-032
SENSOR_PIN = 18  # GPIO donde está conectado el sensor
sensor = Pin(SENSOR_PIN, Pin.IN)

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky003"
MQTT_BROKER = "172.20.10.2"  # Cambia esto por la IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC = "ncm/sensor"

# Función para conectar WiFi
def conectar_wifi():
    print("[INFO] Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print("\n[INFO] Conectado a WiFi!")

# Función para conectar MQTT
def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
    return client

# Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_mqtt()

# Estado anterior del sensor
estado_anterior = sensor.value()
ultimo_cambio = time.ticks_ms()
tiempo_estable = 500  # Tiempo mínimo en ms para considerar el cambio como válido

# Bucle principal
while True:
    estado_actual = sensor.value()  # Leer el estado del sensor

    # Si el estado cambia, esperar para confirmar estabilidad
    if estado_actual != estado_anterior:
        time.sleep_ms(50)  # Pequeño delay para evitar ruido

        # Verificar si sigue en el mismo estado después del delay
        if sensor.value() == estado_actual:
            # Si el estado se ha mantenido estable por un tiempo, enviar el mensaje
            if time.ticks_diff(time.ticks_ms(), ultimo_cambio) > tiempo_estable:
                if estado_actual == 0:
                    mensaje = "Objeto detectado a 2 cm o menos"
                else:
                    mensaje = "No hay objeto cercano"

                print(f"[INFO] {mensaje}")
                client.publish(MQTT_TOPIC, mensaje.encode())  # Publicar en MQTT
                ultimo_cambio = time.ticks_ms()  # Actualizar el tiempo del último cambio
                estado_anterior = estado_actual  # Actualizar estado

    time.sleep(0.1)  # Pequeña pausa para evitar consumir demasiada CPU
