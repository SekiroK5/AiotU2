import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del relé y conexión Wi-Fi
RELAY_PIN = 27  # Pin donde conectas el relé (GPIO 27 como ejemplo)
MQTT_BROKER = "172.20.10.2"
MQTT_TOPIC = "ncm/sensor"
MQTT_CLIENT_ID = "rele_sensor_{}".format(int(time.time()))
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Inicializar el relé como salida digital
rele = Pin(RELAY_PIN, Pin.OUT)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    for _ in range(15):
        if wlan.isconnected():
            print("✅ Wi-Fi conectado:", wlan.ifconfig())
            return wlan
        time.sleep(1)
    
    print("❌ No se pudo conectar a Wi-Fi")
    return None

def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("✅ Conectado a MQTT")
        return client
    except Exception as e:
        print("❌ Error MQTT:", e)
        return None

def publish_relay_state(client, state):
    if client:
        try:
            client.publish(MQTT_TOPIC, str(state))
            print("📡 Estado del relé enviado:", state)
        except Exception as e:
            print("❌ Error al publicar:", e)

# Conectar Wi-Fi y MQTT
wlan = connect_wifi()
if wlan:
    client = connect_mqtt()
    
    while True:
        if not wlan.isconnected():
            print("⚠ Wi-Fi desconectado, reconectando...")
            wlan = connect_wifi()
        
        if not client:
            print("⚠ Reintentando conexión MQTT...")
            client = connect_mqtt()
        
        # Aquí controlas el estado del relé: enciendes y apagas el relé alternadamente
        rele.value(1)  # Enciende el relé (estado ON)
        publish_relay_state(client, 1)  # Envía '1' si está encendido
        time.sleep(2)  # Espera 2 segundos

        rele.value(0)  # Apaga el relé (estado OFF)
        publish_relay_state(client, 0)  # Envía '0' si está apagado
        time.sleep(2)  # Espera 2 segundos
else:
    print("❌ No se pudo conectar a Wi-Fi.")