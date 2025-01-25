import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import re
import sqlite3
import yaml

class Database:
    def __init__(self, database_name="flowmeter/meter_readings.db", schema_file="flowmeter/database_model.yaml"):
        self.database_name = database_name
        self.schema_file = schema_file
        self.connection = None
        self._load_schema()

    def _load_schema(self):
        try:
            with open(self.schema_file, "r") as file:
                self.schema = yaml.safe_load(file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Schema-Datei nicht gefunden: {e}")

    def _connect(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.database_name)
        return self.connection

    def _execute_sql(self, sql, params=None, fetchone=False, fetchall=False, executescript=False):
        with self._connect() as connection:
            cursor = connection.cursor()
            if executescript:
                cursor.executescript(sql)
            else:
                cursor.execute(sql, params or ())
            connection.commit()
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()

    def _validate_input(self, value, pattern, value_name, is_float=True):
        if is_float and not isinstance(value, float):
            raise ValueError(f"{value_name} muss ein Float-Wert sein.")
        if not re.match(pattern, str(value)):
            raise ValueError(f"{value_name} entspricht nicht dem Muster {pattern}.")

    def initialize(self):
        if not self._is_consistent():
            self._create_database()

    def _create_database(self):
        with self._connect() as connection:
            cursor = connection.cursor()
            for table in self.schema["database"]["tables"]:
                table_name = table["name"]
                columns = ", ".join(
                    [f"{column['name']} {column['type']} {' '.join(column.get('constraints', []))}" for column in table["columns"]]
                )
                unique_constraints = table.get("unique_constraints", [])
                for constraint in unique_constraints:
                    columns += f", UNIQUE ({', '.join(constraint['columns'])})"
                sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
                cursor.execute(sql)
            for view in self.schema["database"]["views"]:
                sql = f"CREATE VIEW IF NOT EXISTS {view['name']} AS {view['definition']}"
                cursor.execute(sql)
            connection.commit()

    def _is_consistent(self):
        if not os.path.exists(self.database_name):
            return False
        with self._connect() as connection:
            cursor = connection.cursor()
            try:
                for table in self.schema["database"]["tables"]:
                    cursor.execute(f"SELECT 1 FROM {table['name']} LIMIT 1;")
                for view in self.schema["database"]["views"]:
                    cursor.execute(f"SELECT 1 FROM {view['name']} LIMIT 1;")
            except sqlite3.Error:
                return False
        return True

    def insert_meter_reading(self, meter_type, meter_reading, pattern):
        self._validate_input(meter_reading, pattern, f"{meter_type}-Zählerstand")
        sql = self.schema["database"]["sql"][f"insert_{meter_type}_meter"]
        self._execute_sql(sql, (meter_reading,))

    def insert_electricity_meter(self, electricity_meter_reading):
        self.insert_meter_reading("electricity", electricity_meter_reading, r"^\d{0,6}(\.\d)?$")

    def insert_gas_meter(self, gas_meter_reading):
        self.insert_meter_reading("gas", gas_meter_reading, r"^\d{0,5}(\.\d{1,3})?$")

    def get_last_entry(self, meter_type):
        sql = self.schema["database"]["sql"][f"query_{meter_type}_meter_last_entry"]
        return self._execute_sql(sql, fetchone=True)

    def get_last_electricity_meter(self):
        return self.get_last_entry("electricity")

    def get_last_gas_meter(self):
        return self.get_last_entry("gas")

    def get_all_entries(self, meter_type):
        sql = self.schema["database"]["sql"][f"query_{meter_type}_meter_all_entries"]
        return self._execute_sql(sql, fetchall=True)

    def get_all_electricity_meters(self):
        return self.get_all_entries("electricity")

    def get_all_gas_meters(self):
        return self.get_all_entries("gas")

    def delete_all_data(self):
        sql = self.schema["database"]["sql"]["delete_all_data"]
        self._execute_sql(sql, executescript=True)

    def delete_entry(self, meter_type, record_id):
        sql = self.schema["database"]["sql"][f"delete_{meter_type}_meter_entry"]
        self._execute_sql(sql, (record_id,))

    def delete_electricity_meter(self, record_id):
        self.delete_entry("electricity", record_id)

    def delete_gas_meter(self, record_id):
        self.delete_entry("gas", record_id)