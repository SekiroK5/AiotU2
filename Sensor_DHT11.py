from machine import Pin
import dht
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor DHT11
sensor = dht.DHT11(Pin(4))

# Configuración WiFi
WIFI_SSID = "vivoQR"
WIFI_PASSWORD = "73hgj3jg"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_dht11"
MQTT_BROKER = "192.168.36.212"  
MQTT_PORT = 1883
MQTT_TOPIC_TEMP = "utng"
MQTT_TOPIC_HUM = "utng"

# Variables para almacenar el último valor enviado
last_temp = None
last_hum = None
errores_conexion = 0  # Contador de errores MQTT

# Función para conectar a WiFi
def conectar_wifi():
    print("[INFO] Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.5)
    
    print("\n[INFO] WiFi Conectada!")
    print(f"[INFO] Dirección IP: {sta_if.ifconfig()[0]}")

# Función para conectar a MQTT
def conectar_mqtt():
    global errores_conexion
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
        errores_conexion = 0  # Reiniciamos el contador de errores
        return client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MQTT: {e}")
        errores_conexion += 1
        return None

# Conectar a WiFi
conectar_wifi()

# Conectar a MQTT
client = conectar_mqtt()

# Bucle principal
while True:
    try:
        # Verificar si WiFi sigue activo
        if not network.WLAN(network.STA_IF).isconnected():
            print("[ERROR] WiFi desconectado, reconectando...")
            conectar_wifi()
            client = conectar_mqtt()

        # Si MQTT se desconectó, intentamos reconectar
        if client is None:
            print("[ERROR] MQTT desconectado, intentando reconectar...")
            client = conectar_mqtt()
            time.sleep(5)
            continue  # Volvemos al inicio del loop

        # Leer datos del sensor
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        # Si hay un cambio en los valores, enviamos los datos
        if temp != last_temp or hum != last_hum:
            print("[INFO] Cambio detectado en los valores!")
            print(f"Temperatura: {temp}°C")
            print(f"Humedad: {hum}%")

            try:
                client.publish(MQTT_TOPIC_TEMP, str(temp))
                client.publish(MQTT_TOPIC_HUM, str(hum))
                print("[INFO] Datos enviados a Raspberry Pi vía MQTT")
                
                last_temp = temp
                last_hum = hum

            except Exception as e:
                print(f"[ERROR] Error al publicar en MQTT: {e}")
                client = None  # Forzar reconexión en el próximo ciclo

        # Si hay demasiados errores seguidos, reiniciar WiFi y MQTT
        if errores_conexion >= 10:
            print("[ERROR] Demasiados errores MQTT, reiniciando conexión WiFi y MQTT...")
            conectar_wifi()
            client = conectar_mqtt()
            errores_conexion = 0  # Reiniciar contador de errores

    except OSError as e:
        print(f"[ERROR] Error al leer el sensor: {e}")

    time.sleep(2)  # Leer cada 2 segundos