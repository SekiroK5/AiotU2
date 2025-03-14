from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del buzzer activo
BUZZER_PIN = 4
buzzer = Pin(BUZZER_PIN, Pin.OUT)

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_buzzer"
MQTT_BROKER = "172.20.10.2"  # IP del broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"

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

# Función para conectar a MQTT
def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
    return client

# Función para emitir un pitido fuerte y largo
def emitir_pitido(client):
    print("[INFO] Buzzer ENCENDIDO")
    client.publish(MQTT_TOPIC_PUB, "Buzzer ENCENDIDO")  # Enviar estado ENCENDIDO

    # Pitido fuerte y largo (activando/desactivando varias veces para mayor impacto)
    for _ in range(5):  # Repetir 5 veces
        buzzer.on()
        time.sleep(0.4)  # Mantener encendido 0.4 segundos
        buzzer.off()
        time.sleep(0.1)  # Pequeña pausa antes de volver a encender

    print("[INFO] Buzzer APAGADO")
    client.publish(MQTT_TOPIC_PUB, "Buzzer APAGADO")  # Enviar estado APAGADO

# Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_mqtt()

# Bucle principal: emitir pitido cada cierto tiempo
while True:
    emitir_pitido(client)
    time.sleep(10)  # Intervalo de 10 segundos entre pitidos
