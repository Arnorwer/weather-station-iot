/*En base a la medicion del sensor devuelva un mensaje que indique la fuerza de la lluvia y que
en base a la cantidad de veces que detecte la misma, calcule la cantidad de veces que ha llovido"""*/
//Calculo_del_tiempo_que_estuvo_lloviendo
//Gemini_y_chatGPT
//Libreria_sensor_De_lluvia

//CAlculo de tiempo
unsigned long TiempoInicial = 0;
unsigned long acumuladoA = 0, acumuladoB = 0, acumuladoC = 0;
unsigned long TiempoFinal = 0;
bool rain = false;

//Umbrales de cada tipo
const int umbralseco = 900; //Ambiente seco
const int umbrallow = 700; //Lluvia ligera
const int umbralhard = 300; // Lluvia intensa

//Cambios de estado
int actualstg = 0; //0: Seco, 1: ligera, 2: moderada, 3: fuerte
int latestg = 0;

void setup() { 
Serial.begin(9600); //9600ms, takvez se cambie por 100.000, con tal de hacerlo en "tiempo real", sin ebargo 9600, sigue siendo buen medida
TiempoInicial = millis();
}

void loop() { 
int value = AnalogRead(A3); 
Serial.print("Value : ")
Serial.printIn(value); 

void Reporte() {
  tiempoTotalLluvia = acumuladoA + acumuladoB + acumuladoC + acumuladoD;
  
  Serial.println("\n======= RESUMEN DE LLUVIA =======");
  Serial.print("Tiempo Total: "); Serial.print(TiempoInicial / 1000); Serial.println(" seg");
  Serial.print("Lluvia ligera: "); Serial.print(acumuladoA / 1000); Serial.println(" seg");
  Serial.print("Lluvia moderada):   "); Serial.print(acumuladoB / 1000); Serial.println(" seg");
  Serial.print("Lluvia fuerte: "); Serial.print(acumuladoC / 1000); Serial.println(" seg");
  Serial.println("=================================\n");
}

if (rain = true) {
  TiempoInicial = millis()
 }
if (value >= umbralseco){
Serial.print ("Ambiente Seco")
actualstg = 0
}

if (value >= umbralsoft && value < umbralseco){ // mas como una humedad, o llovisna
Serial.print ("Lluvia lígera")
actualstg = 1
}

if (value >= umbralhard && value < umbrallow){ // este rango va desde ligero  moderada
Serial.print ("Lluvia moderada")
actualstg = 2
}

if (value = 0 && value < umbralhard){
Serial.print ("Lluvia Intensa ") //"tormenta" o "lluvia fuerte"
actualstg = 3
}

//Deteccion de cambio de estado
if (actualstg != latestg) {
  unsigned long duración = millis() - TiempoInicial
  //Suma de tiempos acumulados
  if (latestg == 1) acumuladoA += duracion;
  else if (latestg == 2) acumuladoB += duracion;
  else if (latestg == 3) acumuladoC += duración;

  //Si paso de lluvia y ahora esta seco, se muestar el resumen
  if (latestg != 0 and actualstg == 0){
    Reporte();
    acumuladoA = 0, acumuladoB = 0, acumuladoC = 0;
  }
  
  //reinicio de tiempo y registro de anterior estado
  TiempoInicial = millis()
  latestg = actualstg
}

delay(100);


}