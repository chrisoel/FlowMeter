import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flowmeter.database.database import Database

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
            result = self.database.get_energy_provider(energy_type)
            if result:
                return {
                    'energy_type': result[1],
                    'annual_energy': result[2],
                    'start_date': result[3]
                }
            return None
        except Exception as e:
            raise ValueError(f"Fehler beim Abrufen des Energieanbieters: {str(e)}")

    def get_all_providers(self):
        try:
            results = self.database.get_all_energy_providers()
            return [
                {
                    'energy_type': result[1],
                    'annual_energy': result[2],
                    'start_date': result[3]
                }
                for result in results
            ]
        except Exception as e:
            raise ValueError(f"Fehler beim Abrufen aller Energieanbieter: {str(e)}")

    def prepare_monthly_data(self, energy_type, current_date=None):
        try:
            provider = self.get_provider(energy_type)
            if not provider:
                raise ValueError(f"Kein Anbieter mit Typ {energy_type} gefunden.")

            annual_energy = provider['annual_energy']
            start_date = datetime.strptime(provider['start_date'], '%Y-%m-%d')

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
        
    def calculate_consumption(self, meter_type):
        try:
            if meter_type == "electricity":
                entries = self.database.get_all_electricity_meters()
            elif meter_type == "gas":
                entries = self.database.get_all_gas_meters()
            else:
                raise ValueError("Ungültiger Zählertyp. Verwenden Sie 'electricity' oder 'gas'.")

            entries = sorted(entries, key=lambda x: x[1])

            if len(entries) < 2:
                return {"message": "Nicht genügend Datenpunkte für Verbrauchsberechnung."}

            consumptions = []
            for i in range(1, len(entries)):
                prev_value, prev_time = entries[i - 1][0], datetime.strptime(entries[i - 1][1], "%Y-%m-%d %H:%M:%S")
                current_value, current_time = entries[i][0], datetime.strptime(entries[i][1], "%Y-%m-%d %H:%M:%S")

                time_diff = (current_time - prev_time).total_seconds() / 3600

                if time_diff > 0:
                    consumptions.append((current_value - prev_value) / time_diff)

            if not consumptions:
                return {
                    "message": "Keine gültigen Verbrauchsdaten vorhanden.",
                    "average_consumption": None,
                    "consumptions": [],
                    "total_entries": len(entries)
                }

            avg_consumption = sum(consumptions) / len(consumptions)

            return {
                "average_consumption": avg_consumption,
                "consumptions": consumptions,
                "total_entries": len(entries)
            }

        except Exception as e:
            raise ValueError(f"Fehler bei der Verbrauchsberechnung: {str(e)}")
