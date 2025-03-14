import machine
import time
import network
from umqtt.simple import MQTTClient

# Configuración WiFi y MQTT
SSID = "iPhone de Noe"
PASSWORD = "123412345"
MQTT_BROKER = "172.20.10.2"
MQTT_TOPIC = "ncm/sensor"

# Conectar a WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    print("Conectando a WiFi...")
    time.sleep(1)

print("✅ Conectado a WiFi!")

# Conectar a MQTT
client = MQTTClient("ESP32", MQTT_BROKER)
client.connect()
print("✅ Conectado a MQTT!")


pin_digital = machine.Pin(32, machine.Pin.IN)

try:
    while True:
        estado = pin_digital.value()  
        if estado == 1:
            print("⚠ ¡Gas detectado! ⚠")
            client.publish(MQTT_TOPIC, "645")
        else:
            print("✅ Aire limpio")
        
        time.sleep(3)
except KeyboardInterrupt:
    print("Programa terminado")