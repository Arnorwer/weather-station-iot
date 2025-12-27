import serial
import serial.tools.list_ports
import json
import csv
from datetime import datetime
import os
from ring_buffer import RingBuffer

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

def format_selector():
    print("\n¿En qué formato deseas guardar los datos?")
    print("  1. JSON")
    print("  2. CSV")
    print("  3. Ambos")
    while True:
        option = input("Selecciona (1/2/3): ").strip()
        if option in ['1', '2', '3']:
            return option
        print("Opción inválida. Intenta de nuevo.")

def json_save(data, file='data/sensor_data.json'):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            try:
                records = json.load(f)
            except json.JSONDecodeError:
                records = []
    else:
        records = []
    
    records.append(data)
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
def csv_save(data, file='data/sensor_data.csv'):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    existe = os.path.exists(file)
    with open(file, 'a', newline='', encoding='utf-8') as f:
        fields = ['timestamp'] + [k for k in data.keys() if k != 'timestamp']
        writer = csv.DictWriter(f, fieldnames=fields)
        if not existe:
            writer.writeheader()
        
        writer.writerow(data)

def main():
    buffer_size = input("Ingrese el tamaño del buffer circular (número de lecturas a mantener en memoria): ").strip()
    try:
        buffer_size = int(buffer_size)
        if buffer_size <= 0:
            raise ValueError
    except ValueError:
        print("Tamaño de bufer invalido. Ingrese un número entero positivo.")
        return
    
    buffer_sensors = RingBuffer(capacity=buffer_size)
    
    port_sel = port_selector()
    if not port_sel:
        return
    
    formato = format_selector()
    print(f"\nConectando a {port_sel}...")
    
    try:
        with serial.Serial(port_sel, 9600, timeout=1) as ser:
            print(f"✓ Conectado a {port_sel}")
            print("Leyendo datos (Ctrl+C para detener)...\n")
            print("="*60)
            
            counter = 0
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
                        counter += 1
                        print(f"[{counter}] {datetime.now().strftime('%H:%M:%S')}")
                        for key, value in data_sensor.items():
                            if key != 'timestamp':
                                print(f"  {key}: {value}")
                        print("-" * 60)
                        
                        if formato in ['1', '3']:
                            json_save(data_sensor)
                        if formato in ['2', '3']:
                            csv_save(data_sensor)
                        
                    except json.JSONDecodeError as e:
                        print(f"⚠ Error al parsear JSON: {e}")
                        print(f"  Línea recibida: {line}")
                    except Exception as e:
                        print(f"⚠ Error inesperado: {e}")
                        
    except serial.SerialException as e:
        print(f"✗ Error al abrir el puerto: {e}")
    except KeyboardInterrupt:
        print("\n\n✓ Lectura detenida por el usuario.")
        print(f"Total de registros guardados: {counter}")

if __name__ == "__main__":
    main()