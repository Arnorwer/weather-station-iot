#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>


Adafruit_BMP280 bmp;

float TEMPERATURA;
float PRESION, P0;

void setup() {
    Serial.begin (9600);
    Serial.println ("Iniciando:");
    if ( !bmp.begin ()  )   {
    Serial.println ("Bmp280 no encontrado !");
    while (1); 
}
P0 = bmp.readPressure()/100;
}

void loop() {
    TEMPERATURA = bmp.readTemperature();
    PRESION = bmp.readPressure()/100;

    Serial.print ("Temperatura: ") ;
    Serial.print (TEMPERATURA) ;
    Serial.print (" C ") ;

    Serial.print ("Presion: ") ;
    Serial.print (PRESION) ;
    Serial.println (" hPa ") ;
    
    Serial.print ("Altitud aprox: ") ;
    Serial.print (bmp.readAltitude(P0)) ;
    Serial.println (" m ") ;
    delay(5000)

}
