import serial
import serial.tools.list_ports

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

def main():
    port_sel = seleccionar_puerto()
    if not port_sel:
        return
    try:
        with serial.Serial(port_sel, 9600, timeout=1) as ser:
            print(f"Conectado a {port_sel} a 9600 baud.")
            print("Leyendo datos (Ctrl+C para salir)...")
            while True:
                if ser.in_waiting:
                    serialData = ser.readline()
                    print(serialData.decode('utf-8', errors='replace').rstrip())
    except serial.SerialException as e:
        print(f"Error al abrir el puerto: {e}")

if __name__ == "__main__":
    main()