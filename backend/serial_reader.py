import serial
import serial.tools.list_ports
import json
import csv
from datetime import datetime
import os

def seleccionar_puerto():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No se encontraron puertos seriales disponibles.")
        return None
    print("Puertos disponibles:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port.device} - {port.description}")
    while True:
        seleccion = input("Selecciona el número del puerto: ").strip()
        if seleccion.isdigit():
            idx = int(seleccion) - 1
            if 0 <= idx < len(ports):
                return ports[idx].device
        print("Selección inválida. Intenta de nuevo.")

def seleccionar_formato():
    print("\n¿En qué formato deseas guardar los datos?")
    print("  1. JSON")
    print("  2. CSV")
    print("  3. Ambos")
    while True:
        opcion = input("Selecciona (1/2/3): ").strip()
        if opcion in ['1', '2', '3']:
            return opcion
        print("Opción inválida. Intenta de nuevo.")

def guardar_json(data, archivo='data/sensor_data.json'):
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            try:
                registros = json.load(f)
            except json.JSONDecodeError:
                registros = []
    else:
        registros = []
    
    registros.append(data)
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(registros, f, indent=2, ensure_ascii=False)

def guardar_csv(data, archivo='data/sensor_data.csv'):
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    existe = os.path.exists(archivo)
    with open(archivo, 'a', newline='', encoding='utf-8') as f:
        campos = ['timestamp'] + [k for k in data.keys() if k != 'timestamp']
        writer = csv.DictWriter(f, fieldnames=campos)
        if not existe:
            writer.writeheader()
        
        writer.writerow(data)

def main():
    port_sel = seleccionar_puerto()
    if not port_sel:
        return
    
    formato = seleccionar_formato()
    print(f"\nConectando a {port_sel}...")
    
    try:
        with serial.Serial(port_sel, 9600, timeout=1) as ser:
            print(f"✓ Conectado a {port_sel}")
            print("Leyendo datos (Ctrl+C para detener)...\n")
            print("="*60)
            
            contador = 0
            while True:
                if ser.in_waiting:
                    try:
                        line = ser.readline().decode('utf-8', errors='replace').strip()
                        if not line or not line.startswith('{'):
                            continue
                        
                        datos_sensor = json.loads(line)
                        datos_sensor['timestamp'] = datetime.now().isoformat()
                        
                        # Mostrar en consola
                        contador += 1
                        print(f"[{contador}] {datetime.now().strftime('%H:%M:%S')}")
                        for key, value in datos_sensor.items():
                            if key != 'timestamp':
                                print(f"  {key}: {value}")
                        print("-" * 60)
                        
                        if formato in ['1', '3']:
                            guardar_json(datos_sensor)
                        if formato in ['2', '3']:
                            guardar_csv(datos_sensor)
                        
                    except json.JSONDecodeError as e:
                        print(f"⚠ Error al parsear JSON: {e}")
                        print(f"  Línea recibida: {line}")
                    except Exception as e:
                        print(f"⚠ Error inesperado: {e}")
                        
    except serial.SerialException as e:
        print(f"✗ Error al abrir el puerto: {e}")
    except KeyboardInterrupt:
        print("\n\n✓ Lectura detenida por el usuario.")
        print(f"Total de registros guardados: {contador}")

if __name__ == "__main__":
    main()