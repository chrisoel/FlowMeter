import pytest
from flowmeter.logic import ElectricityMeter, GasMeter, EnergyProvider
from flowmeter.database import Database

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

def test_add_energy_provider(test_database):
    provider = EnergyProvider(database=test_database)
    provider.add_provider("electricity", 2000, "2025-01-01")
    result = provider.get_provider("electricity")

    assert result is not None
    assert result[1] == "electricity"
    assert result[2] == 2000
    assert result[3] == "2025-01-01"

def test_update_energy_provider(test_database):
    provider = EnergyProvider(database=test_database)
    provider.add_provider("gas", 1500, "2025-01-01")
    provider.update_provider("gas", 1800, "2025-06-01")
    result = provider.get_provider("gas")

    assert result is not None
    assert result[1] == "gas"
    assert result[2] == 1800
    assert result[3] == "2025-06-01"

def test_get_all_energy_providers(test_database):
    provider = EnergyProvider(database=test_database)
    provider.add_provider("electricity", 2000, "2025-01-01")
    provider.add_provider("gas", 1500, "2025-01-01")
    results = provider.get_all_providers()

    assert len(results) == 2
    assert results[0][1] == "electricity"
    assert results[1][1] == "gas"

def test_delete_energy_provider(test_database):
    provider = EnergyProvider(database=test_database)
    provider.add_provider("electricity", 2000, "2025-01-01")
    provider.delete_provider("electricity")
    result = provider.get_provider("electricity")

    assert result is None