import pytest
import os
from flowmeter.database.database import Database

@pytest.fixture
def test_database():
    test_db = "tests/test_flowmeter.db"
    schema_file = "flowmeter/database/database_model.yaml"
    db = Database(database_name=test_db, schema_file=schema_file)
    db.initialize()
    yield db
    if os.path.exists(test_db):
        os.remove(test_db)

def test_database_file_creation(test_database):
    db = test_database
    assert os.path.exists(db.database_name), "Die Datenbankdatei sollte existieren."

def test_electricity_meter_entry(test_database):
    db = test_database
    db.insert_electricity_meter(123456.7)
    result = db.get_all_electricity_meters()
    assert len(result) == 1, "Es sollte genau einen Stromzähler-Eintrag geben."
    assert result[0][2] == 123456.7, "Der Stromzählerwert sollte korrekt sein."

def test_gas_meter_entry(test_database):
    db = test_database
    db.insert_gas_meter(12345.678)
    result = db.get_all_gas_meters()
    assert len(result) == 1, "Es sollte genau einen Gaszähler-Eintrag geben."
    assert result[0][2] == 12345.678, "Der Gaszählerwert sollte korrekt sein."

def test_invalid_meter_reading(test_database):
    db = test_database
    with pytest.raises(ValueError):
        db.insert_electricity_meter(-123456.7)
    with pytest.raises(ValueError):
        db.insert_gas_meter(-12345.678)
    with pytest.raises(ValueError):
        db.insert_electricity_meter("123456.7")
    with pytest.raises(ValueError):
        db.insert_gas_meter("12345.678")

def test_last_electricity_meter_entry(test_database):
    db = test_database
    db.insert_electricity_meter(123456.7)
    db.insert_electricity_meter(123457.7)
    result = db.get_last_electricity_meter()
    assert result[2] == 123457.7, "Der letzte Stromzählerwert sollte mit dem neuesten Eintrag übereinstimmen."

def test_last_gas_meter_entry(test_database):
    db = test_database
    db.insert_gas_meter(12345.678)
    db.insert_gas_meter(12346.678)
    result = db.get_last_gas_meter()
    assert result[2] == 12346.678, "Der letzte Gaszählerwert sollte mit dem neuesten Eintrag übereinstimmen."

def test_database_clear_functionality(test_database):
    db = test_database
    db.insert_electricity_meter(123456.7)
    db.insert_gas_meter(12345.678)

    assert len(db.get_all_electricity_meters()) > 0, "Es sollten Stromzähler-Einträge vorhanden sein."
    assert len(db.get_all_gas_meters()) > 0, "Es sollten Gaszähler-Einträge vorhanden sein."

    db.delete_all_data()

    assert len(db.get_all_electricity_meters()) == 0, "Die Stromzähler-Tabelle sollte leer sein."
    assert len(db.get_all_gas_meters()) == 0, "Die Gaszähler-Tabelle sollte leer sein."

def test_electricity_meter_pattern_validation(test_database):
    db = test_database
    with pytest.raises(ValueError):
        db.insert_electricity_meter(12345.67)
    with pytest.raises(ValueError):
        db.insert_electricity_meter(1234567.0)
    with pytest.raises(ValueError):
        db.insert_electricity_meter("123456.7")
    with pytest.raises(ValueError):
        db.insert_electricity_meter(1234567)

def test_gas_meter_pattern_validation(test_database):
    db = test_database
    with pytest.raises(ValueError):
        db.insert_gas_meter(1234.6789)
    with pytest.raises(ValueError):
        db.insert_gas_meter(123456.78)
    with pytest.raises(ValueError):
        db.insert_gas_meter("12345.678") 
    with pytest.raises(ValueError):
        db.insert_gas_meter(12345678)

def test_insert_energy_provider(test_database):
    db = test_database
    db.insert_energy_provider('electricity', 2000, '2025-01-01')
    result = db.get_energy_provider('electricity')
    assert result[1] == 'electricity', "Der Energie-Typ sollte 'electricity' sein."
    assert result[2] == 2000, "Der jährliche Energieverbrauch sollte 2000 sein."

def test_update_energy_provider(test_database):
    db = test_database
    db.insert_energy_provider('gas', 1500, '2025-01-01')
    db.update_energy_provider('gas', 1800, '2025-06-01')
    result = db.get_energy_provider('gas')
    assert result[2] == 1800, "Der jährliche Energieverbrauch sollte auf 1800 aktualisiert sein."
    assert result[3] == '2025-06-01', "Das Startdatum sollte auf '2025-06-01' aktualisiert sein."

def test_delete_energy_provider(test_database):
    db = test_database
    db.insert_energy_provider('electricity', 2000, '2025-01-01')
    db.delete_energy_provider('electricity')
    result = db.get_energy_provider('electricity')
    assert result is None, "Der Eintrag sollte gelöscht sein."

def test_get_all_energy_providers(test_database):
    db = test_database
    db.insert_energy_provider('electricity', 2000, '2025-01-01')
    db.insert_energy_provider('gas', 1500, '2025-01-01')
    results = db.get_all_energy_providers()
    assert len(results) == 2, "Es sollten genau zwei Energieversorger-Einträge vorhanden sein."