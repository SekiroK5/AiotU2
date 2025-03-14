from machine import ADC, Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración WiFi y MQTT
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

print(f"✅ Conectado a WiFi! IP: {wifi.ifconfig()[0]}")

# Conectar a MQTT con un ID único
client = MQTTClient("ESP32_LDR_" + str(time.ticks_ms()), MQTT_BROKER)
time.sleep(2)  # Espera tras conectar
client.connect()
print("✅ Conectado a MQTT!")

# Configurar el sensor LDR (KY-018)
ldr = ADC(Pin(34))  
ldr.atten(ADC.ATTN_11DB)  # Rango 0-4095

while True:
    valor_ldr = ldr.read()
    print(f"Valor LDR (ADC): {valor_ldr}")

    # Publicar siempre en MQTT, sin importar el valor
    try:
        client.publish(MQTT_TOPIC, str(valor_ldr))
        print(f"📤 Publicado en MQTT: {valor_ldr}")
    except Exception as e:
        print(f"❌ Error al publicar: {e}")
        client.connect()  # Reintentar conexión MQTT

    time.sleep(5)  # Espera 5 segundos
