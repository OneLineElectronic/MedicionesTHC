from microdot import Microdot, send_file
import dht
import machine
import ujson
import time
import network # Importar network para la conexión Wi-Fi

# Pin GPIO al que esta conectado el sensor DHT11
DHT_PIN = 4 # Puedes cambiar este numero al pin que estes usando

# Inicializar el sensor DHT11
try:
    d = dht.DHT11(machine.Pin(DHT_PIN))
    print(f"Sensor DHT11 inicializado en el pin GPIO {DHT_PIN}")
except Exception as e:
    print(f"Error al inicializar el sensor DHT11: {e}")
    d = None # Establecer d a None si falla la inicializacion

app = Microdot()

# Ruta para la pagina principal
@app.route('/')
def index(request):
    return send_file('index.html')

# Ruta para obtener los datos del sensor
@app.route('/data')
def get_sensor_data(request):
    temperature = None
    humidity = None
    if d:
        try:
            d.measure()
            time.sleep_ms(100) # Pequeno retardo para asegurar la lectura
            temperature = d.temperature()
            humidity = d.humidity()
            print(f"Lectura del sensor: Temp={temperature}C, Hum={humidity}%")
        except Exception as e:
            print(f"Error al leer el sensor DHT11: {e}")
            temperature = None
            humidity = None
    
    response_data = {
        'temperature': temperature,
        'humidity': humidity,
        'timestamp': time.time()
    }
    return ujson.dumps(response_data), {'Content-Type': 'application/json'}

# Funcion para configurar la red Wi-Fi
def connect_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    if not station.isconnected():
        print(f'Conectando a la red {ssid}...')
        station.connect(ssid, password)
        # Esperar hasta que la conexion se establezca o falle
        max_attempts = 10
        attempts = 0
        while not station.isconnected() and attempts < max_attempts:
            time.sleep(1)
            attempts += 1
            print(f'Intento de conexion: {attempts}/{max_attempts}...')
        
        if station.isconnected():
            print('Conexion Wi-Fi exitosa!')
            print('Configuracion de red:', station.ifconfig())
        else:
            print('Fallo la conexion Wi-Fi.')
    else:
        print('Ya conectado a la red Wi-Fi:', station.ifconfig())

# --- Configura tu red Wi-Fi aqui ---
WIFI_SSID = 'nombre_de_tu_red'
WIFI_PASSWORD = 'contraseña_de_tu_red'
# -----------------------------------

if __name__ == '__main__':
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    if network.WLAN(network.STA_IF).isconnected():
        try:
            print('Servidor Microdot iniciando en el puerto 80...')
            app.run(port=80, debug=True) # debug=True para ver logs en la consola
        except KeyboardInterrupt:
            pass
        finally:
            app.shutdown()
            print('Servidor Microdot apagado.')
    else:
        print("No se pudo iniciar el servidor Microdot debido a la falta de conexion Wi-Fi.")