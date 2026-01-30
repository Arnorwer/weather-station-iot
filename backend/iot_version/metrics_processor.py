"""
Procesamiento de métricas del buffer circular
Adaptado de _outputdemo.py para versión IoT
"""
from graph_monitor import plot_metric

def interactive_output(snapshot, sensor_key, sensor_name):
    """
    Procesa un snapshot del buffer y retorna métricas formateadas
    """
    result = []
    
    for reading in snapshot:
        if sensor_key in reading:
            result.append({
                "metrica": reading[sensor_key],
                "instante": reading.get("timestamp", "N/A")
            })
    
    return result


def show_metrics_menu(buffer, snapshot):
    """
    Muestra menú interactivo de métricas disponibles
    
    Args:
        buffer: Instancia de RingBuffer
        snapshot: Snapshot actual del buffer
    """
    if not snapshot:
        print("\n✗ Buffer vacío. No hay datos para mostrar.\n")
        return
    
    # Detectar métricas disponibles
    available_metrics = list(snapshot[0].keys())
    
    # Definir nombres legibles
    metric_names = {
        "temp_bmp": "Temperatura BMP280",
        "temp_dht": "Temperatura DHT11",
        "humedad": "Humedad Relativa",
        "presion": "Presión Atmosférica",
        "altitud": "Altitud",
        "lluvia_valor": "Sensor Lluvia (raw)",
        "lluvia_estado": "Estado de Lluvia",
        "tiempo_total_lluvia": "Tiempo Total Lloviendo",
        "tiempo_lluvia_ligera": "Tiempo Lluvia Ligera",
        "tiempo_lluvia_moderada": "Tiempo Lluvia Moderada",
        "tiempo_tormenta": "Tiempo en Tormenta"
    }
    
    print("\n" + "="*60)
    print("📊 MÉTRICAS DISPONIBLES")
    print("="*60)
    
    # Filtrar métricas relevantes (excluir timestamp, etc.)
    metrics_to_show = [m for m in available_metrics if m not in ['timestamp', 'received_at']]
    
    for idx, metric_key in enumerate(metrics_to_show, 1):
        metric_name = metric_names.get(metric_key, metric_key.replace("_", " ").title())
        print(f"  {idx}. {metric_name}")
    
    print(f"\n  0. Volver al menú principal")
    print("="*60)
    
    try:
        choice = int(input("\nSelecciona métrica (número): ").strip())
        
        if choice == 0:
            return
        
        if 1 <= choice <= len(metrics_to_show):
            selected_key = metrics_to_show[choice - 1]
            selected_name = metric_names.get(selected_key, selected_key)
            
            print(f"\n→ Procesando: {selected_name}...")
            
            # Procesar datos
            metrics_data = interactive_output(
                snapshot, 
                selected_key, 
                selected_name
            )
            
            # Mostrar resultados
            print("\n" + "="*60)
            print(f"📈 {selected_name.upper()}")
            print("="*60)
            print(f"Total de lecturas: {len(metrics_data)}")
            print(f"Capacidad buffer: {buffer.capacity}")
            print("-"*60)
            
            plot_metric(buffer, selected_key, selected_name, metrics_data)
        else:
            print("✗ Opción inválida")
            
    except ValueError:
        print("✗ Entrada inválida")
    except Exception as e:
        print(f"✗ Error: {e}")