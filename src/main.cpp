/*#include <Arduino.h>

#include <Arduino.h>


// Definicje pinów
const int TRIG_PIN = 9;
const int ECHO_PIN = 10;

// Zmienne
long duration;
float distance;
const int breaktime=1500;
unsigned long starttime=0;

void setup() {
  // Inicjalizacja portów szeregowych
  Serial.begin(9600);
  
  // Konfiguracja pinów
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  Serial.println("Czujnik HC-SR04 - pomiar odległości");
}

void loop() {
  // Czyszczenie pinu TRIG
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  // Wysłanie impulsu 10µs
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Odczyt czasu trwania echa
  duration = pulseIn(ECHO_PIN, HIGH);
  
  // Obliczenie odległości w cm
  // Prędkość dźwięku = 343 m/s = 0.0343 cm/µs
  // Odległość = (czas * prędkość) / 2
  unsigned long nowTime=millis();
  if(nowTime-starttime>=breaktime){
    distance = (duration * 0.0343) / 2;
  
  // Wyświetlenie wyniku
 
  if(distance<4.0 || distance>400.0)
  {
    distance=0;
  }
   Serial.print("Odległość: ");
  Serial.print(distance);
  Serial.println(" cm");
  Serial.println("---------");
  Serial.println(starttime);
  Serial.println(nowTime);
  starttime=nowTime;



  
  }
  
  
 
}*/

#include <Arduino.h>

// ============================================================================
// DEFINICJE PINÓW - CZUJNIKI ULTRADŹWIĘKOWE
// ============================================================================
const int TRIG_LEWY = 8;
const int ECHO_LEWY = 9;

const int TRIG_SRODEK = 6;
const int ECHO_SRODEK = 7;

const int TRIG_PRAWY = 4;
const int ECHO_PRAWY = 5;

// ============================================================================
// DEFINICJE PINÓW - SILNIKI (bez PWM, tylko HIGH/LOW)
// ============================================================================

const int M1A = 10;   // lewy silnik
const int M1B = 11;
 const int M2A = 12;   // prawy silnik
const int M2B = 13;

// ============================================================================
// STAŁE SYSTEMU
// ============================================================================
const int POMIAR_INTERVAL = 100;  // Pomiar co 100ms
const int WYSWIETL_INTERVAL = 500; 
unsigned long lastMeasurement = 0;
unsigned long lastDisplay = 0; 

const float MAX_DISTANCE = 400.0; // Maksymalna odległość czujnika (cm)

// ============================================================================
// ZMIENNE GLOBALNE - ODLEGŁOŚCI
// ============================================================================
float odleglosc_lewy = 0;
float odleglosc_srodek = 0;
float odleglosc_prawy = 0;

// ============================================================================
// FUNKCJE POMOCNICZE - POMIAR ODLEGŁOŚCI
// ============================================================================

float zmierzOdleglosc(int trigPin, int echoPin) {
  // Wyślij impuls
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Odczytaj czas echa (timeout 30ms = ~500cm)
  long duration = pulseIn(echoPin, HIGH, 30000);
  
  if (duration == 0) {
    return MAX_DISTANCE; // Brak sygnału = daleko
  }
  
  // Oblicz odległość w cm
  float distance = (duration * 0.0343) / 2.0;
  
  // Filtruj błędne odczyty
  if (distance < 2.0 || distance > MAX_DISTANCE) {
    return MAX_DISTANCE;
  }
  
  return distance;
}

// ============================================================================
// LOGIKA ROZMYTA TSK - FUNKCJE PRZYNALEŻNOŚCI
// ============================================================================

float przynaleznoscTrapez(float wartosc, float a, float b, float c, float d) {
  /*
   * Funkcja trapezoidalna [a, b, c, d]
   * a, b: wzrost od 0 do 1
   * c, d: spadek od 1 do 0
   */
  if (wartosc <= a) return 0.0;
  if (wartosc <= b) return (wartosc - a) / (b - a);
  if (wartosc <= c) return 1.0;
  if (wartosc <= d) return (d - wartosc) / (d - c);
  return 0.0;
}

// Zbiory rozmyte dla każdego czujnika
struct ZbioryRozmyte {
  float przeszkoda;  // Przynależność do "przeszkoda"
  float wolne;       // Przynależność do "wolne"
};


ZbioryRozmyte obliczPrzynaleznosci(float odleglosc) {
  ZbioryRozmyte z;
  
  // PRZESZKODA: od 0 do 40cm
  z.przeszkoda = przynaleznoscTrapez(odleglosc, -5, 0, 30, 40);
  
  // WOLNE: od 30cm do MAX_DISTANCE (400cm)
  z.wolne = przynaleznoscTrapez(odleglosc, 30, 40, 400, 450);
  
  return z;
}

// ============================================================================
// LOGIKA ROZMYTA TSK - FUNKCJE WYJŚCIOWE
// ============================================================================

float kierunek_stop(float lewy, float srodek, float prawy) {
  return -2.0;
}

float kierunek_lewo(float lewy, float srodek, float prawy) {
  return -1.0;
}

float kierunek_prosto(float lewy, float srodek, float prawy) {
  return 0.0;
}

float kierunek_prawo(float lewy, float srodek, float prawy) {
  return 1.0;
}

// ============================================================================
// LOGIKA ROZMYTA TSK - WNIOSKOWANIE
// ============================================================================

float wnioskowanieTSK(float lewy, float srodek, float prawy) {
  // Oblicz przynależności
  ZbioryRozmyte z_lewy = obliczPrzynaleznosci(lewy);
  ZbioryRozmyte z_srodek = obliczPrzynaleznosci(srodek);
  ZbioryRozmyte z_prawy = obliczPrzynaleznosci(prawy);
  
  // ========================================================================
  // MOCE ODPALENIA REGUŁ (wi = min)
  // ========================================================================
  
  // R1: wolne × wolne × wolne → PROSTO
  float w1 = min(min(z_lewy.wolne, z_srodek.wolne), z_prawy.wolne);
  
  // R2: przeszkoda × wolne × wolne → PRAWO
  float w2 = min(min(z_lewy.przeszkoda, z_srodek.wolne), z_prawy.wolne);
  
  // R3: wolne × wolne × przeszkoda → LEWO
  float w3 = min(min(z_lewy.wolne, z_srodek.wolne), z_prawy.przeszkoda);
  
  // R4: przeszkoda × wolne × przeszkoda → PROSTO
  float w4 = min(min(z_lewy.przeszkoda, z_srodek.wolne), z_prawy.przeszkoda);
  
  // R5: wolne × przeszkoda × wolne → STOP
  float w5 = min(min(z_lewy.wolne, z_srodek.przeszkoda), z_prawy.wolne);
  
  // R6: przeszkoda × przeszkoda × wolne → PRAWO
  float w6 = min(min(z_lewy.przeszkoda, z_srodek.przeszkoda), z_prawy.wolne);
  
  // R7: wolne × przeszkoda × przeszkoda → LEWO
  float w7 = min(min(z_lewy.wolne, z_srodek.przeszkoda), z_prawy.przeszkoda);
  
  // R8: przeszkoda × przeszkoda × przeszkoda → STOP
  float w8 = min(min(z_lewy.przeszkoda, z_srodek.przeszkoda), z_prawy.przeszkoda);
  
  // ========================================================================
  // WYJŚCIA FUNKCJI (zi)
  // ========================================================================
  
  float z1 = kierunek_prosto(lewy, srodek, prawy);
  float z2 = kierunek_prawo(lewy, srodek, prawy);
  float z3 = kierunek_lewo(lewy, srodek, prawy);
  float z4 = kierunek_prosto(lewy, srodek, prawy);
  float z5 = kierunek_stop(lewy, srodek, prawy);
  float z6 = kierunek_prawo(lewy, srodek, prawy);
  float z7 = kierunek_lewo(lewy, srodek, prawy);
  float z8 = kierunek_stop(lewy, srodek, prawy);
  
  // ========================================================================
  // ŚREDNIA WAŻONA (wzór TSK)
  // ========================================================================
  
  float licznik = w1*z1 + w2*z2 + w3*z3 + w4*z4 + w5*z5 + w6*z6 + w7*z7 + w8*z8;
  float mianownik = w1 + w2 + w3 + w4 + w5 + w6 + w7 + w8;
  
  if (mianownik > 0.0001) {
    return licznik / mianownik;
  } else {
    return 0.0; // Domyślnie PROSTO gdy żadna reguła się nie odpaliła
  }
}

// ============================================================================
// STEROWANIE SILNIKAMI (PROSTE: HIGH/LOW)
// ============================================================================

void sterujSilnikami(float kierunek) {
  /*
   * kierunek:
   *   -2.0 = STOP        → Lewy: LOW,  Prawy: LOW
   *   -1.0 = LEWO        → Lewy: HIGH, Prawy: LOW
   *    0.0 = PROSTO      → Lewy: HIGH, Prawy: HIGH
   *   +1.0 = PRAWO       → Lewy: LOW,  Prawy: HIGH
   */
  
  if (kierunek < -1.5) {
    // ========== STOP ==========
    Serial.println("🛑 ");
    digitalWrite(M1A, LOW);
    digitalWrite(M1B, LOW);
    digitalWrite(M2A, LOW);
    digitalWrite(M2B,LOW);

    /*wersja z */

    
    
  } else if (kierunek < -0.5) {
    // ========== LEWO ==========
    Serial.println("⬅️ ");
    digitalWrite(M1A, LOW);
    digitalWrite(M1B, LOW);
    digitalWrite(M2A, HIGH);
    digitalWrite(M2B, LOW);

    
  } else if (kierunek < 0.5) {
    // ========== PROSTO ==========
    Serial.println("⬆️ ");
    digitalWrite(M1A, HIGH);
    digitalWrite(M1B, LOW);
    digitalWrite(M2A, HIGH);
    digitalWrite(M2B, LOW);

    
  } else {
    // ========== PRAWO ==========
    Serial.println("➡️ ");
    digitalWrite(M1A, HIGH);
    digitalWrite(M1B, LOW);
    digitalWrite(M2A, LOW);
    digitalWrite(M2B, LOW);

  }
}

// ============================================================================
// WYŚWIETLANIE SZCZEGÓŁOWYCH OBLICZEŃ (OPCJONALNE)
// ============================================================================

void wyswietlSzczegoly(float lewy, float srodek, float prawy, float kierunek) {
  Serial.println("\n========================================");
  Serial.println("SZCZEGÓŁY OBLICZEŃ TSK");
  Serial.println("========================================");
  
  // Przynależności
  ZbioryRozmyte z_lewy = obliczPrzynaleznosci(lewy);
  ZbioryRozmyte z_srodek = obliczPrzynaleznosci(srodek);
  ZbioryRozmyte z_prawy = obliczPrzynaleznosci(prawy);
  
  Serial.print("Lewy (");
  Serial.print(lewy, 1);
  Serial.print(" cm): przeszkoda=");
  Serial.print(z_lewy.przeszkoda, 2);
  Serial.print(", wolne=");
  Serial.println(z_lewy.wolne, 2);
  
  Serial.print("Środek (");
  Serial.print(srodek, 1);
  Serial.print(" cm): przeszkoda=");
  Serial.print(z_srodek.przeszkoda, 2);
  Serial.print(", wolne=");
  Serial.println(z_srodek.wolne, 2);
  
  Serial.print("Prawy (");
  Serial.print(prawy, 1);
  Serial.print(" cm): przeszkoda=");
  Serial.print(z_prawy.przeszkoda, 2);
  Serial.print(", wolne=");
  Serial.println(z_prawy.wolne, 2);
  
  Serial.print("\nKierunek TSK: ");
  Serial.println(kierunek, 2);
  
  Serial.println("========================================");
}

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  Serial.begin(9600);
  
  // Konfiguracja czujników ultradźwiękowych
  pinMode(TRIG_LEWY, OUTPUT);
  pinMode(ECHO_LEWY, INPUT);
  pinMode(TRIG_SRODEK, OUTPUT);
  pinMode(ECHO_SRODEK, INPUT);
  pinMode(TRIG_PRAWY, OUTPUT);
  pinMode(ECHO_PRAWY, INPUT);
  
  // Konfiguracja silników
  pinMode(M1A, OUTPUT);
  pinMode(M1B, OUTPUT);
  pinMode(M2A, OUTPUT);
  pinMode(M2B, OUTPUT);
  
  // Zatrzymaj silniki na starcie
  digitalWrite(M1A, LOW);
  digitalWrite(M1B, LOW);
   digitalWrite(M2A, LOW);
  digitalWrite(M2B, LOW);
  
  Serial.println("========================================");
  Serial.println("  ROBOT Z LOGIKĄ ROZMYTĄ TSK");
  Serial.println("========================================");
  Serial.println("Uruchamianie systemu...\n");
  
  delay(2000); // Pauza przed startem
}

// ============================================================================
// LOOP
// ============================================================================

void loop() {
  unsigned long currentTime = millis();

  // Pomiar co POMIAR_INTERVAL ms
  if (currentTime - lastMeasurement >= POMIAR_INTERVAL) {
    lastMeasurement = currentTime;
    
    // ========================================================================
    // KROK 1: POMIAR ODLEGŁOŚCI
    // ========================================================================
    
    odleglosc_lewy = zmierzOdleglosc(TRIG_LEWY, ECHO_LEWY);
    odleglosc_srodek = zmierzOdleglosc(TRIG_SRODEK, ECHO_SRODEK);
    odleglosc_prawy = zmierzOdleglosc(TRIG_PRAWY, ECHO_PRAWY);
    
    // ========================================================================
    // KROK 2: WNIOSKOWANIE TSK
    // ========================================================================
    
    float kierunek = wnioskowanieTSK(odleglosc_lewy, odleglosc_srodek, odleglosc_prawy);
    
   
    // ========================================================================
    // KROK 3: WYŚWIETL DANE (UPROSZCZONE)
    // ========================================================================
  
    
    
    // Opcjonalnie: wyświetl szczegóły (odkomentuj jeśli chcesz)
    // wyswietlSzczegoly(odleglosc_lewy, odleglosc_srodek, odleglosc_prawy, kierunek);
    
    // ========================================================================
    // KROK 4: STEROWANIE SILNIKAMI
    // ========================================================================
    
    sterujSilnikami(kierunek);
    
    Serial.println("========================================");
  }


  // WYŚWIETLANIE (co 500ms - niezależnie)
  if (currentTime - lastDisplay >= WYSWIETL_INTERVAL) {
    lastDisplay = currentTime;
    
    Serial.println("\n========================================");
    Serial.print("L: ");
    Serial.print(odleglosc_lewy, 1);
    Serial.print(" cm | S: ");
    Serial.print(odleglosc_srodek, 1);
    Serial.print(" cm | P: ");
    Serial.print(odleglosc_prawy, 1);
    
    // Oblicz kierunek tylko do wyświetlenia
    float kierunek_display = wnioskowanieTSK(odleglosc_lewy, odleglosc_srodek, odleglosc_prawy);
    Serial.print(" cm | K: ");
    Serial.println(kierunek_display, 2);
    Serial.println("========================================");
  }
}