import pytest
from flowmeter.main import Stromzaehler, Gaszaehler

@pytest.fixture
def clean_test_datei():
    test_datei = "tests/zaehler_test.txt"
    with open(test_datei, "w") as file:
        file.truncate(0)
    yield test_datei
    with open(test_datei, "w") as file:
        file.truncate(0)

def test_zaehlerstand_erfassen(clean_test_datei):
    # User Stories: US1_Strom_erfassen, US2_Gas_erfassen

    # Test für Stromzähler
    strom = Stromzaehler(clean_test_datei)
    strom.erfasse_zaehlerstand(123456.7)
    assert strom.stand == 123456.7, "Der Zählerstand für Strom sollte 123456.7 sein."

    # Test für Gaszähler
    gas = Gaszaehler(clean_test_datei)
    gas.erfasse_zaehlerstand(12345.678)
    assert gas.stand == 12345.678, "Der Zählerstand für Gas sollte 12345.678 sein."

def test_zaehlerstand_ist_float(clean_test_datei):
    # User Stories: US1_Strom_erfassen, US2_Gas_erfassen, US5_Zählerstandseingabe_validieren

    # Test für Stromzähler
    strom = Stromzaehler(clean_test_datei)
    strom.erfasse_zaehlerstand(123456.7)
    assert isinstance(strom.stand, float), "Der Zählerstand für Strom sollte ein Float sein."

    # Test für Gaszähler
    gas = Gaszaehler(clean_test_datei)
    gas.erfasse_zaehlerstand(12345.678)
    assert isinstance(gas.stand, float), "Der Zählerstand für Gas sollte ein Float sein."

def test_zaehlerstand_negativ_nicht_erlaubt(clean_test_datei):
    # User Stories: US1_Strom_erfassen, US2_Gas_erfassen, US5_Zählerstandseingabe_validieren

    # Test für Stromzähler
    strom = Stromzaehler(clean_test_datei)
    with pytest.raises(ValueError, match="Der Zählerstand darf nicht negativ sein."):
        strom.erfasse_zaehlerstand(-123456.7)

    # Test für Gaszähler
    gas = Gaszaehler(clean_test_datei)
    with pytest.raises(ValueError, match="Der Zählerstand darf nicht negativ sein."):
        gas.erfasse_zaehlerstand(-12345.678)

def test_zaehlerstand_validierung(clean_test_datei):
    # User Stories: US1_Strom_erfassen, US2_Gas_erfassen, US5_Zählerstandseingabe_validieren

    # Test für Stromzähler (7 Stellen, 1 Nachkommastelle)
    strom = Stromzaehler(clean_test_datei)
    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 7 Stellen haben."):
        strom.erfasse_zaehlerstand(12345.67)

    # Test für Gaszähler (8 Stellen, 3 Nachkommastellen)
    gas = Gaszaehler(clean_test_datei)
    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 8 Stellen haben."):
        gas.erfasse_zaehlerstand(1234.5678)

def test_zaehlerstand_in_datei_gespeichert(clean_test_datei):
    # User Stories: US1_Strom_erfassen, US2_Gas_erfassen

    # Test für Stromzähler
    strom = Stromzaehler(clean_test_datei)
    strom.erfasse_zaehlerstand(123456.7)

    with open(clean_test_datei, "r") as file:
        lines = file.readlines()
    assert any("D3-XX XXXXX: 123456.7" in line for line in lines), f"Strom-Zählerstand wurde nicht korrekt gespeichert: {lines}"

    # Test für Gaszähler
    gas = Gaszaehler(clean_test_datei)
    gas.erfasse_zaehlerstand(12345.678)

    with open(clean_test_datei, "r") as file:
        lines = file.readlines()
    assert any("X XXXXX XXXX XXXX: 12345.678" in line for line in lines), f"Gas-Zählerstand wurde nicht korrekt gespeichert: {lines}"

def test_zaehlernummer_standard(clean_test_datei):
    # User Stories: US3_Stromzählernummer, US4_Gaszählernummer

    # Test für Stromzähler
    strom = Stromzaehler(clean_test_datei)
    assert strom.zaehlernummer == "D3-XX XXXXX", "Die Standard-Zählernummer für Strom ist nicht korrekt."

    # Test für Gaszähler
    gas = Gaszaehler(clean_test_datei)
    assert gas.zaehlernummer == "X XXXXX XXXX XXXX", "Die Standard-Zählernummer für Gas ist nicht korrekt."

def test_zaehlernummer_anpassen(clean_test_datei):
    # User Stories: US3_Stromzählernummer, US4_Gaszählernummer

    # Test für Stromzähler
    strom = Stromzaehler(clean_test_datei, zaehlernummer="D3-12 34567")
    assert strom.zaehlernummer == "D3-12 34567", "Die angepasste Zählernummer für Strom ist nicht korrekt."
    strom.erfasse_zaehlerstand(123456.7)

    with open(clean_test_datei, "r") as file:
        lines = file.readlines()
    assert any("D3-12 34567: 123456.7" in line for line in lines), f"Die angepasste Zählernummer für Strom wurde nicht korrekt gespeichert: {lines}"

    # Test für Gaszähler
    gas = Gaszaehler(clean_test_datei, zaehlernummer="A 12345 6789 0123")
    assert gas.zaehlernummer == "A 12345 6789 0123", "Die angepasste Zählernummer für Gas ist nicht korrekt."
    gas.erfasse_zaehlerstand(12345.678)

    with open(clean_test_datei, "r") as file:
        lines = file.readlines()
    assert any("A 12345 6789 0123: 12345.678" in line for line in lines), f"Die angepasste Zählernummer für Gas wurde nicht korrekt gespeichert: {lines}"