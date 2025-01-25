import pytest
from datetime import datetime
from flowmeter.logik import Stromzaehler, Gaszaehler
from flowmeter.datenbank import Datenbank
import time

@pytest.fixture
def test_datenbank():
    db = Datenbank(db_name="tests/test_flowmeter.db")
    db.initialize()
    time.sleep(1)
    return db

def test_zaehlerstand_erfassen(test_datenbank):
    strom = Stromzaehler(db=test_datenbank)
    strom.erfasse_zaehlerstand(123456.7)
    assert strom.stand == 123456.7

    gas = Gaszaehler(db=test_datenbank)
    gas.erfasse_zaehlerstand(12345.678)
    assert gas.stand == 12345.678

def test_zaehlerstand_erfassen_zu_kurz(test_datenbank):
    strom = Stromzaehler(db=test_datenbank)
    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 7 Stellen haben."):
        strom.erfasse_zaehlerstand(12345.7)

    gas = Gaszaehler(db=test_datenbank)
    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 8 Stellen haben."):
        gas.erfasse_zaehlerstand(1234.678)

def test_zaehlerstand_erfassen_zu_lang(test_datenbank):
    strom = Stromzaehler(db=test_datenbank)
    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 7 Stellen haben."):
        strom.erfasse_zaehlerstand(1234567.8)

    gas = Gaszaehler(db=test_datenbank)
    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 8 Stellen haben."):
        gas.erfasse_zaehlerstand(123456.789)

def test_zaehlerstand_ist_float(test_datenbank):
    strom = Stromzaehler(db=test_datenbank)
    strom.erfasse_zaehlerstand(123456.7)
    assert isinstance(strom.stand, float)

    gas = Gaszaehler(db=test_datenbank)
    gas.erfasse_zaehlerstand(12345.678)
    assert isinstance(gas.stand, float)

def test_zaehlerstand_negativ_nicht_erlaubt(test_datenbank):
    strom = Stromzaehler(db=test_datenbank)
    with pytest.raises(ValueError, match="Der Zählerstand darf nicht negativ sein."):
        strom.erfasse_zaehlerstand(-123456.7)

    gas = Gaszaehler(db=test_datenbank)
    with pytest.raises(ValueError, match="Der Zählerstand darf nicht negativ sein."):
        gas.erfasse_zaehlerstand(-12345.678)

def test_zaehlerstand_validierung(test_datenbank):
    strom = Stromzaehler(db=test_datenbank)
    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 7 Stellen haben."):
        strom.erfasse_zaehlerstand(12345.6)

    gas = Gaszaehler(db=test_datenbank)
    with pytest.raises(ValueError, match="Der Zählerstand muss insgesamt 8 Stellen haben."):
        gas.erfasse_zaehlerstand(123456.7)

def test_zaehlerstand_in_datenbank_gespeichert(test_datenbank):
    strom = Stromzaehler(db=test_datenbank)
    strom.erfasse_zaehlerstand(123456.7)

    gas = Gaszaehler(db=test_datenbank)
    gas.erfasse_zaehlerstand(12345.678)

    strom_ergebnisse = test_datenbank.get_stromzaehler_id_last_view()
    gas_ergebnisse = test_datenbank.get_gaszaehler_id_last_view()

    assert any(row[3] == 123456.7 for row in strom_ergebnisse)
    assert any(row[3] == 12345.678 for row in gas_ergebnisse)

def test_zaehlernummer_standard(test_datenbank):
    strom = Stromzaehler(db=test_datenbank)
    assert strom.zaehlernummer == "D3-XX XXXXX"

    gas = Gaszaehler(db=test_datenbank)
    assert gas.zaehlernummer == "X XXXXX XXXX XXXX"

def test_zaehlernummer_anpassen(test_datenbank):
    strom = Stromzaehler(db=test_datenbank, zaehlernummer="D3-12 34567")
    assert strom.zaehlernummer == "D3-12 34567"
    strom.erfasse_zaehlerstand(123456.7)

    gas = Gaszaehler(db=test_datenbank, zaehlernummer="A 12345 6789 0123")
    assert gas.zaehlernummer == "A 12345 6789 0123"
    gas.erfasse_zaehlerstand(12345.678)

def test_zaehlerstand_speichern_mit_zeitstempel(test_datenbank):
    strom = Stromzaehler(db=test_datenbank)
    strom.erfasse_zaehlerstand(123456.7)

    gas = Gaszaehler(db=test_datenbank)
    gas.erfasse_zaehlerstand(12345.678)

    strom_ergebnisse = test_datenbank.get_stromzaehler_id_view(strom.zaehlernummer)
    gas_ergebnisse = test_datenbank.get_gaszaehler_id_view(gas.zaehlernummer)

    for row in strom_ergebnisse + gas_ergebnisse:
        zeitstempel = row[2]
        try:
            datetime.strptime(zeitstempel, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pytest.fail("Ungültiges Zeitstempelformat.")