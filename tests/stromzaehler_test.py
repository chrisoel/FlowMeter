import pytest
from flowmeter.main import Stromzaehler

@pytest.fixture
def clean_test_datei():
    test_datei = "tests/zaehlerstand_test.txt"
    with open(test_datei, "w") as file:
        file.truncate(0)
    yield test_datei
    with open(test_datei, "w") as file:
        file.truncate(0)

def test_strom_zaehlerstand_erfassen(clean_test_datei):
    # User Story: US1_Strom_erfassen
    zaehler = Stromzaehler(clean_test_datei)
    zaehler.erfasse_zaehlerstand(123456.7)
    assert zaehler.stand == 123456.7, "Der Zählerstand sollte 123456.7 sein."

def test_strom_zaehlerstand_ist_float(clean_test_datei):
    # User Story: US1_Strom_erfassen
    zaehler = Stromzaehler(clean_test_datei)
    zaehler.erfasse_zaehlerstand(123456.7)
    assert isinstance(zaehler.stand, float), "Der Zählerstand sollte ein Float sein."

def test_strom_zaehlerstand_ist_nicht_negativ(clean_test_datei):
    # User Story: US1_Strom_erfassen
    zaehler = Stromzaehler(clean_test_datei)
    with pytest.raises(ValueError, match="Der Zählerstand darf nicht negativ sein."):
        zaehler.erfasse_zaehlerstand(-123456.7)

def test_strom_zaehlerstand_7_stellen_1_komma(clean_test_datei):
    # User Story: US1_Strom_erfassen
    zaehler = Stromzaehler(clean_test_datei)

    zaehler.erfasse_zaehlerstand(123456.7)
    assert zaehler.stand == 123456.7, "Der Zählerstand sollte 123456.7 sein."

    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 7 Stellen haben."):
        zaehler.erfasse_zaehlerstand(12345.67)

    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 7 Stellen haben."):
        zaehler.erfasse_zaehlerstand(1234.56)
    
    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 7 Stellen haben."):
        zaehler.erfasse_zaehlerstand(12345678)

    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 7 Stellen haben."):
        zaehler.erfasse_zaehlerstand(123.456)

def test_strom_zaehlerstand_negativ_nicht_erlaubt(clean_test_datei):
    # User Story: US1_Strom_erfassen
    zaehler = Stromzaehler(clean_test_datei)
    with pytest.raises(ValueError, match="Der Zählerstand darf nicht negativ sein."):
        zaehler.erfasse_zaehlerstand(-123456.7)

def test_strom_zaehlerstand_ungültige_typen(clean_test_datei):
    # User Story: US1_Strom_erfassen
    zaehler = Stromzaehler(clean_test_datei)

    with pytest.raises(ValueError, match="Der Zählerstand muss ein Float sein."):
        zaehler.erfasse_zaehlerstand("123456.7")

    with pytest.raises(ValueError, match="Der Zählerstand muss ein Float sein."):
        zaehler.erfasse_zaehlerstand([123456.7])

def test_strom_zaehlerstand_in_datei_gespeichert(clean_test_datei):
    # User Story: US1_Strom_erfassen
    zaehler = Stromzaehler(clean_test_datei)
    zaehler.erfasse_zaehlerstand(123456.7)

    # Datei prüfen
    with open(clean_test_datei, "r") as file:
        lines = file.readlines()

    assert any("Zähler:123456.7" in line for line in lines), "Der Zählerstand wurde nicht korrekt in der Datei gespeichert."