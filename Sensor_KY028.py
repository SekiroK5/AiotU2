from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor KY-028
sensor_pin = ADC(Pin(35))  # Entrada analógica
sensor_pin.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V

# Configuración WiFi
WIFI_SSID = "iPhone de Noe"
WIFI_PASSWORD = "123412345"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky028_temp"
MQTT_BROKER = "172.20.10.2"  # IP del broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "ncm/sensor"

# Variables para almacenar el último valor enviado
ultima_temperatura = None
umbral_cambio = 0.2  # Reducimos el umbral a 0.2°C
num_muestras = 5  # Número de lecturas para promediar
ultimo_envio = time.time()  # Guardar tiempo del último envío
intervalo_envio = 10  # Publicar cada 10 segundos si no hay cambios
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

# Función para conectar/reconectar a MQTT
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

# Bucle principal para leer el sensor KY-028
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

        # Tomamos varias lecturas y calculamos el promedio
        suma_valores = 0
        for _ in range(num_muestras):
            suma_valores += sensor_pin.read()
            time.sleep(0.1)  # Pequeña pausa entre lecturas
        
        valor_adc_prom = suma_valores / num_muestras

        # Convertir el valor ADC a temperatura aproximada
        temperatura = (valor_adc_prom / 4095) * 100  # Ajusta según calibración

        print(f"[DEBUG] Valor ADC: {valor_adc_prom} -> Temperatura: {temperatura:.1f}°C")

        # Verificar si hubo un cambio significativo o si han pasado 10s
        tiempo_actual = time.time()
        if (ultima_temperatura is None or abs(temperatura - ultima_temperatura) >= umbral_cambio) or (tiempo_actual - ultimo_envio >= intervalo_envio):
            mensaje = f"Temperatura: {temperatura:.1f}°C"
            print(f"[INFO] Publicando MQTT: {mensaje}")
            try:
                client.publish(MQTT_TOPIC_PUB, mensaje)
                ultima_temperatura = temperatura  # Guardar el último valor enviado
                ultimo_envio = tiempo_actual  # Actualizar el tiempo del último envío
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
