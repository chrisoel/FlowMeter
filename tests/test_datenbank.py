import pytest
import os
from datetime import datetime
from flowmeter.datenbank import Datenbank

@pytest.fixture
def test_database():
    test_db = "tests/test_flowmeter.db"
    schema_file = "flowmeter/database.yaml"
    db = Datenbank(db_name=test_db, schema_file=schema_file)
    db.initialize()
    yield db
    if os.path.exists(test_db):
        os.remove(test_db)

def test_database_creation(test_database):
    db = test_database
    assert os.path.exists(db.db_name), "Die Datenbankdatei sollte existieren."

def test_stromzaehler_eintrag(test_database):
    db = test_database
    db.insert_stromzaehler("D3-XX XXXXX", "2025-01-24 14:00:00", 123456.7)
    result = db.get_stromzaehler_view()
    assert len(result) == 1, "Es sollte genau ein Stromzähler-Eintrag vorhanden sein."
    assert result[0][1] == "D3-XX XXXXX"
    assert result[0][2] == "2025-01-24 14:00:00"
    assert result[0][3] == 123456.7

def test_gaszaehler_eintrag(test_database):
    db = test_database
    db.insert_gaszaehler("X XXXXX XXXX XXXX", "2025-01-24 14:30:00", 12345.678)
    result = db.get_gaszaehler_view()
    assert len(result) == 1, "Es sollte genau ein Gaszähler-Eintrag vorhanden sein."
    assert result[0][1] == "X XXXXX XXXX XXXX"
    assert result[0][2] == "2025-01-24 14:30:00"
    assert result[0][3] == 12345.678

def test_zaehlerstand_validierung(test_database):
    db = test_database
    with pytest.raises(ValueError):
        db.insert_stromzaehler("D3-XX XXXXX", "2025-01-24 14:00:00", -123456.7)
    with pytest.raises(ValueError):
        db.insert_gaszaehler("X XXXXX XXXX XXXX", "2025-01-24 14:30:00", -12345.678)

def test_zeitstempel_format(test_database):
    db = test_database
    db.insert_stromzaehler("D3-XX XXXXX", "2025-01-24 15:00:00", 123456.7)
    result = db.get_stromzaehler_view()
    zeitstempel = result[0][2]
    datetime.strptime(zeitstempel, "%Y-%m-%d %H:%M:%S")

def test_stromzaehler_id_last_view(test_database):
    db = test_database
    db.insert_stromzaehler("D3-XX XXXXX", "2025-01-24 15:00:00", 123456.7)
    db.insert_stromzaehler("D3-XX XXXXX", "2025-01-24 16:00:00", 123457.7)
    result = db.get_stromzaehler_id_last_view()
    assert len(result) == 1, "Die View sollte nur den letzten Eintrag liefern."
    assert result[0][2] == "2025-01-24 16:00:00"
    assert result[0][3] == 123457.7

def test_gaszaehler_id_last_view(test_database):
    db = test_database
    db.insert_gaszaehler("X XXXXX XXXX XXXX", "2025-01-24 15:30:00", 12345.678)
    db.insert_gaszaehler("X XXXXX XXXX XXXX", "2025-01-24 16:30:00", 12346.678)
    result = db.get_gaszaehler_id_last_view()
    assert len(result) == 1, "Die View sollte nur den letzten Eintrag liefern."
    assert result[0][2] == "2025-01-24 16:30:00"
    assert result[0][3] == 12346.678