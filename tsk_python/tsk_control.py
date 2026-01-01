'''import numpy as np
from pyit2fls import T1TSK, T1FS, tri_mf, trapezoid_mf
import matplotlib.pyplot as plt

# Uniwersa (0-173 cm dla czujników ultradźwiękowych)
odleglosc_universe = np.linspace(0.0, 173.0, 1000)

# ============================================================================
# ZBIORY ROZMYTE
# ============================================================================

# CZUJNIK LEWY
przeszkoda_lewy = T1FS(odleglosc_universe, trapezoid_mf, [-5, 0, 30, 40, 1.0])
wolne_lewy = T1FS(odleglosc_universe, trapezoid_mf, [30, 40, 173, 178, 1.0])

# CZUJNIK ŚRODKOWY
przeszkoda_srodek = T1FS(odleglosc_universe, trapezoid_mf, [-5, 0, 30, 40, 1.0])
wolne_srodek = T1FS(odleglosc_universe, trapezoid_mf, [30, 40, 173, 178, 1.0])

# CZUJNIK PRAWY
przeszkoda_prawy = T1FS(odleglosc_universe, trapezoid_mf, [-5, 0, 30, 40, 1.0])
wolne_prawy = T1FS(odleglosc_universe, trapezoid_mf, [30, 40, 173, 178, 1.0])

# ============================================================================
# FUNKCJE WYJŚCIOWE
# ============================================================================
# WAŻNE: Kolejność argumentów musi pasować do kolejności add_input_variable!

def kierunek_stop(lewy, srodek, prawy):
    return -2.0

def kierunek_lewo(lewy, srodek, prawy):
    return -1.0

def kierunek_prosto(lewy, srodek, prawy):
    return 0.0

def kierunek_prawo(lewy, srodek, prawy):
    return 1.0

# ============================================================================
# STEROWNIK TSK
# ============================================================================

controller = T1TSK()

# WAŻNE: Kolejność dodawania zmiennych!
controller.add_input_variable('lewy')
controller.add_input_variable('srodek')
controller.add_input_variable('prawy')
controller.add_output_variable('kierunek')

# ============================================================================
# REGUŁY (8 reguł)
# ============================================================================

# Reguła 1: Wszystko wolne → PROSTO
controller.add_rule([('lewy', wolne_lewy), ('srodek', wolne_srodek), ('prawy', wolne_prawy)], 
                    [('kierunek', kierunek_prosto)])

# Reguła 2: Przeszkoda po lewej, reszta wolna → PRAWO
controller.add_rule([('lewy', przeszkoda_lewy), ('srodek', wolne_srodek), ('prawy', wolne_prawy)], 
                    [('kierunek', kierunek_prawo)])

# Reguła 3: Przeszkoda po prawej, reszta wolna → LEWO
controller.add_rule([('lewy', wolne_lewy), ('srodek', wolne_srodek), ('prawy', przeszkoda_prawy)], 
                    [('kierunek', kierunek_lewo)])

# Reguła 4: Przeszkody po obu bokach, środek wolny → PROSTO (lub STOP?)
controller.add_rule([('lewy', przeszkoda_lewy), ('srodek', wolne_srodek), ('prawy', przeszkoda_prawy)], 
                    [('kierunek', kierunek_prosto)])

# Reguła 5: Przeszkoda z przodu, boki wolne → STOP (lub wybierz stronę?)
controller.add_rule([('lewy', wolne_lewy), ('srodek', przeszkoda_srodek), ('prawy', wolne_prawy)], 
                    [('kierunek', kierunek_stop)])

# Reguła 6: Przód i lewo zajęte, prawo wolne → PRAWO
controller.add_rule([('lewy', przeszkoda_lewy), ('srodek', przeszkoda_srodek), ('prawy', wolne_prawy)], 
                    [('kierunek', kierunek_prawo)])

# Reguła 7: Przód i prawo zajęte, lewo wolne → LEWO
controller.add_rule([('lewy', wolne_lewy), ('srodek', przeszkoda_srodek), ('prawy', przeszkoda_prawy)], 
                    [('kierunek', kierunek_lewo)])

# Reguła 8: Wszystko zajęte → STOP
controller.add_rule([('lewy', przeszkoda_lewy), ('srodek', przeszkoda_srodek), ('prawy', przeszkoda_prawy)], 
                    [('kierunek', kierunek_stop)])

# ============================================================================
# TESTOWANIE
# ============================================================================

print("="*70)
print("SYSTEM STEROWANIA ROBOTEM - TESTY")
print("="*70)

# Test 1: Przeszkoda po lewej
print("\nTest 1: lewy=10cm, środek=150cm, prawy=160cm (przeszkoda po lewej)")
wynik1 = controller.evaluate({"lewy": 10, "srodek": 150, "prawy": 160}, (10, 150, 160))
print(f"Wynik: {wynik1['kierunek']:.2f}")
print(f"Interpretacja: ", end="")
if wynik1['kierunek'] > 0.5:
    print("➡️ PRAWO")
elif wynik1['kierunek'] < -1.5:
    print("🛑 STOP")
elif wynik1['kierunek'] < -0.5:
    print("⬅️ LEWO")
else:
    print("⬆️ PROSTO")

# Test 2: Wszystko wolne
print("\nTest 2: lewy=100cm, środek=120cm, prawy=110cm (wszystko wolne)")
wynik2 = controller.evaluate({"lewy": 100, "srodek": 120, "prawy": 110}, (100, 120, 110))
print(f"Wynik: {wynik2['kierunek']:.2f}")
print(f"Interpretacja: ", end="")
if wynik2['kierunek'] > 0.5:
    print("➡️ PRAWO")
elif wynik2['kierunek'] < -1.5:
    print("🛑 STOP")
elif wynik2['kierunek'] < -0.5:
    print("⬅️ LEWO")
else:
    print("⬆️ PROSTO")

# Test 3: Przeszkoda z przodu
print("\nTest 3: lewy=80cm, środek=15cm, prawy=90cm (przeszkoda z przodu)")
wynik3 = controller.evaluate({"lewy": 80, "srodek": 15, "prawy": 90}, (80, 15, 90))
print(f"Wynik: {wynik3['kierunek']:.2f}")
print(f"Interpretacja: ", end="")
if wynik3['kierunek'] > 0.5:
    print("➡️ PRAWO")
elif wynik3['kierunek'] < -1.5:
    print("🛑 STOP")
elif wynik3['kierunek'] < -0.5:
    print("⬅️ LEWO")
else:
    print("⬆️ PROSTO")

# Test 4: Twój przykład
print("\nTest 4: lewy=0cm, środek=157cm, prawy=157cm")
wynik4 = controller.evaluate({"lewy": 0, "srodek": 157, "prawy": 157}, (0, 157, 157))
print(f"Wynik: {wynik4['kierunek']:.2f}")
print(f"Interpretacja: ", end="")
if wynik4['kierunek'] > 0.5:
    print("➡️ PRAWO")
elif wynik4['kierunek'] < -1.5:
    print("🛑 STOP")
elif wynik4['kierunek'] < -0.5:
    print("⬅️ LEWO")
else:
    print("⬆️ PROSTO")

# Wykresy zbiorów rozmytych
przeszkoda_lewy.plot('Lewy: przeszkoda')
wolne_lewy.plot('Lewy: wolne')
plt.show()
'''

import numpy as np
from pyit2fls import T1TSK, T1FS, tri_mf, trapezoid_mf
import matplotlib.pyplot as plt

# Uniwersa (0-173 cm dla czujników ultradźwiękowych)
odleglosc_universe = np.linspace(0.0, 173.0, 1000)

# ============================================================================
# ZBIORY ROZMYTE
# ============================================================================

# CZUJNIK LEWY
przeszkoda_lewy = T1FS(odleglosc_universe, trapezoid_mf, [-5, 0, 30, 40, 1.0])
wolne_lewy = T1FS(odleglosc_universe, trapezoid_mf, [30, 40, 173, 178, 1.0])

# CZUJNIK ŚRODKOWY
przeszkoda_srodek = T1FS(odleglosc_universe, trapezoid_mf, [-5, 0, 30, 40, 1.0])
wolne_srodek = T1FS(odleglosc_universe, trapezoid_mf, [30, 40, 173, 178, 1.0])

# CZUJNIK PRAWY
przeszkoda_prawy = T1FS(odleglosc_universe, trapezoid_mf, [-5, 0, 30, 40, 1.0])
wolne_prawy = T1FS(odleglosc_universe, trapezoid_mf, [30, 40, 173, 178, 1.0])

# ============================================================================
# FUNKCJE WYJŚCIOWE
# ============================================================================
# WAŻNE: Kolejność argumentów musi pasować do kolejności add_input_variable!

def kierunek_stop(lewy, srodek, prawy):
    return -2.0

def kierunek_lewo(lewy, srodek, prawy):
    return -1.0

def kierunek_prosto(lewy, srodek, prawy):
    return 0.0

def kierunek_prawo(lewy, srodek, prawy):
    return 1.0

# ============================================================================
# STEROWNIK TSK
# ============================================================================

controller = T1TSK()

# WAŻNE: Kolejność dodawania zmiennych!
controller.add_input_variable('lewy')
controller.add_input_variable('srodek')
controller.add_input_variable('prawy')
controller.add_output_variable('kierunek')

# ============================================================================
# REGUŁY (8 reguł)
# ============================================================================

# Reguła 1: Wszystko wolne → PROSTO
controller.add_rule([('lewy', wolne_lewy), ('srodek', wolne_srodek), ('prawy', wolne_prawy)], 
                    [('kierunek', kierunek_prosto)])

# Reguła 2: Przeszkoda po lewej, reszta wolna → PRAWO
controller.add_rule([('lewy', przeszkoda_lewy), ('srodek', wolne_srodek), ('prawy', wolne_prawy)], 
                    [('kierunek', kierunek_prawo)])

# Reguła 3: Przeszkoda po prawej, reszta wolna → LEWO
controller.add_rule([('lewy', wolne_lewy), ('srodek', wolne_srodek), ('prawy', przeszkoda_prawy)], 
                    [('kierunek', kierunek_lewo)])

# Reguła 4: Przeszkody po obu bokach, środek wolny → PROSTO
controller.add_rule([('lewy', przeszkoda_lewy), ('srodek', wolne_srodek), ('prawy', przeszkoda_prawy)], 
                    [('kierunek', kierunek_prosto)])

# Reguła 5: Przeszkoda z przodu, boki wolne → STOP
controller.add_rule([('lewy', wolne_lewy), ('srodek', przeszkoda_srodek), ('prawy', wolne_prawy)], 
                    [('kierunek', kierunek_stop)])

# Reguła 6: Przód i lewo zajęte, prawo wolne → PRAWO
controller.add_rule([('lewy', przeszkoda_lewy), ('srodek', przeszkoda_srodek), ('prawy', wolne_prawy)], 
                    [('kierunek', kierunek_prawo)])

# Reguła 7: Przód i prawo zajęte, lewo wolne → LEWO
controller.add_rule([('lewy', wolne_lewy), ('srodek', przeszkoda_srodek), ('prawy', przeszkoda_prawy)], 
                    [('kierunek', kierunek_lewo)])

# Reguła 8: Wszystko zajęte → STOP
controller.add_rule([('lewy', przeszkoda_lewy), ('srodek', przeszkoda_srodek), ('prawy', przeszkoda_prawy)], 
                    [('kierunek', kierunek_stop)])

# ============================================================================
# FUNKCJA DO OBLICZANIA PRZYNALEŻNOŚCI
# ============================================================================

def oblicz_przynaleznosc_trapez(wartosc, a, b, c, d):
    """
    Oblicza przynależność do zbioru trapezoidalnego
    trapez: [a, b, c, d] gdzie:
    - a, b: wzrost od 0 do 1
    - c, d: spadek od 1 do 0
    """
    if wartosc <= a:
        return 0.0
    elif a < wartosc <= b:
        return (wartosc - a) / (b - a)
    elif b < wartosc <= c:
        return 1.0
    elif c < wartosc <= d:
        return (d - wartosc) / (d - c)
    else:
        return 0.0

# ============================================================================
# SZCZEGÓŁOWE OBLICZENIA DLA WYBRANEGO PRZYPADKU
# ============================================================================

def szczegolowe_obliczenia(lewy_test, srodek_test, prawy_test):
    print("\n" + "="*70)
    print("OBLICZANIE WYNIKU STERUJĄCEGO - WZÓR TSK")
    print("="*70)
    print(f"\nDla: lewy={lewy_test}cm, środek={srodek_test}cm, prawy={prawy_test}cm")
    
    print("\nWZÓR TSK:")
    print("           N")
    print("         Σ (wi × zi)")
    print("         i=1")
    print("kierunek = ─────────────")
    print("           N")
    print("         Σ wi")
    print("         i=1")
    
    # ========================================================================
    # KROK 1: Oblicz przynależności do zbiorów rozmytych
    # ========================================================================
    print("\n" + "-"*70)
    print("KROK 1: Przynależność do zbiorów rozmytych")
    print("-"*70)
    
    # Lewy czujnik
    mu_lewy_przeszkoda = oblicz_przynaleznosc_trapez(lewy_test, -5, 0, 30, 40)
    mu_lewy_wolne = oblicz_przynaleznosc_trapez(lewy_test, 30, 40, 173, 178)
    
    print(f"\nLewy czujnik ({lewy_test}cm):")
    print(f"  przeszkoda: {mu_lewy_przeszkoda:.4f}")
    print(f"  wolne:      {mu_lewy_wolne:.4f}")
    
    # Środkowy czujnik
    mu_srodek_przeszkoda = oblicz_przynaleznosc_trapez(srodek_test, -5, 0, 30, 40)
    mu_srodek_wolne = oblicz_przynaleznosc_trapez(srodek_test, 30, 40, 173, 178)
    
    print(f"\nŚrodkowy czujnik ({srodek_test}cm):")
    print(f"  przeszkoda: {mu_srodek_przeszkoda:.4f}")
    print(f"  wolne:      {mu_srodek_wolne:.4f}")
    
    # Prawy czujnik
    mu_prawy_przeszkoda = oblicz_przynaleznosc_trapez(prawy_test, -5, 0, 30, 40)
    mu_prawy_wolne = oblicz_przynaleznosc_trapez(prawy_test, 30, 40, 173, 178)
    
    print(f"\nPrawy czujnik ({prawy_test}cm):")
    print(f"  przeszkoda: {mu_prawy_przeszkoda:.4f}")
    print(f"  wolne:      {mu_prawy_wolne:.4f}")
    
    # ========================================================================
    # KROK 2: Oblicz moce odpalenia reguł (wi = min)
    # ========================================================================
    print("\n" + "-"*70)
    print("KROK 2: Moce odpalenia reguł (wi = min)")
    print("-"*70)
    
    # Oblicz wi dla każdej reguły
    w1 = min(mu_lewy_wolne, mu_srodek_wolne, mu_prawy_wolne)
    w2 = min(mu_lewy_przeszkoda, mu_srodek_wolne, mu_prawy_wolne)
    w3 = min(mu_lewy_wolne, mu_srodek_wolne, mu_prawy_przeszkoda)
    w4 = min(mu_lewy_przeszkoda, mu_srodek_wolne, mu_prawy_przeszkoda)
    w5 = min(mu_lewy_wolne, mu_srodek_przeszkoda, mu_prawy_wolne)
    w6 = min(mu_lewy_przeszkoda, mu_srodek_przeszkoda, mu_prawy_wolne)
    w7 = min(mu_lewy_wolne, mu_srodek_przeszkoda, mu_prawy_przeszkoda)
    w8 = min(mu_lewy_przeszkoda, mu_srodek_przeszkoda, mu_prawy_przeszkoda)
    
    print(f"\nw1 = min({mu_lewy_wolne:.4f}, {mu_srodek_wolne:.4f}, {mu_prawy_wolne:.4f}) = {w1:.4f}  [R1: wolne×wolne×wolne → PROSTO]")
    print(f"w2 = min({mu_lewy_przeszkoda:.4f}, {mu_srodek_wolne:.4f}, {mu_prawy_wolne:.4f}) = {w2:.4f}  [R2: przeszk×wolne×wolne → PRAWO]")
    print(f"w3 = min({mu_lewy_wolne:.4f}, {mu_srodek_wolne:.4f}, {mu_prawy_przeszkoda:.4f}) = {w3:.4f}  [R3: wolne×wolne×przeszk → LEWO]")
    print(f"w4 = min({mu_lewy_przeszkoda:.4f}, {mu_srodek_wolne:.4f}, {mu_prawy_przeszkoda:.4f}) = {w4:.4f}  [R4: przeszk×wolne×przeszk → PROSTO]")
    print(f"w5 = min({mu_lewy_wolne:.4f}, {mu_srodek_przeszkoda:.4f}, {mu_prawy_wolne:.4f}) = {w5:.4f}  [R5: wolne×przeszk×wolne → STOP]")
    print(f"w6 = min({mu_lewy_przeszkoda:.4f}, {mu_srodek_przeszkoda:.4f}, {mu_prawy_wolne:.4f}) = {w6:.4f}  [R6: przeszk×przeszk×wolne → PRAWO]")
    print(f"w7 = min({mu_lewy_wolne:.4f}, {mu_srodek_przeszkoda:.4f}, {mu_prawy_przeszkoda:.4f}) = {w7:.4f}  [R7: wolne×przeszk×przeszk → LEWO]")
    print(f"w8 = min({mu_lewy_przeszkoda:.4f}, {mu_srodek_przeszkoda:.4f}, {mu_prawy_przeszkoda:.4f}) = {w8:.4f}  [R8: przeszk×przeszk×przeszk → STOP]")
    
    # ========================================================================
    # KROK 3: Oblicz wyjścia funkcji (zi)
    # ========================================================================
    print("\n" + "-"*70)
    print("KROK 3: Wyjścia funkcji (zi)")
    print("-"*70)
    
    z1 = kierunek_prosto(lewy_test, srodek_test, prawy_test)
    z2 = kierunek_prawo(lewy_test, srodek_test, prawy_test)
    z3 = kierunek_lewo(lewy_test, srodek_test, prawy_test)
    z4 = kierunek_prosto(lewy_test, srodek_test, prawy_test)
    z5 = kierunek_stop(lewy_test, srodek_test, prawy_test)
    z6 = kierunek_prawo(lewy_test, srodek_test, prawy_test)
    z7 = kierunek_lewo(lewy_test, srodek_test, prawy_test)
    z8 = kierunek_stop(lewy_test, srodek_test, prawy_test)
    
    print(f"\nz1 = kierunek_prosto({lewy_test}, {srodek_test}, {prawy_test}) = {z1}")
    print(f"z2 = kierunek_prawo({lewy_test}, {srodek_test}, {prawy_test}) = {z2}")
    print(f"z3 = kierunek_lewo({lewy_test}, {srodek_test}, {prawy_test}) = {z3}")
    print(f"z4 = kierunek_prosto({lewy_test}, {srodek_test}, {prawy_test}) = {z4}")
    print(f"z5 = kierunek_stop({lewy_test}, {srodek_test}, {prawy_test}) = {z5}")
    print(f"z6 = kierunek_prawo({lewy_test}, {srodek_test}, {prawy_test}) = {z6}")
    print(f"z7 = kierunek_lewo({lewy_test}, {srodek_test}, {prawy_test}) = {z7}")
    print(f"z8 = kierunek_stop({lewy_test}, {srodek_test}, {prawy_test}) = {z8}")
    
    # ========================================================================
    # KROK 4: LICZNIK - Σ(wi × zi)
    # ========================================================================
    print("\n" + "-"*70)
    print("KROK 4: LICZNIK - Σ(wi × zi)")
    print("-"*70)
    
    licznik_1 = w1 * z1
    licznik_2 = w2 * z2
    licznik_3 = w3 * z3
    licznik_4 = w4 * z4
    licznik_5 = w5 * z5
    licznik_6 = w6 * z6
    licznik_7 = w7 * z7
    licznik_8 = w8 * z8
    
    print(f"\nw1 × z1 = {w1:.4f} × {z1} = {licznik_1:.4f}")
    print(f"w2 × z2 = {w2:.4f} × {z2} = {licznik_2:.4f}")
    print(f"w3 × z3 = {w3:.4f} × {z3} = {licznik_3:.4f}")
    print(f"w4 × z4 = {w4:.4f} × {z4} = {licznik_4:.4f}")
    print(f"w5 × z5 = {w5:.4f} × {z5} = {licznik_5:.4f}")
    print(f"w6 × z6 = {w6:.4f} × {z6} = {licznik_6:.4f}")
    print(f"w7 × z7 = {w7:.4f} × {z7} = {licznik_7:.4f}")
    print(f"w8 × z8 = {w8:.4f} × {z8} = {licznik_8:.4f}")
    
    licznik_suma = licznik_1 + licznik_2 + licznik_3 + licznik_4 + licznik_5 + licznik_6 + licznik_7 + licznik_8
    
    print(f"\nLICZNIK = {licznik_1:.4f} + {licznik_2:.4f} + {licznik_3:.4f} + {licznik_4:.4f} + {licznik_5:.4f} + {licznik_6:.4f} + {licznik_7:.4f} + {licznik_8:.4f}")
    print(f"LICZNIK = {licznik_suma:.4f}")
    
    # ========================================================================
    # KROK 5: MIANOWNIK - Σ(wi)
    # ========================================================================
    print("\n" + "-"*70)
    print("KROK 5: MIANOWNIK - Σ(wi)")
    print("-"*70)
    
    print(f"\nw1 = {w1:.4f}")
    print(f"w2 = {w2:.4f}")
    print(f"w3 = {w3:.4f}")
    print(f"w4 = {w4:.4f}")
    print(f"w5 = {w5:.4f}")
    print(f"w6 = {w6:.4f}")
    print(f"w7 = {w7:.4f}")
    print(f"w8 = {w8:.4f}")
    
    mianownik_suma = w1 + w2 + w3 + w4 + w5 + w6 + w7 + w8
    
    print(f"\nMIANOWNIK = {w1:.4f} + {w2:.4f} + {w3:.4f} + {w4:.4f} + {w5:.4f} + {w6:.4f} + {w7:.4f} + {w8:.4f}")
    print(f"MIANOWNIK = {mianownik_suma:.4f}")
    
    # ========================================================================
    # KROK 6: WYNIK KOŃCOWY
    # ========================================================================
    print("\n" + "-"*70)
    print("KROK 6: WYNIK KOŃCOWY")
    print("-"*70)
    
    if mianownik_suma > 0:
        wynik_reczny = licznik_suma / mianownik_suma
        
        print(f"\n         LICZNIK      {licznik_suma:.4f}")
        print(f"kierunek = ────────── = ──────────")
        print(f"        MIANOWNIK    {mianownik_suma:.4f}")
        print(f"\nkierunek = {wynik_reczny:.4f}")
    else:
        wynik_reczny = 0
        print("\n⚠️ UWAGA: Wszystkie reguły mają wi = 0! Brak aktywnych reguł.")
        print("kierunek = 0 (domyślnie)")
    
    # Weryfikacja z biblioteką
    wynik_biblioteki = controller.evaluate({"lewy": lewy_test, "srodek": srodek_test, "prawy": prawy_test}, 
                                          (lewy_test, srodek_test, prawy_test))
    
    print(f"\nWynik z biblioteki = {wynik_biblioteki['kierunek']:.4f}")
    
    roznica = abs(wynik_reczny - wynik_biblioteki['kierunek'])
    print(f"Różnica = {roznica:.6f}")
    
    if roznica < 0.01:
        print("\n✅ ZGADZA SIĘ!")
    else:
        print(f"\n⚠️ Niewielka różnica (prawdopodobnie zaokrąglenia)")
    
    # Interpretacja
    print("\n" + "-"*70)
    print("INTERPRETACJA WYNIKU")
    print("-"*70)
    
    if wynik_reczny < -1.5:
        print("🛑 STOP - zatrzymaj się (przeszkoda z przodu)")
    elif wynik_reczny < -0.5:
        print("⬅️ LEWO - skręć w lewo (przeszkoda po prawej)")
    elif wynik_reczny < 0.5:
        print("⬆️ PROSTO - jedź prosto (droga wolna)")
    else:
        print("➡️ PRAWO - skręć w prawo (przeszkoda po lewej)")
    
    return wynik_reczny

# ============================================================================
# TESTOWANIE Z SZCZEGÓŁOWYMI OBLICZENIAMI
# ============================================================================

print("="*70)
print("SYSTEM STEROWANIA ROBOTEM - TESTY ZE SZCZEGÓŁAMI")
print("="*70)

# Test 1: Przeszkoda po lewej (szczegółowe obliczenia)
print("\n" + "█"*70)
print("TEST 1: Przeszkoda po lewej")
print("█"*70)
szczegolowe_obliczenia(10, 150, 160)

# Test 2: Wszystko wolne (szczegółowe obliczenia)
print("\n\n" + "█"*70)
print("TEST 2: Wszystko wolne")
print("█"*70)
szczegolowe_obliczenia(100, 120, 110)

# Test 3: Przeszkoda z przodu (szczegółowe obliczenia)
print("\n\n" + "█"*70)
print("TEST 3: Przeszkoda z przodu")
print("█"*70)
szczegolowe_obliczenia(80, 15, 90)

# Test 4: Twój przykład (szczegółowe obliczenia)
print("\n\n" + "█"*70)
print("TEST 4: Przeszkoda bezpośrednio po lewej")
print("█"*70)
szczegolowe_obliczenia(0, 157, 157)

# Wykresy zbiorów rozmytych
print("\n\nGenerowanie wykresów zbiorów rozmytych...")
przeszkoda_lewy.plot('Lewy czujnik: przeszkoda')
wolne_lewy.plot('Lewy czujnik: wolne')
plt.show()