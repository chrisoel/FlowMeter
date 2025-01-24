import pytest
from datetime import datetime
from flowmeter.logik import Stromzaehler, Gaszaehler

@pytest.fixture
def clean_test_datei():
    test_datei = "tests/zaehler_test.txt"
    with open(test_datei, "w") as file:
        file.truncate(0)
    yield test_datei
    with open(test_datei, "w") as file:
        file.truncate(0)

def test_zaehlerstand_erfassen(clean_test_datei):
    strom = Stromzaehler(clean_test_datei)
    strom.erfasse_zaehlerstand(123456.7)
    assert strom.stand == 123456.7

    gas = Gaszaehler(clean_test_datei)
    gas.erfasse_zaehlerstand(12345.678)
    assert gas.stand == 12345.678

def test_zaehlerstand_ist_float(clean_test_datei):
    strom = Stromzaehler(clean_test_datei)
    strom.erfasse_zaehlerstand(123456.7)
    assert isinstance(strom.stand, float)

    gas = Gaszaehler(clean_test_datei)
    gas.erfasse_zaehlerstand(12345.678)
    assert isinstance(gas.stand, float)

def test_zaehlerstand_negativ_nicht_erlaubt(clean_test_datei):
    strom = Stromzaehler(clean_test_datei)
    with pytest.raises(ValueError, match="Der Zählerstand darf nicht negativ sein."):
        strom.erfasse_zaehlerstand(-123456.7)

    gas = Gaszaehler(clean_test_datei)
    with pytest.raises(ValueError, match="Der Zählerstand darf nicht negativ sein."):
        gas.erfasse_zaehlerstand(-12345.678)

def test_zaehlerstand_validierung(clean_test_datei):
    strom = Stromzaehler(clean_test_datei)
    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 7 Stellen haben."):
        strom.erfasse_zaehlerstand(12345.67)

    gas = Gaszaehler(clean_test_datei)
    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 8 Stellen haben."):
        gas.erfasse_zaehlerstand(1234.5678)

def test_zaehlerstand_in_datei_gespeichert(clean_test_datei):
    strom = Stromzaehler(clean_test_datei)
    strom.erfasse_zaehlerstand(123456.7)
    gas = Gaszaehler(clean_test_datei)
    gas.erfasse_zaehlerstand(12345.678)

    with open(clean_test_datei, "r") as file:
        lines = file.readlines()

    assert any("D3-XX XXXXX" in line and "123456.7" in line for line in lines)
    assert any("X XXXXX XXXX XXXX" in line and "12345.678" in line for line in lines)

def test_zaehlernummer_standard(clean_test_datei):
    strom = Stromzaehler(clean_test_datei)
    assert strom.zaehlernummer == "D3-XX XXXXX"

    gas = Gaszaehler(clean_test_datei)
    assert gas.zaehlernummer == "X XXXXX XXXX XXXX"

def test_zaehlernummer_anpassen(clean_test_datei):
    strom = Stromzaehler(clean_test_datei, zaehlernummer="D3-12 34567")
    assert strom.zaehlernummer == "D3-12 34567"
    strom.erfasse_zaehlerstand(123456.7)

    gas = Gaszaehler(clean_test_datei, zaehlernummer="A 12345 6789 0123")
    assert gas.zaehlernummer == "A 12345 6789 0123"
    gas.erfasse_zaehlerstand(12345.678)

def test_zaehlerstand_speichern_mit_zeitstempel(clean_test_datei):
    strom = Stromzaehler(clean_test_datei)
    strom.erfasse_zaehlerstand(123456.7)
    gas = Gaszaehler(clean_test_datei)
    gas.erfasse_zaehlerstand(12345.678)

    with open(clean_test_datei, "r") as file:
        lines = file.readlines()

    for line in lines:
        zeitstempel = line.split(" | ")[0]
        try:
            datetime.strptime(zeitstempel, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pytest.fail("Ungültiges Zeitstempelformat.")