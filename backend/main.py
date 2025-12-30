from serial_reader import read_from_serial, port_selector, format_selector
from ring_buffer import TwoDayStore

def main():
    print("=== Lector de Datos del Sensor Meteorológico ===\n")

    # Configurar la capacidad del buffer
    buffer = input("Indique si desea cambiar la capacidad del buffer circular (1440 por defecto) (s/n): ").strip().lower()
    buffer_size = 1440 if buffer != 's' else input("Ingrese la capacidad del buffer circular: ").strip()
    try:
        buffer_size = int(buffer_size)
        if buffer_size <= 0:
            raise ValueError
    except ValueError:
        print("Tamaño de buffer inválido. Ingrese un número entero positivo.")
        return
    
    # Crear instancia del buffer
    buffer_sensors = TwoDayStore(capacity_day=buffer_size)

    # Seleccionar y conectar al puerto serial
    port_sel = port_selector()
    if not port_sel:
        return
    
    # Seleccionar formato de salida
    formato = format_selector()
    
    # Ejecutar el lector serial
    read_from_serial(buffer_sensors, port_sel, formato)

if __name__ == "__main__":
    main()