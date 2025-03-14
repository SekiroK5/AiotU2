from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración del KY-023
x_axis = ADC(Pin(34))  # Eje X (Salida analógica)
y_axis = ADC(Pin(35))  # Eje Y (Salida analógica)
z_button = Pin(17, Pin.IN, Pin.PULL_UP)  # Botón Z (Salida digital)

x_axis.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V
y_axis.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky023_joystick"
MQTT_BROKER = "172.20.10.2"  # IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"  # Topic para enviar los datos del joystick

# Variables para evitar enviar datos sin cambios
ultimo_x = None
ultimo_y = None
ultimo_z = None
umbral_cambio = 200  # Diferencia mínima para considerar un cambio significativo

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

# Función para conectar a MQTT con reconexión automática
def conectar_mqtt():
    global client
    try:
        print("Conectando a MQTT...")
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"Conectado a {MQTT_BROKER}")
    except OSError as e:
        print(f"Error al conectar a MQTT: {e}")
        time.sleep(5)
        conectar_mqtt()

# Conectar a WiFi y MQTT
conectar_wifi()
conectar_mqtt()

# Bucle principal para leer los datos del joystick
while True:
    try:
        x_val = x_axis.read()
        y_val = y_axis.read()
        z_val = 0 if z_button.value() == 0 else 1  # 0 = Botón presionado, 1 = No presionado

        # Solo enviamos si hay un cambio significativo en los valores
        if (
            (ultimo_x is None or abs(x_val - ultimo_x) > umbral_cambio) or
            (ultimo_y is None or abs(y_val - ultimo_y) > umbral_cambio) or
            (ultimo_z is None or z_val != ultimo_z)
        ):
            mensaje = f"X: {x_val}, Y: {y_val}, Z: {'Presionado' if z_val == 0 else 'No presionado'}"
            print(f"Publicando: {mensaje}")
            client.publish(MQTT_TOPIC_PUB, mensaje)

            # Guardamos los valores actuales para la siguiente comparación
            ultimo_x = x_val
            ultimo_y = y_val
            ultimo_z = z_val

    except OSError as e:
        print(f"Error de comunicación: {e}")
        conectar_mqtt()  # Intentar reconectar en caso de error

    time.sleep(0.5)  # Leer cada 500ms para mejor respuesta
