import network
import time
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# 🔹 Configuración de la red Wi-Fi
wifi_ssid = "iPhone de Noe"  # Cambia por tu SSID
wifi_password = "123412345"  # Cambia por tu contraseña

# 🔹 Configuración del broker MQTT
mqtt_broker = "172.20.10.2"  # IP del broker
mqtt_port = 1883
mqtt_topic = "ncm/sensor"  # Nuevo topic para la vibración

# 🔹 Configuración del motor vibrador (PWM)
motor = PWM(Pin(17), freq=1000)  # Frecuencia de 1 kHz

# 📡 Función para conectar a Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Conexión Wi-Fi exitosa:', wlan.ifconfig())

# 🔗 Función para conectar al broker MQTT
def connect_mqtt():
    try:
        client = MQTTClient("vibration_client", mqtt_broker, mqtt_port)
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

# 🚀 Función para activar vibración y enviar datos por MQTT
def vibrar(intensidad, duracion, nivel, client):
    motor.duty(intensidad)  # Ajusta la intensidad (0-1023)
    
    mensaje = str(nivel)
    try:
        client.publish(mqtt_topic, mensaje)
        print("Datos enviados por MQTT:", mensaje)
    except Exception as e:
        print("Error al enviar datos MQTT:", e)
    
    time.sleep(duracion)
    motor.duty(0)  # Apagar vibración

# 🔌 Conectar Wi-Fi y MQTT
connect_wifi()
client = connect_mqtt()

# 🔄 Bucle principal
while client:
    vibrar(300, 1, 1, client)  # Vibración suave
    time.sleep(1)

    vibrar(600, 1, 2, client)  # Vibración media
    time.sleep(1)

    vibrar(1023, 1, 3, client)  # Vibración fuerte
    time.sleep(2)