"""
Main IoT Version - HTTP REST API
CAMBIO: WebSocket → HTTP POST
"""
import time
import socket
from ring_buffer import RingBuffer
from websocket_receiver import start_http_receiver_thread
from metrics_processor import show_metrics_menu
from backend.iot_version.dashboard import RealtimeDashboard

HTTP_PORT = 8000  # Puerto HTTP

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def main():
    print("\n" + "="*60)
    print("🌤️  ESTACIÓN METEOROLÓGICA UMA - VERSIÓN IoT")
    print("="*60)
    
    # Buffer
    buffer_size = 1440
    cambiar = input(f"¿Cambiar buffer? ({buffer_size}) [s/N]: ").lower()
    if cambiar == 's':
        try:
            buffer_size = int(input("Capacidad: "))
        except:
            buffer_size = 1440
    
    buffer_sensors = RingBuffer(capacity=buffer_size)
    print(f"✓ Buffer: {buffer_size}\n")
    
    # Mostrar IP para configurar Arduino
    ip = get_local_ip()
    print(f"💡 Configura Arduino con:")
    print(f"   server_host = \"{ip}\"")
    print(f"   server_port = {HTTP_PORT}\n")
    
    # Iniciar servidor HTTP
    receiver = start_http_receiver_thread(buffer_sensors, "0.0.0.0", HTTP_PORT)
    time.sleep(1)
    
    # Preguntar modo de operación
    print("\n" + "="*60)
    print("📈 MODO DE VISUALIZACIÓN")
    print("  1. Dashboard Gráfico (Ventana)")
    print("  2. Consola de Texto")
    print("="*60)
    mode = input("Selecciona opción [1/2]: ").strip()
    
    if mode == '1':
        print("\nAbriendo Dashboard... (Cierra la ventana para salir)")
        dashboard = RealtimeDashboard(buffer_sensors)
        # El servidor HTTP sigue corriendo en background gracias a start_http_receiver_thread
        try:
            dashboard.run() # Bloquea aquí hasta cerrar ventana
        except KeyboardInterrupt:
            pass
        finally:
            receiver.stop()
            print("✓ Sistema cerrado")
            return # Salir del programa

    # Menú Consola (Modo original)
    print("⌨️  COMANDOS")
    print("="*60)
    print("  v → Ver métricas")
    print("  s → Estado")
    print("  c → Limpiar")
    print("  q → Salir")
    print("="*60 + "\n")
    
    try:
        while True:
            cmd = input("Comando: ").strip().lower()
            
            if cmd == 'v':
                snapshot = buffer_sensors.snapshot()
                show_metrics_menu(buffer_sensors, snapshot)
            
            elif cmd == 's':
                print(f"\nBuffer: {buffer_sensors.length()}/{buffer_sensors.capacity}")
                print(f"Arduino: {'✓' if receiver.arduino_connected else '✗'}\n")
            
            elif cmd == 'c':
                if input("¿Limpiar? [s/N]: ").lower() == 's':
                    buffer_sensors.clear()
                    print("✓ Limpiado\n")
            
            elif cmd == 'q':
                break
    
    except KeyboardInterrupt:
        print("\n✓ Interrumpido")
    
    finally:
        receiver.stop()
        print("✓ Sistema cerrado\n")

if __name__ == "__main__":
    main()