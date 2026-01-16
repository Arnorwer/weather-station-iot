from serial_reader import read_from_serial, port_selector, start_serial_thread
from ring_buffer import RingBuffer
from _outputdemo import show_metrics_menu

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
    buffer_sensors = RingBuffer(capacity=buffer_size)

    # Seleccionar y conectar al puerto serial
    port_sel = port_selector()
    if not port_sel:
        return
    
    print("\n" + "="*60)
    stop_event, thread = start_serial_thread(buffer_sensors, port_sel)
    print("="*60)
    print("Comandos disponibles:")
    print("  'v' + Enter → Ver métricas acumuladas")
    print("  'q' + Enter → Salir")
    print("="*60 + "\n")

    try:
        while True:
            cmd = input("Ingresa comando (v/q): ").strip().lower()
            
            if cmd == 'v':
                # ← Obtener snapshot (thread-safe)
                sensors_snapshot = buffer_sensors.snapshot()
                
                # ← Delegar menú a _outputdemo
                show_metrics_menu(buffer_sensors, sensors_snapshot)

            elif cmd == 'q':
                print("\n✓ Saliendo...")
                break
            
            else:
                print("✗ Comando no válido.\n")

    except KeyboardInterrupt:
        print("\n\n✓ Interrumpido por usuario.")
    
    finally:
        # Limpieza: detener thread
        print("Deteniendo lector serial...")
        stop_event.set()
        thread.join(timeout=2)
        print("✓ Programa finalizado.")

if __name__ == "__main__":
    main()
