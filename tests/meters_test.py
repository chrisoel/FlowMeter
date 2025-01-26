import pytest
from flowmeter.logic.meters import ElectricityMeter, GasMeter
from flowmeter.database.database import Database

@pytest.fixture
def test_database():
    database = Database(database_name="tests/test_flowmeter.db")
    database.initialize()
    yield database
    database.delete_all_data()
    database.connection.close()

def test_record_reading_electricity_successful(test_database):
    electricity = ElectricityMeter(database=test_database)
    electricity.record_reading(123456.7)
    assert electricity.record == 123456.7

def test_record_reading_gas_successful(test_database):
    gas = GasMeter(database=test_database)
    gas.record_reading(12345.678)
    assert gas.record == 12345.678

def test_record_reading_negative_value(test_database):
    electricity = ElectricityMeter(database=test_database)
    with pytest.raises(ValueError, match="Der Zählerstand darf nicht negativ sein."):
        electricity.record_reading(-123456.7)

    gas = GasMeter(database=test_database)
    with pytest.raises(ValueError, match="Der Zählerstand darf nicht negativ sein."):
        gas.record_reading(-12345.678)

def test_record_reading_less_than_last_value(test_database):
    electricity = ElectricityMeter(database=test_database)
    electricity.record_reading(123456.7)
    with pytest.raises(ValueError, match="Der neue Zählerstand muss größer sein als der letzte Zählerstand."):
        electricity.record_reading(123455.6)

    gas = GasMeter(database=test_database)
    gas.record_reading(12345.678)
    with pytest.raises(ValueError, match="Der neue Zählerstand muss größer sein als der letzte Zählerstand."):
        gas.record_reading(12345.5)

def test_reading_saved_to_database(test_database):
    electricity = ElectricityMeter(database=test_database)
    electricity.record_reading(123456.7)

    gas = GasMeter(database=test_database)
    gas.record_reading(12345.678)

    electricity_result = test_database.get_last_electricity_meter()
    gas_result = test_database.get_last_gas_meter()

    assert electricity_result is not None
    assert gas_result is not None

    assert electricity_result[2] == 123456.7
    assert gas_result[2] == 12345.678

def test_reading_boundary_values(test_database):
    electricity = ElectricityMeter(database=test_database)
    electricity.record_reading(100000.0)
    electricity.record_reading(999999.9)

    gas = GasMeter(database=test_database)
    gas.record_reading(10000.000)
    gas.record_reading(99999.999)