### Archivo crado apra probar la extraccion de datos en un campo controlado

sensors = [
  {
    "temp_bmp": 29.79,
    "presion": 914.8347,
    "altitud": -0.060339,
    "temp_dht": 29.3,
    "humedad": 72,
    "lluvia_valor": 994,
    "lluvia_estado": "Seco",
    "tiempo_total_lluvia": "00:00:00",
    "tiempo_lluvia_ligera": "00:00:00",
    "tiempo_lluvia_moderada": "00:00:00",
    "tiempo_tormenta": "00:00:00",
    "timestamp": "2026-01-13T15:40:00.995017"
  },
  {
    "temp_bmp": 29.81,
    "presion": 914.7922,
    "altitud": -0.153863,
    "temp_dht": 29.4,
    "humedad": 71,
    "lluvia_valor": 993,
    "lluvia_estado": "Seco",
    "tiempo_total_lluvia": "00:00:00",
    "tiempo_lluvia_ligera": "00:00:00",
    "tiempo_lluvia_moderada": "00:00:00",
    "tiempo_tormenta": "00:00:00",
    "timestamp": "2026-01-13T15:40:51.701456"
  },
  {
    "temp_bmp": 29.83,
    "presion": 914.7806,
    "altitud": 0.133752,
    "temp_dht": 29.5,
    "humedad": 71,
    "lluvia_valor": 993,
    "lluvia_estado": "Seco",
    "tiempo_total_lluvia": "00:00:00",
    "tiempo_lluvia_ligera": "00:00:00",
    "tiempo_lluvia_moderada": "00:00:00",
    "tiempo_tormenta": "00:00:00",
    "timestamp": "2026-01-13T15:40:54.853507"
  },
  {
    "temp_bmp": 30.13,
    "presion": 914.7913,
    "altitud": -0.373089,
    "temp_dht": 29.9,
    "humedad": 70,
    "lluvia_valor": 993,
    "lluvia_estado": "Seco",
    "tiempo_total_lluvia": "00:00:00",
    "tiempo_lluvia_ligera": "00:00:00",
    "tiempo_lluvia_moderada": "00:00:00",
    "tiempo_tormenta": "00:00:00",
    "timestamp": "2026-01-13T16:34:10.547096"
  },
  {
    "temp_bmp": 30.13,
    "presion": 914.7808,
    "altitud": -0.277556,
    "temp_dht": 29.9,
    "humedad": 70,
    "lluvia_valor": 993,
    "lluvia_estado": "Seco",
    "tiempo_total_lluvia": "00:00:00",
    "tiempo_lluvia_ligera": "00:00:00",
    "tiempo_lluvia_moderada": "00:00:00",
    "tiempo_tormenta": "00:00:00",
    "timestamp": "2026-01-13T16:34:12.896898"
  }
]

#read_from_serials(buffer_sensors, port_sel)

#sensors = buffer_sensors.snapshot() 

def interactive_output(sensors, met, name):
    stats = []
    for m in sensors:
        data = {
            "metrica": m[met], 
            "instante": m["timestamp"]
        }
        stats.append(data)
    
    print(f"--LISTA METRICA-TIMESTAMP--\n") 
    for n in stats:
        print(f"{name}: {n['metrica']}, Tiempo: {n['instante']}")

interacción = input("""---METRICAS DISPONIBLES--- \n\n 
                        [1] Temperatura 
                        [2] Humedad
                        [3] Presion
                        [4] Altitud
                        [5] Estado actual de la lluvia
                        [6] Tiempo total de lluvia
                        ¿Cual es la métrica que desea ver?: """).strip()

match interacción:
    case "1":
        metrica = "temp_bmp"
        name = "Temperatura"
    case "2":
        metrica = "humedad"  
        name = "Humedad"      
    case "3":
        metrica = "presion"   
        name = "Presión"      
    case "4":
        metrica = "altitud"   
        name = "Altitud"      
    case "5":
        metrica = "lluvia_estado" 
        name = "Estado actual de la lluvia"        
    case "6":
        metrica = "tiempo_total_lluvia"     
        name = "Tiempo total de lluvia"    
    case _:
        metrica = None
        print("Comando no reconocido.")

if metrica:
    interactive_output (sensors, metrica, name)


