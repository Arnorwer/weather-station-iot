import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
import matplotlib.dates as mdates

class RealtimePlotter:
    def __init__(self, buffer_sensors, metrica, nombre_metrica, stats_iniciales, intervalo=500):
        self.buffer = buffer_sensors
        self.metrica = metrica
        self.nombre = nombre_metrica
        self.intervalo = intervalo
        self.stats_iniciales = stats_iniciales
        
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.fig.suptitle(f'Monitor en Tiempo Real - {nombre_metrica}', fontsize=14, fontweight='bold')
        
        self.line, = self.ax.plot([], [], lw=2, color='blue', marker='o', markersize=4)
        
        # ← EJE X: Tiempo (timestamps)
        self.ax.set_xlabel('Tiempo', fontsize=11)
        # ← EJE Y: Valor de la métrica
        self.ax.set_ylabel(f'{nombre_metrica}', fontsize=11)
        self.ax.grid(True, alpha=0.3)
        
        # Formato para el eje X (mostrar hora:minuto:segundo)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.fig.autofmt_xdate(rotation=45)
        
        self.anim = FuncAnimation(
            self.fig,
            self.update,
            interval=intervalo,
            blit=True,
            cache_frame_data=False
        )
    
    def update(self, frame):
        """
        Se ejecuta cada 500ms.
        Extrae datos de stats y los grafica con tiempo en eje X.
        """
        snapshot_actual = self.buffer.snapshot()
        
        from metrics_processor import interactive_output
        stats_nuevos = interactive_output(snapshot_actual, self.metrica, self.nombre)
        
        if len(stats_nuevos) == 0:
            return self.line,
        
        # ← CREAR DATOS PARA GRAFICAR CON TIEMPO
        # Eje X: timestamps convertidos a datetime
        tiempos = []
        for stat in stats_nuevos:
            try:
                # Convertir string de timestamp a datetime
                dt = datetime.fromisoformat(stat["instante"])
                tiempos.append(dt)
            except (ValueError, TypeError):
                tiempos.append(datetime.now())
        
        # Eje Y: valores de la métrica
        valores_y = []
        for stat in stats_nuevos:
            try:
                valor = stat["metrica"]
                if isinstance(valor, str):
                    valor = float(valor)
                valores_y.append(valor)
            except (ValueError, TypeError, KeyError):
                valores_y.append(0)
        
        # ← ACTUALIZAR LÍNEA CON TIEMPO EN AXIS X
        # x_data = [datetime(...), datetime(...), ...]  (tiempos)
        # y_data = [23.5, 23.6, 23.7, ...]  (valores)
        self.line.set_data(tiempos, valores_y)
        
        # Ajustar límites automáticamente
        if tiempos:
            self.ax.set_xlim(tiempos[0], tiempos[-1])
        
        if valores_y:
            y_min = min(valores_y) * 0.95
            y_max = max(valores_y) * 1.05
            margen = (y_max - y_min) * 0.1 if y_max != y_min else 1
            self.ax.set_ylim(y_min - margen, y_max + margen)
        
        self.ax.set_title(
            f'{self.nombre} | Mediciones: {len(valores_y)} | Actualizado: {datetime.now().strftime("%H:%M:%S")}',
            fontsize=10,
            color='gray'
        )
        
        return self.line,
    
    def show(self):
        plt.tight_layout()
        plt.show()


def plot_metric(buffer_sensors, metrica, nombre_metrica, stats):
    """
    Abre gráfica en tiempo real.
    
    Eje X: Timestamp (hora:minuto:segundo)
    Eje Y: Valor de la métrica
    
    Estructura de stats:
    [
        {"metrica": 23.5, "instante": "2026-01-16T14:30:45.123456"},
        {"metrica": 23.6, "instante": "2026-01-16T14:30:46.234567"},
        ...
    ]
    """
    print(f"\nAbriendo gráfica de {nombre_metrica}...")
    print("(Eje X: Tiempo | Eje Y: {nombre_metrica})")
    print("(Actualiza cada 500ms)\n")
    
    plotter = RealtimePlotter(buffer_sensors, metrica, nombre_metrica, stats)
    plotter.show()