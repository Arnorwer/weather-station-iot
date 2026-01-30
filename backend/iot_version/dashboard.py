import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec

# Configuración de estilo visual
plt.style.use('fivethirtyeight')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['toolbar'] = 'None'

class RealtimeDashboard:
    def __init__(self, buffer_sensors):
        self.buffer = buffer_sensors
        
        # Configuración de la ventana
        self.fig = plt.figure(figsize=(16, 9), facecolor='#f0f2f6')
        self.fig.canvas.manager.set_window_title('Estación Meteorológica UMA - Monitor Tiempo Real')
        
        # Grid Layout (3 filas)
        gs = gridspec.GridSpec(3, 3, figure=self.fig, height_ratios=[1, 0.4, 1], hspace=0.4, wspace=0.3)
        
        # Fila 1: Sensores Principales
        self.ax_temp = self.fig.add_subplot(gs[0, 0])
        self.ax_hum = self.fig.add_subplot(gs[0, 1])
        self.ax_pres = self.fig.add_subplot(gs[0, 2])
        
        # Fila 2: Indicadores (KPIs)
        self.ax_rain_status = self.fig.add_subplot(gs[1, 0])
        self.ax_alt = self.fig.add_subplot(gs[1, 1])
        self.ax_rain_level = self.fig.add_subplot(gs[1, 2])
        
        # Fila 3: Histórico
        self.ax_bottom = self.fig.add_subplot(gs[2, :])
        
        self.max_points = 50
        
        # Configurar ejes inicialmente
        self.setup_axes()
        
        # Animación (cada 1s)
        self.anim = FuncAnimation(self.fig, self.update, interval=1000, cache_frame_data=False)

    def setup_axes(self):
        """Configura títulos y colores de las gráficas"""
        configs = [
            (self.ax_temp, "Temperatura (BMP280)", '#ff6b6b'),
            (self.ax_hum, "Humedad (DHT11)", '#4ecdc4'),
            (self.ax_pres, "Presión Atmosférica", '#45b7d1')
        ]
        
        for ax, title, color in configs:
            ax.set_title(title, fontsize=12, fontweight='bold', color='#333333')
            ax.tick_params(axis='both', labelsize=8)
            ax.set_facecolor('white')
            # Guardamos color para reusarlo en update
            ax.metric_color = color

        # Limpiar paneles de texto para que no muestren ejes
        for ax in [self.ax_rain_status, self.ax_alt, self.ax_rain_level]:
            ax.set_axis_off()
            ax.set_facecolor('#f0f2f6')

        self.ax_bottom.set_title("Sensor Lluvia (Analógico - Menos es más lluvia)", fontsize=12, fontweight='bold')
        self.ax_bottom.set_facecolor('white')

    def update_kpi_panel(self, ax, title, value_text, subtext, icon, color='black'):
        """Dibuja tarjeta de datos"""
        ax.clear()
        ax.set_axis_off()
        ax.text(0.05, 0.85, title, transform=ax.transAxes, fontsize=10, color='gray')
        ax.text(0.5, 0.5, value_text, transform=ax.transAxes, fontsize=20, fontweight='bold', color=color, ha='center', va='center')
        ax.text(0.1, 0.5, icon, transform=ax.transAxes, fontsize=24, ha='center', va='center')
        ax.text(0.5, 0.2, subtext, transform=ax.transAxes, fontsize=9, color='gray', ha='center')

    def update(self, frame):
        # 1. Obtener datos del buffer
        snapshot = self.buffer.snapshot()
        if not snapshot:
            return

        # 2. Tomar solo los últimos N puntos
        data = snapshot[-self.max_points:]
        
        # 3. Procesar datos en listas
        times = []
        temps = []
        hums = []
        press = []
        rain_vals = []
        rain_digs = []
        alts = []
        
        for reading in data:
            # Timestamp corto (HH:MM:SS)
            ts = reading.get('timestamp', '')
            try:
                # Intenta cortar solo la hora de formato ISO
                t_str = ts.split('T')[1][:8] if 'T' in ts else ts[-8:]
                times.append(t_str)
            except:
                times.append("")

            # Extracción segura de valores (default a 0 o valor anterior)
            temps.append(float(reading.get('temp_bmp', 0)))
            hums.append(float(reading.get('humedad', 0)))
            press.append(float(reading.get('presion', 0)))
            rain_vals.append(float(reading.get('lluvia_valor', 1024)))
            
            # Manejo robusto de llovia_estado (soporta "Seco"/"Mojado" o 0/1)
            raw_rain = reading.get('lluvia_estado', 1)
            try:
                if isinstance(raw_rain, str):
                    # Si contiene "seco", es 1 (no lluvia). Sino 0 (lluvia)
                    rain_val = 1 if "seco" in raw_rain.lower() else 0
                else:
                    rain_val = int(raw_rain)
            except:
                rain_val = 1 # Default seguro
            rain_digs.append(rain_val)

            alts.append(float(reading.get('altitud', 0)))
        
        x_indices = range(len(times))
        
        # --- DIBUJAR GRÁFICAS ---
        
        # Temperatura
        self.ax_temp.clear()
        self.ax_temp.set_title("Temperatura (BMP280)", fontsize=12, fontweight='bold')
        self.ax_temp.plot(x_indices, temps, color='#ff6b6b', lw=2)
        self.ax_temp.fill_between(x_indices, temps, alpha=0.2, color='#ff6b6b')
        if temps: self.ax_temp.text(0.02, 0.9, f"{temps[-1]:.1f}°C", transform=self.ax_temp.transAxes, fontweight='bold')
        
        # Humedad
        self.ax_hum.clear()
        self.ax_hum.set_title("Humedad (DHT11)", fontsize=12, fontweight='bold')
        self.ax_hum.plot(x_indices, hums, color='#4ecdc4', lw=2)
        if hums: self.ax_hum.text(0.02, 0.9, f"{hums[-1]:.1f}%", transform=self.ax_hum.transAxes, fontweight='bold')
        
        # Presión
        self.ax_pres.clear()
        self.ax_pres.set_title("Presión (BMP280)", fontsize=12, fontweight='bold')
        self.ax_pres.plot(x_indices, press, color='#45b7d1', lw=2)
        if press: self.ax_pres.text(0.02, 0.9, f"{press[-1]:.0f} hPa", transform=self.ax_pres.transAxes, fontweight='bold')

        # --- DIBUJAR KPIs ---
        
        # Lluvia Digital (0=Mojado usualmente en sensores activos a bajo)
        if rain_digs:
            # Asumimos logica: 0=Lloviendo, 1=Seco (ajustar si es al revés)
            is_raining = (rain_digs[-1] == 0)
            status_text = "LLOVIENDO" if is_raining else "SECO"
            if rain_vals and rain_vals[-1] < 800: # Doble chequeo con analógico por seguridad visual
                 status_text = "LLOVIENDO" if is_raining or rain_vals[-1] < 600 else "SECO"
            
            icon = "ON" if "LLOVIENDO" in status_text else "OFF"
            col = '#e74c3c' if "LLOVIENDO" in status_text else '#2ecc71'
            self.update_kpi_panel(self.ax_rain_status, "ESTADO LLUVIA", status_text, "Digital Status", icon, col)

        # Altitud
        if alts:
            self.update_kpi_panel(self.ax_alt, "ALTITUD", f"{alts[-1]:.1f}m", "Nivel del Mar", "Alt", '#34495e')

        # Lluvia Analógica
        if rain_vals:
            r_val = rain_vals[-1]
            # Interpretación típica MH-RD: <300 Tormenta, <600 Lluvia, >900 Seco
            msg = "Seco"
            if r_val < 300: msg = "Tormenta!!"
            elif r_val < 600: msg = "Lluvia Fuerte"
            elif r_val < 850: msg = "Llovizna"
            
            self.update_kpi_panel(self.ax_rain_level, "INTENSIDAD LLUVIA", f"{r_val:.0f}", msg, "Rain", '#3498db')

        # --- DIBUJAR HISTÓRICO ---
        self.ax_bottom.clear()
        self.ax_bottom.set_title("Sensor Lluvia (Analógico) - Tiempo Real", fontsize=12)
        self.ax_bottom.plot(x_indices, rain_vals, color='#8e44ad', lw=2)
        self.ax_bottom.grid(True, alpha=0.3)
        # Etiquetas eje X (reducidas)
        if len(times) > 0:
            step = max(1, len(times)//8)
            self.ax_bottom.set_xticks(x_indices[::step])
            self.ax_bottom.set_xticklabels(times[::step], rotation=0, fontsize=8)

    def run(self):
        plt.tight_layout()
        plt.show()
