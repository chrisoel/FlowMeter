import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from flowmeter.database import Database

class BaseMeter:
    def __init__(self, database: Database):
        self.record = 0.0
        self.database = database

    def record_reading(self, new_record):
        last_record = self.get_last_record()

        if not isinstance(new_record, float):
            raise ValueError("Ungültige Eingabe. Es sind nur Fließkommazahlen erlaubt.")
        
        if new_record < 0:
            raise ValueError("Der Zählerstand darf nicht negativ sein.")

        if last_record:
            if new_record < last_record:
                raise ValueError("Der neue Zählerstand muss größer sein als der letzte Zählerstand.")

        self.record = new_record
        self.save_reading()

    def save_reading(self):
        try:
            if isinstance(self, ElectricityMeter):
                self.database.insert_electricity_meter(self.record)
            elif isinstance(self, GasMeter):
                self.database.insert_gas_meter(self.record)
            else:
                raise ValueError("Unbekannter Zählertyp. Der Wert kann nicht gespeichert werden.")
        except Exception:
            raise

    def get_last_record(self):
        try:
            if isinstance(self, ElectricityMeter):
                last_record = self.database.get_last_electricity_meter()
            elif isinstance(self, GasMeter):
                last_record = self.database.get_last_gas_meter()
            else:
                raise ValueError("Unbekannter Zählertyp.")

            if not last_record:
                return 0.0
            
            return last_record[2]
        except Exception as e:
            raise

    def get_all_records(self):
        try:
            if isinstance(self, ElectricityMeter):
                return self.database.get_all_electricity_meters()
            elif isinstance(self, GasMeter):
                return self.database.get_all_gas_meters()
        except Exception:
            raise

    def reset_all_data(self):
        try:
            self.database.delete_all_data()
        except Exception:
            raise

    def delete_record(self, record_id):
        try:
            if isinstance(self, ElectricityMeter):
                self.database.delete_electricity_meter(record_id)
            elif isinstance(self, GasMeter):
                self.database.delete_gas_meter(record_id)
            else:
                raise ValueError("Unbekannter Zählertyp.")
        except Exception as e:
            raise ValueError(f"Fehler beim Löschen des Eintrags mit ID {record_id}: {str(e)}")

class ElectricityMeter(BaseMeter):
    def __init__(self, database=None):
        if database is None:
            database = Database()
            database.initialize()
        super().__init__(database=database)

class GasMeter(BaseMeter):
    def __init__(self, database=None):
        if database is None:
            database = Database()
            database.initialize()
        super().__init__(database=database)

class EnergyProvider:
    def __init__(self, database=None):
        if database is None:
            database = Database()
            database.initialize()
        self.database = database

    def add_provider(self, energy_type, annual_energy, start_date):
        try:
            self.database.insert_energy_provider(energy_type, annual_energy, start_date)
        except Exception as e:
            raise ValueError(f"Fehler beim Hinzufügen/Aktualisieren des Energieanbieters: {str(e)}")

    def update_provider(self, energy_type, annual_energy, start_date):
        try:
            self.database.update_energy_provider(energy_type, annual_energy, start_date)
        except Exception as e:
            raise ValueError(f"Fehler beim Aktualisieren des Energieanbieters: {str(e)}")

    def delete_provider(self, energy_type):
        try:
            self.database.delete_energy_provider(energy_type)
        except Exception as e:
            raise ValueError(f"Fehler beim Löschen des Energieanbieters: {str(e)}")

    def get_provider(self, energy_type):
        try:
            return self.database.get_energy_provider(energy_type)
        except Exception as e:
            raise ValueError(f"Fehler beim Abrufen des Energieanbieters: {str(e)}")

    def get_all_providers(self):
        try:
            return self.database.get_all_energy_providers()
        except Exception as e:
            raise ValueError(f"Fehler beim Abrufen aller Energieanbieter: {str(e)}")