import serial
import serial.tools.list_ports
import json
from datetime import datetime
import threading

def port_selector():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No se encontraron puertos seriales disponibles.")
        return None
    print("Puertos disponibles:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port.device} - {port.description}")
    while True:
        selection = input("Selecciona el número del puerto: ").strip()
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(ports):
                return ports[idx].device
        print("Selección inválida. Intenta de nuevo.")

def read_from_serial(buffer_sensors, port_sel):
    #counter = 0
    try:
        with serial.Serial(port_sel, 9600, timeout=1) as ser:
            print(f"✓ Conectado a {port_sel}")
            print("Leyendo datos (Ctrl+C para detener)...\n")
            print("="*60)
            while True:
                if ser.in_waiting:
                    try:
                        line = ser.readline().decode('utf-8', errors='replace').strip()
                        if not line or not line.startswith('{'):
                            continue
                        
                        data_sensor = json.loads(line)
                        data_sensor['timestamp'] = datetime.now().isoformat()
                        buffer_sensors.append(data_sensor)
                        
                        # Mostrar en consola
                        # counter += 1
                        # print(f"[{counter}] {datetime.now().strftime('%H:%M:%S')}")
                        # for key, value in data_sensor.items():
                        #     if key != 'timestamp':
                        #         print(f"  {key}: {value}")
                        # print("-" * 60)
                        
                    except json.JSONDecodeError as e:
                        print(f"⚠ Error al parsear JSON: {e}")
                        print(f"  Línea recibida: {line}")
                    except Exception as e:
                        print(f"⚠ Error inesperado: {e}")
                        
    except serial.SerialException as e:
        print(f"✗ Error al abrir el puerto: {e}")
    except KeyboardInterrupt:
        print("\n\n✓ Lectura detenida por el usuario.")
        #print(f"Total de registros guardados: {counter}")

def read_from_serial_loop(buffer_sensors, port_sel, stop_event):
    try:
        with serial.Serial(port_sel, 9600, timeout=0.5) as ser:
            print(f"✓ Lector serial iniciado en thread background\n")
            
            while not stop_event.is_set():
                try:
                    if ser.in_waiting:
                        line = ser.readline().decode('utf-8', errors='replace').strip()
                        
                        if not line or not line.startswith('{'):
                            continue
                        
                        data_sensor = json.loads(line)
                        data_sensor['timestamp'] = datetime.now().isoformat()
                        buffer_sensors.append(data_sensor)
                        
                    else:
                        # No hay datos, esperar brevemente (permite detención limpia)
                        stop_event.wait(0.05)
                
                except Exception as e:
                    print(f"⚠ Error procesando dato: {e}")
                    continue
    
    except serial.SerialException as e:
        print(f"✗ Error puerto serial: {e}")

def start_serial_thread(buffer_sensors, port_sel):
    stop_event = threading.Event()
    
    thread = threading.Thread(
        target=read_from_serial_loop,
        args=(buffer_sensors, port_sel, stop_event),
        daemon=True
    )
    
    thread.start()
    
    return stop_event, thread
        
        