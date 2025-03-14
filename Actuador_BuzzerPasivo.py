from machine import Pin, PWM
import time
import network
import random
from umqtt.simple import MQTTClient

# Definir el pin del buzzer
BUZZER_PIN = 4
buzzer = PWM(Pin(BUZZER_PIN))

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_buzzer"
MQTT_BROKER = "172.20.10.2"  # IP del broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"

# Definición de notas musicales
NOTES = {
    "B0": 31, "C1": 33, "D1": 37, "E1": 41, "F1": 44, "G1": 49, "A1": 55, "B1": 62,
    "C2": 65, "D2": 73, "E2": 82, "F2": 87, "G2": 98, "A2": 110, "B2": 123,
    "C3": 131, "D3": 147, "E3": 165, "F3": 175, "G3": 196, "A3": 220, "B3": 247,
    "C4": 262, "D4": 294, "E4": 330, "F4": 349, "G4": 392, "A4": 440, "B4": 494,
    "C5": 523, "D5": 587, "E5": 659, "F5": 698, "G5": 784, "A5": 880, "B5": 988,
    "C6": 1047, "D6": 1175, "E6": 1319, "F6": 1397, "G6": 1568, "A6": 1760, "B6": 1976,
}

# Melodías
melodias = {
    "Imperial March": (["A4", "A4", "A4", "F4", "C5", "A4", "F4", "C5", "A4"], [350, 350, 350, 250, 100, 350, 250, 100, 700]),
    "Super Mario": (["E5", "E5", "C5", "E5", "G5", "C5"], [150, 150, 150, 150, 150, 300]),
    "Jingle Bells": (["E5", "E5", "E5", "E5", "E5", "E5"], [200, 200, 400, 200, 200, 400])
}

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

# Función para reproducir una melodía
def reproducir_melodia(nombre, client):
    notas, duraciones = melodias[nombre]
    print(f"[INFO] Reproduciendo: {nombre}")
    client.publish(MQTT_TOPIC_PUB, nombre)  # Enviar el nombre de la melodía por MQTT
    for i in range(len(notas)):
        if notas[i] in NOTES:
            buzzer.freq(NOTES[notas[i]])
            buzzer.duty(512)  # Volumen del buzzer
        time.sleep_ms(duraciones[i])
        buzzer.duty(0)  # Apagar el buzzer entre notas
        time.sleep_ms(50)

# Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_mqtt()

# Bucle principal con reproducción aleatoria
while True:
    for _ in range(5):  # Reproducir 5 veces antes de una pausa larga
        melodia_aleatoria = random.choice(list(melodias.keys()))
        reproducir_melodia(melodia_aleatoria, client)
        
        pausa_aleatoria = random.uniform(1.0, 3.0)  # Pausa aleatoria entre 1 y 3 segundos
        time.sleep(pausa_aleatoria)

    print("[INFO] Pausa larga antes de reiniciar el ciclo.")
    time.sleep(10)  # Pausa larga después de 5 melodías
