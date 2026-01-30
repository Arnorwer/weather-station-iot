// ============================================
// Estación Meteorológica UMA - Código Unificado
// Sensores: DHT11, BMP280, MH-RD
// ============================================

// Librerías
#include <DHT.h>
#include <DHT_U.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <ArduinoJson.h>

// ============================================
// CONFIGURACIÓN DE SENSORES
// ============================================

// Sensor BMP280
Adafruit_BMP280 bmp;

// Sensor DHT11
const int DHT_PIN = 2;
DHT ht(DHT_PIN, DHT11);

// Sensor MH-RD (Lluvia)
const int MHRD_PIN = A0;
const int MHRD_VCC_PIN = 4;

// Presión de referencia para la altitud
float P0;

// ============================================
// CONFIGURACIÓN DE TIEMPO
// ============================================

// Intervalo de muestreo:  10 minutos
const unsigned long MEASURE_INTERVAL_MS = 10UL * 60UL * 1000UL;
const unsigned long MHRD_STABILIZE_MS = 50UL;

// Control de tiempo
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

// Acumuladores de tiempo (en milisegundos)
unsigned long totalTimeRaining = 0;
unsigned long timeLightRain = 0;
unsigned long timeModerateRain = 0;
unsigned long timeStorm = 0;

// Umbrales del sensor de lluvia
const int DRY_THRESHOLD = 800;
const int LIGHT_THRESHOLD = 400;
const int MODERATE_THRESHOLD = 200;

// ============================================
// PROTOTIPOS DE FUNCIONES
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
  
    // Configurar pin de alimentación del sensor de lluvia
    pinMode(MHRD_VCC_PIN, OUTPUT);
    digitalWrite(MHRD_VCC_PIN, LOW);
    
    // Inicializar DHT11
    ht.begin();
    
    // Inicializar BMP280
    if (! bmp.begin()) {
        Serial.println("{\"error\": \"BMP280 no encontrado\"}");
        while (1) {
            // Detener si el BMP280 falla
        }
    }
    P0 = bmp.readPressure()/100;
    // Primera muestra inmediata al arrancar
    delay(1000);
    startTimeStatus = millis();
    measureAndPrint();
    lastMeasureMs = millis();
}

// ============================================
// LOOP
// ============================================

void loop() {
    unsigned long now = millis();
    
    // Verificar si es momento de tomar una nueva muestra
    if ((now - lastMeasureMs) >= MEASURE_INTERVAL_MS) {
        lastMeasureMs = now;
        measureAndPrint();
    }
        // Sin delay:  el micro queda libre para otras tareas
}

// ============================================
// FUNCIÓN PRINCIPAL DE MUESTREO
// ============================================

void measureAndPrint() {
    // Crear documento JSON con tamaño aumentado para temporizadores
    StaticJsonDocument<512> sensors_doc;

    // ========================================
    // LECTURA BMP280 (Temperatura y Presión)
    // ========================================
    float bmp_temp = bmp.readTemperature();
    float bmp_pres = bmp.readPressure() / 100.0f; // Convertir a hPa
    float bmp_alt = bmp.readAltitude(P0);

    // ========================================
    // LECTURA DHT11 (Temperatura y Humedad)
    // ========================================
    float dht_temp = ht. readTemperature();
    float dht_hum = ht.readHumidity();

    // ========================================
    // LECTURA MH-RD (Sensor de Lluvia)
    // ========================================
    // Alimentar el sensor momentáneamente
    digitalWrite(MHRD_VCC_PIN, HIGH);
    delay(MHRD_STABILIZE_MS);
    int mhrd_value = analogRead(MHRD_PIN);
    digitalWrite(MHRD_VCC_PIN, LOW);

    // Determinar estado de lluvia
    RainState newState = determineRainStatus(mhrd_value);
    String rain_state;
    
    switch (newState) {
        case SECO: 
            rain_state = "Seco";
            break;
        case LLUVIA_LIGERA:
            rain_state = "Lluvia Ligera";
            break;
        case LLUVIA_MODERADA:
            rain_state = "Lluvia Moderada";
            break;
        case TORMENTA: 
            rain_state = "Tormenta";
            break;
    }

    // Actualizar temporizadores si cambió el estado
    updateTimers(newState);

    // ========================================
    // CONSTRUCCIÓN DEL JSON
    // ========================================
    
    // Datos de sensores
    sensors_doc["temp_bmp"] = bmp_temp;
    sensors_doc["presion"] = bmp_pres;
    sensors_doc["altitud"] = bmp_alt;
    sensors_doc["temp_dht"] = dht_temp;
    sensors_doc["humedad"] = dht_hum;
    sensors_doc["lluvia_valor"] = mhrd_value;
    sensors_doc["lluvia_estado"] = rain_state;
    
    // Temporizadores de lluvia (milisegundos)
    /*sensors_doc["tiempo_total_lluvia_ms"] = totalTimeRaining;
    sensors_doc["tiempo_lluvia_ligera_ms"] = timeLightRain;
    sensors_doc["tiempo_lluvia_moderada_ms"] = timeModerateRain;
    sensors_doc["tiempo_tormenta_ms"] = timeStorm;*/
    
    // Temporizadores en formato legible (HH:MM:SS)
    sensors_doc["tiempo_total_lluvia"] = milisAHMS(totalTimeRaining);
    sensors_doc["tiempo_lluvia_ligera"] = milisAHMS(timeLightRain);
    sensors_doc["tiempo_lluvia_moderada"] = milisAHMS(timeModerateRain);
    sensors_doc["tiempo_tormenta"] = milisAHMS(timeStorm);

    // Serializar y enviar por Serial
    serializeJson(sensors_doc, Serial);
    Serial.println();
}

// ============================================
// FUNCIONES AUXILIARES
// ============================================

RainState determineRainStatus(int sensorValue) {
    if (sensorValue >= DRY_THRESHOLD) {
        return SECO;
    } else if (sensorValue >= LIGHT_THRESHOLD) {
        return LLUVIA_LIGERA;
    } else if (sensorValue >= MODERATE_THRESHOLD) {
        return LLUVIA_MODERADA;
    } else {
        return TORMENTA;
    }
}

void updateTimers(RainState newState) {
    unsigned long now = millis();
    unsigned long durationState = now - startTimeStatus;
    
    // Acumular el tiempo según el estado previo
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
            // No se acumula tiempo cuando está seco
            break;
    }
    
    // Actualizar estados
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
