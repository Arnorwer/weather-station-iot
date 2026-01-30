// ============================================
// Estación Meteorológica UMA - Versión IoT
// ============================================

// Librerías
#include <DHT.h>
#include <DHT_U.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <ArduinoJson.h>
#include <WiFiS3.h>

// ============================================
// CONFIGURACIÓN WiFi + HTTP
// ============================================
const char* ssid = "NombreRedWiFi";
const char* password = "ClaveRedWiFi";

// Servidor HTTP (tu PC con Python)
const char* server_host = "ServidorIP";
const uint16_t server_port = 8000;
const char* api_endpoint = "/sensors/post_data";

WiFiClient client;

// ============================================
// CONFIGURACIÓN DE SENSORES
// ============================================

Adafruit_BMP280 bmp;
const int DHT_PIN = 2;
DHT ht(DHT_PIN, DHT11);
const int MHRD_PIN = A0;
const int MHRD_VCC_PIN = 4;
float P0;

// ============================================
// CONFIGURACIÓN DE TIEMPO
// ============================================

const unsigned long MEASURE_INTERVAL_MS = 1000UL;
const unsigned long MHRD_STABILIZE_MS = 50UL;
unsigned long lastMeasureMs = 0;

// ============================================
// TEMPORIZADORES DE LLUVIA
// ============================================

enum RainState {
    SECO,
    LLUVIA_LIGERA,
    LLUVIA_MODERADA,
    TORMENTA
};

RainState currentState = SECO;
RainState previousState = SECO;
unsigned long startTimeStatus = 0;
unsigned long totalTimeRaining = 0;
unsigned long timeLightRain = 0;
unsigned long timeModerateRain = 0;
unsigned long timeStorm = 0;

const int DRY_THRESHOLD = 800;
const int LIGHT_THRESHOLD = 400;
const int MODERATE_THRESHOLD = 200;

// ============================================
// PROTOTIPOS
// ============================================

void measureAndPrint();
void updateTimers(RainState newState);
String milisAHMS(unsigned long ms);
RainState determineRainStatus(int sensorValue);

// ============================================
// SETUP
// ============================================

void setup() {
    Serial.begin(9600);
    delay(2000);
    
    Serial.println("=== Estación Meteorológica UMA - IoT ===");
    
    // Configurar sensores
    pinMode(MHRD_VCC_PIN, OUTPUT);
    digitalWrite(MHRD_VCC_PIN, LOW);
    ht.begin();
    
    if (!bmp.begin(0x76)) {
        Serial.println("{\"error\": \"BMP280 no encontrado\"}");
        while (1);
    }
    P0 = bmp.readPressure()/100;
    Serial.println("✓ Sensores inicializados");
    
    // ========================================
    // Conectar WiFi con espera de IP
    // ========================================
    Serial.print("Conectando WiFi: ");
    Serial.println(ssid);
    
    // Desconectar primero (por si acaso)
    WiFi.disconnect();
    delay(100);
    
    WiFi.begin(ssid, password);
    
    // Esperar conexión WiFi
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 40) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("\n✗ Error WiFi - no se pudo conectar");
        Serial.println("Reiniciando en 5 segundos...");
        delay(5000);
        setup();
        return;
    }
    
    Serial.println("\n✓ WiFi conectado");
    
    Esperar a obtener IP válida
    Serial.print("Obteniendo IP");
    attempts = 0;
    while (WiFi.localIP() == IPAddress(0, 0, 0, 0) && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    IPAddress ip = WiFi.localIP();
    if (ip == IPAddress(0, 0, 0, 0)) {
        Serial.println("\n✗ No se obtuvo IP - reiniciando...");
        delay(3000);
        setup();
        return;
    }
    
    Serial.println();
    Serial.print("IP Arduino: ");
    Serial.println(ip);
    Serial.print("Gateway: ");
    Serial.println(WiFi.gatewayIP());
    Serial.print("Servidor: http://");
    Serial.print(server_host);
    Serial.print(":");
    Serial.println(server_port);
    
    // Verificar conectividad básica
    Serial.print("Verificando conectividad con servidor... ");
    if (client.connect(server_host, server_port)) {
        Serial.println("✓ OK");
        client.stop();
    } else {
        Serial.println("✗ No se puede alcanzar el servidor");
        Serial.println("Verifica que Python esté ejecutándose y el firewall");
    }
    
    // Primera muestra
    delay(1000);
    startTimeStatus = millis();
    measureAndPrint();
    lastMeasureMs = millis();
}

// ============================================
// LOOP
// ============================================

void loop() {
    // Verificar WiFi
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("✗ WiFi desconectado - reconectando...");
        WiFi.begin(ssid, password);
        delay(5000);
        return;
    }
    
    unsigned long now = millis();
    if ((now - lastMeasureMs) >= MEASURE_INTERVAL_MS) {
        lastMeasureMs = now;
        measureAndPrint();
    }
}

// ============================================
// FUNCIÓN PRINCIPAL
// ============================================

void measureAndPrint() {
    StaticJsonDocument<512> sensors_doc;

    // ========================================
    // LECTURA SENSORES
    // ========================================
    float bmp_temp = bmp.readTemperature();
    float bmp_pres = bmp.readPressure() / 100.0f;
    float bmp_alt = bmp.readAltitude(P0);
    float dht_temp = ht.readTemperature();
    float dht_hum = ht.readHumidity();
    
    digitalWrite(MHRD_VCC_PIN, HIGH);
    delay(MHRD_STABILIZE_MS);
    int mhrd_value = analogRead(MHRD_PIN);
    digitalWrite(MHRD_VCC_PIN, LOW);

    RainState newState = determineRainStatus(mhrd_value);
    String rain_state;
    
    switch (newState) {
        case SECO: rain_state = "Seco"; break;
        case LLUVIA_LIGERA: rain_state = "Lluvia Ligera"; break;
        case LLUVIA_MODERADA: rain_state = "Lluvia Moderada"; break;
        case TORMENTA: rain_state = "Tormenta"; break;
    }

    updateTimers(newState);

    // ========================================
    // JSON
    // ========================================
    sensors_doc["temp_bmp"] = bmp_temp;
    sensors_doc["presion"] = bmp_pres;
    sensors_doc["altitud"] = bmp_alt;
    sensors_doc["temp_dht"] = dht_temp;
    sensors_doc["humedad"] = dht_hum;
    sensors_doc["lluvia_valor"] = mhrd_value;
    sensors_doc["lluvia_estado"] = rain_state;
    sensors_doc["tiempo_total_lluvia"] = milisAHMS(totalTimeRaining);
    sensors_doc["tiempo_lluvia_ligera"] = milisAHMS(timeLightRain);
    sensors_doc["tiempo_lluvia_moderada"] = milisAHMS(timeModerateRain);
    sensors_doc["tiempo_tormenta"] = milisAHMS(timeStorm);

    String json;
    serializeJson(sensors_doc, json);
    
    // Enviar por HTTP POST
    Serial.print("→ Enviando HTTP POST... ");
    
    if (WiFi.status() == WL_CONNECTED) {
        if (client.connect(server_host, server_port)) {
            // Construir petición HTTP POST
            client.print("POST ");
            client.print(api_endpoint);
            client.println(" HTTP/1.1");
            
            client.print("Host: ");
            client.println(server_host);
            
            client.println("Content-Type: application/json");
            client.println("Connection: close");
            
            client.print("Content-Length: ");
            client.println(json.length());
            
            client.println();  // Línea vacía antes del body
            client.println(json);
            
            // Esperar respuesta
            unsigned long timeout = millis();
            while (client.available() == 0 && (millis() - timeout < 5000));
            
            // Leer respuesta
            bool success = false;
            while (client.available()) {
                String line = client.readStringUntil('\n');
                if (line.indexOf("200 OK") >= 0 || line.indexOf("201") >= 0) {
                    success = true;
                }
            }
            
            client.stop();
            Serial.println(success ? "✓ OK" : "✗ Error servidor");
            
        } else {
            Serial.println("✗ No se pudo conectar");
        }
    } else {
        Serial.println("✗ WiFi no conectado");
    }
}

// ============================================
// FUNCIONES AUXILIARES
// ============================================

RainState determineRainStatus(int sensorValue) {
    if (sensorValue >= DRY_THRESHOLD) return SECO;
    else if (sensorValue >= LIGHT_THRESHOLD) return LLUVIA_LIGERA;
    else if (sensorValue >= MODERATE_THRESHOLD) return LLUVIA_MODERADA;
    else return TORMENTA;
}

void updateTimers(RainState newState) {
    unsigned long now = millis();
    unsigned long durationState = now - startTimeStatus;
    
    switch (previousState) {
        case LLUVIA_LIGERA:
            timeLightRain += durationState;
            totalTimeRaining += durationState;
            break;
        case LLUVIA_MODERADA:
            timeModerateRain += durationState;
            totalTimeRaining += durationState;
            break;
        case TORMENTA:
            timeStorm += durationState;
            totalTimeRaining += durationState;
            break;
        case SECO:
            break;
    }
    
    previousState = currentState;
    currentState = newState;
    startTimeStatus = now;
}

String milisAHMS(unsigned long ms) {
    unsigned long seconds = ms / 1000;
    unsigned long minutes = seconds / 60;
    unsigned long hours = minutes / 60;
    
    seconds = seconds % 60;
    minutes = minutes % 60;
    
    String result = "";
    if (hours < 10) result += "0";
    result += String(hours) + ":";
    if (minutes < 10) result += "0";
    result += String(minutes) + ":";
    if (seconds < 10) result += "0";
    result += String(seconds);
    
    return result;
}