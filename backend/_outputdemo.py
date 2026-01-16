### Archivo crado apra probar la extraccion de datos en un campo controlado

#read_from_serials(buffer_sensors, port_sel)

#sensors = buffer_sensors.snapshot() 
def interactive_output(sensors, met, name, buffer_capacity=None):
    stats = []
    for m in sensors:
        data = {
            "metrica": m[met], 
            "instante": m["timestamp"]
        }
        stats.append(data)
    
    if buffer_capacity and len(stats) > buffer_capacity:
        stats = stats[-buffer_capacity:]
    
    print(f"\n--LISTA {name.upper()}--\n") 
    for n in stats:
        print(f"{name}: {n['metrica']}, Tiempo: {n['instante']}")
    print()
    
    return stats


def show_metrics_menu(buffer_sensors, sensors_snapshot):
    if not sensors_snapshot:
        print("⚠ Buffer vacío. Espera a que lleguen datos.\n")
        return

    print("\n" + "="*60)
    print("---MÉTRICAS DISPONIBLES---")
    print("="*60)
    print("  [1] Temperatura (temp_bmp)")
    print("  [2] Humedad (humedad)")
    print("  [3] Presión (presion)")
    print("  [4] Altitud (altitud)")
    print("  [5] Temperatura (temp_dht)")
    print("  [6] Estado lluvia (lluvia_estado)")
    print("  [7] Tiempo total lluvia (tiempo_total_lluvia)")
    print("="*60)
    
    interaccion = input("Selecciona métrica (1-7): ").strip()
    # Mapeo: opción → (clave_dict, nombre_legible)
    metricas = {
        "1": ("temp_bmp", "Temperatura"),
        "2": ("humedad", "Humedad"),
        "3": ("presion", "Presión"),
        "4": ("altitud", "Altitud"),
        "5": ("temp_dht", "Temperatura DHT"),
        "6": ("lluvia_estado", "Estado lluvia"),
        "7": ("tiempo_total_lluvia", "Tiempo total lluvia"),
    }

    if interaccion in metricas:
        metrica, nombre = metricas[interaccion]
        interactive_output(sensors_snapshot, metrica, nombre, buffer_capacity=buffer_sensors._capacity)
    else:
        print("✗ Opción inválida.\n")


