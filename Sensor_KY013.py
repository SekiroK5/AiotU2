import network
import time
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración de la red Wi-Fi
wifi_ssid = "iPhone de Noe"
wifi_password = "123412345"  # Cambia por tu contraseña

# Configuración del broker MQTT
mqtt_broker = "172.20.10.2"  # IP del broker
mqtt_port = 1883
mqtt_topic = "ncm/sensor"

# Configuración del sensor KY-013
sensor_temp = ADC(Pin(32))  # Usar un pin ADC (Ejemplo: GPIO34)
sensor_temp.atten(ADC.ATTN_11DB)  # Permite medir hasta 3.3V

# Conexión Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Conexión Wi-Fi exitosa:', wlan.ifconfig())

# Conexión MQTT
def connect_mqtt():
    try:
        client = MQTTClient("sensor_temp_client", mqtt_broker, mqtt_port)
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

def leer_temperatura():
    valor_adc = sensor_temp.read()
    voltaje = valor_adc * (3.3 / 4095)  # Convertir a voltaje
    resistencia = (10000 * voltaje) / (3.3 - voltaje)  # Calcular resistencia del termistor
    temperatura_c = 3950 / ((3950 / 298.15) + (resistencia / 10000)) - 273.15  # Conversión usando la ecuación NTC
    return temperatura_c


# Enviar datos cada 10 segundos
def publish_data(client):
    if client is None:
        print("Cliente MQTT no disponible, reintentando conexión...")
        return
    
    try:
        temperatura = leer_temperatura()
        payload = str(temperatura)  # Convertir el valor a string
        client.publish(mqtt_topic, payload)
        print("Datos enviados:", payload, "°C")

    except Exception as e:
        print("Error al leer el sensor o enviar datos:", e)

# Main
connect_wifi()
client = connect_mqtt()

while True:
    publish_data(client)
    time.sleep(10)  # Esperar 10 segundos antes del próximo envío