"""
Receptor HTTP - API REST para recibir datos del Arduino
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime
from threading import Thread

class HTTPReceiver(BaseHTTPRequestHandler):
    """Manejador de peticiones HTTP del Arduino"""
    
    buffer = None  # Se asignará desde afuera
    arduino_connected = False
    
    def do_GET(self):
        """Maneja peticiones GET para diagnóstico"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        html = f"""
        <html>
            <body style='font-family: sans-serif; text-align: center; padding-top: 50px;'>
                <h1 style='color: #2e7d32;'>✅ Servidor Operativo</h1>
                <p>La Estación Meteorológica UMA está lista para recibir datos.</p>
                <p><b>IP Actual:</b> {self.headers.get('Host')}</p>
                <p><b>Endpoint:</b> /sensors/post_data (POST)</p>
            </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        """Maneja peticiones POST del Arduino"""
        if self.path == '/sensors/post_data':
            try:
                # Leer tamaño del body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Parsear JSON
                data = json.loads(post_data.decode('utf-8'))
                
                # Agregar timestamp
                data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Guardar en buffer
                HTTPReceiver.buffer.append(data)
                HTTPReceiver.arduino_connected = True
                
                # Responder OK
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error":"invalid json"}')
            except Exception as e:
                print(f"✗ Error: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Silenciar logs HTTP por defecto"""
        pass


class HTTPReceiverServer:
    """Servidor HTTP para recibir datos del Arduino"""
    
    def __init__(self, buffer, host="0.0.0.0", port=8000):
        self.buffer = buffer
        self.host = host
        self.port = port
        self.running = False
        HTTPReceiver.buffer = buffer
        
    @property
    def arduino_connected(self):
        return HTTPReceiver.arduino_connected
    
    def start_server(self):
        """Inicia servidor HTTP"""
        print("="*60)
        print("🌐 Servidor HTTP - Estación Meteorológica UMA")
        print("="*60)
        print(f"Escuchando: http://{self.host}:{self.port}")
        print(f"Endpoint: POST /sensors/post_data")
        print(f"Buffer: {self.buffer.capacity} mediciones")
        print("="*60 + "\n")
        print("⏳ Esperando datos del Arduino...\n")
        
        self.running = True
        server = HTTPServer((self.host, self.port), HTTPReceiver)
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    
    def stop(self):
        self.running = False


def start_http_receiver_thread(buffer, host="0.0.0.0", port=8000):
    """
    Inicia servidor HTTP en thread separado
    """
    receiver = HTTPReceiverServer(buffer, host, port)
    
    def run():
        try:
            receiver.start_server()
        except Exception as e:
            print(f"✗ Error en servidor HTTP: {e}")
    
    thread = Thread(target=run, daemon=True)
    thread.start()
    
    return receiver