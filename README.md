# Estación Meteorológica (EMMD) - weather-station-iot

Proyecto: Estación meteorológica con microcontroladores y dashboard interactivo.

Integrantes:
- Esteban Avila (Líder)
- Moises Araujo
- Luis de Faria

Descripción breve:
Repositorio base con la estructura simplificada para que el equipo comience a desarrollar: firmware (Arduino), backend (FastAPI + SQLite) y frontend (HTML/CSS/JS).

Estructura principal:
- firmware/: Código para el Arduino (lectura de sensores y envío por serial).
- backend/: Servidor Python (FastAPI), lector serial y manejo de SQLite.
- frontend/: Dashboard web sencillo que consume la API.
- docs/: Documentación básica y plan semanal.

Cómo usar (resumen rápido):
1. Instalar dependencias Python: pip install -r requirements.txt
2. Iniciar backend: uvicorn backend.server:app --reload
3. Ejecutar el lector serial (si Arduino conectado): python backend/serial_reader.py
4. Abrir frontend/index.html en el navegador o servirlo con un servidor estático.

Licencia: MIT (se puede añadir LICENSE si se desea)