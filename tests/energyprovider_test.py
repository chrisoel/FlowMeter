from datetime import datetime
import pytest
from flowmeter.logic.energyprovider import EnergyProvider
from flowmeter.database.database import Database
from dateutil.relativedelta import relativedelta

@pytest.fixture
def test_database():
    database = Database(database_name="tests/test_flowmeter.db")
    database.initialize()
    yield database
    database.delete_all_data()
    database.connection.close()

def test_add_energy_provider(test_database):
    provider = EnergyProvider(database=test_database)
    provider.add_provider("electricity", 2000, "2025-01-01")
    result = provider.get_provider("electricity")

    assert result is not None
    assert result['energy_type'] == "electricity"
    assert result['annual_energy'] == 2000
    assert result['start_date'] == "2025-01-01"

def test_update_energy_provider(test_database):
    provider = EnergyProvider(database=test_database)
    provider.add_provider("gas", 1500, "2025-01-01")
    provider.update_provider("gas", 1800, "2025-06-01")
    result = provider.get_provider("gas")

    assert result is not None
    assert result['energy_type'] == "gas"
    assert result['annual_energy'] == 1800
    assert result['start_date'] == "2025-06-01"

def test_get_all_energy_providers(test_database):
    provider = EnergyProvider(database=test_database)
    provider.add_provider("electricity", 2000, "2025-01-01")
    provider.add_provider("gas", 1500, "2025-01-01")
    results = provider.get_all_providers()

    assert len(results) == 2
    assert results[0]['energy_type'] == "electricity"
    assert results[1]['energy_type'] == "gas"

def test_delete_energy_provider(test_database):
    provider = EnergyProvider(database=test_database)
    provider.add_provider("electricity", 2000, "2025-01-01")
    provider.delete_provider("electricity")
    result = provider.get_provider("electricity")

    assert result is None

def prepare_monthly_data(self, energy_type, current_date=None):
    try:
        provider = self.get_provider(energy_type)
        if not provider:
            raise ValueError(f"Kein Anbieter mit Typ {energy_type} gefunden.")

        annual_energy = provider[2]
        start_date = datetime.strptime(provider[3], '%Y-%m-%d')

        if current_date is None:
            current_date = datetime.now()

        monthly_energy = annual_energy / 12
        start_period = current_date - relativedelta(years=1)
        end_period = current_date + relativedelta(years=1)
        data_points = []
        current = start_period
        while current <= end_period:
            if current >= start_date:
                data_points.append({
                    'date': current.strftime('%Y-%m-%d'),
                    'consumption': monthly_energy
                })
            current += relativedelta(months=1)

        return data_points

    except Exception as e:
        raise ValueError(f"Fehler bei der Vorbereitung der monatlichen Daten: {str(e)}")
    
def test_calculate_consumption(test_database):
    provider = EnergyProvider(database=test_database)

    provider.database.insert_electricity_meter(1000.0)
    provider.database.insert_electricity_meter(1500.0)
    provider.database.insert_electricity_meter(1800.0)

    result = provider.calculate_consumption("electricity")

    if result["message"] == "Keine gültigen Verbrauchsdaten vorhanden.":
        assert result["average_consumption"] is None
        assert len(result["consumptions"]) == 0
    else:
        assert "average_consumption" in result
        assert result["average_consumption"] > 0
        assert len(result["consumptions"]) == 2 