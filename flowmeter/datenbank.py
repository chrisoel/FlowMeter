import sqlite3
import os
import yaml
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Datenbank:
    def __init__(self, db_name="flowmeter/zaehler.db", schema_file="flowmeter/database.yaml"):
        self.db_name = db_name
        self.schema_file = schema_file
        self.connection = None
        self._load_schema()

    def _load_schema(self):
        logging.info("Lade Schema aus der YAML-Datei.")
        try:
            with open(self.schema_file, "r") as file:
                self.schema = yaml.safe_load(file)
                logging.debug(f"Schema erfolgreich geladen: {self.schema}")
        except FileNotFoundError as e:
            logging.error(f"Schema-Datei nicht gefunden: {e}")
            raise

    def _create_database(self):
        logging.info("Erstelle die Datenbank aus dem Schema.")
        with self._connect() as conn:
            cursor = conn.cursor()

            for table in self.schema["database"]["tables"]:
                table_name = table["name"]
                columns = ", ".join(
                    [f"{col['name']} {col['type']} {' '.join(col.get('constraints', []))}" for col in table["columns"]]
                )
                unique_constraints = table.get("unique_constraints", [])
                for unique in unique_constraints:
                    columns += f", UNIQUE ({', '.join(unique['columns'])})"

                sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
                logging.info(f"Tabelle '{table_name}' wird erstellt.")
                logging.debug(f"SQL: {sql}")
                cursor.execute(sql)

            for table in self.schema["database"]["tables"]:
                for trigger in table.get("triggers", []):
                    sql = f"CREATE TRIGGER IF NOT EXISTS {trigger['name']} {trigger['timing']} ON {table['name']} FOR EACH ROW BEGIN {trigger['body']} END;"
                    logging.info(f"Trigger '{trigger['name']}' wird erstellt.")
                    logging.debug(f"SQL: {sql}")
                    cursor.execute(sql)

            for view in self.schema["database"]["views"]:
                sql = f"CREATE VIEW IF NOT EXISTS {view['name']} AS {view['definition']}"
                logging.info(f"View '{view['name']}' wird erstellt.")
                logging.debug(f"SQL: {sql}")
                cursor.execute(sql)

            conn.commit()
            logging.info("Datenbank erfolgreich erstellt.")

    def _is_consistent(self):
        logging.info("Prüfe Konsistenz der Datenbank.")
        if not os.path.exists(self.db_name):
            logging.warning("Datenbank-Datei existiert nicht.")
            return False

        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                for table in self.schema["database"]["tables"]:
                    cursor.execute(f"SELECT 1 FROM {table['name']} LIMIT 1;")
                for view in self.schema["database"]["views"]:
                    cursor.execute(f"SELECT 1 FROM {view['name']} LIMIT 1;")
            except sqlite3.Error as e:
                logging.error(f"Konsistenzprüfung fehlgeschlagen: {e}")
                return False

        logging.info("Datenbank ist konsistent.")
        return True

    def _connect(self):
        if not self.connection:
            logging.info("Stelle Verbindung zur Datenbank her.")
            self.connection = sqlite3.connect(self.db_name)
        return self.connection

    def initialize(self):
        logging.info("Initialisiere die Datenbank.")
        if not self._is_consistent():
            logging.warning("Die Datenbank ist inkonsistent. Sie wird neu erstellt.")
            self._create_database()

    def insert_stromzaehler(self, stromZaehlerNR, zeitpunkt, stromZaehlerStand):
        try:
            if not isinstance(stromZaehlerStand, float):
                raise ValueError("Ungültiger Zählerstand. Der Wert muss ein Float sein.")

            stromzaehler_str = str(stromZaehlerStand)
            if '.' not in stromzaehler_str or len(stromzaehler_str.split('.')[1]) != 1:
                raise ValueError("Der Stromzählerstand muss genau 1 Nachkommastelle haben.")

            if len(stromzaehler_str.replace('.', '')) != 7:
                raise ValueError("Der Stromzählerstand muss genau 7 Ziffern (inkl. 1 Nachkommastelle) haben.")
            
            if stromZaehlerStand < 0:
                raise ValueError("Der Zählerstand darf nicht negativ sein.")

            logging.info(f"Füge Stromzähler-Daten ein: NR={stromZaehlerNR}, Zeitpunkt={zeitpunkt}, Stand={stromZaehlerStand}.")
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO StromZaehler (stromZaehlerNR, zeitpunkt, stromZaehlerStand)
                    VALUES (?, ?, ?);""",
                    (stromZaehlerNR, zeitpunkt, stromZaehlerStand),
                )
                conn.commit()
        except sqlite3.IntegrityError as e:
            logging.error(f"Fehler beim Einfügen in die Datenbank: {e}")
            if "RAISE(ABORT" in str(e):
                raise ValueError(f"Ungültige Eingabe für Stromzählerstand: {e}")
            else:
                raise

    def insert_gaszaehler(self, gasZaehlerNR, zeitpunkt, gasZaehlerStand):
        try:
            if not isinstance(gasZaehlerStand, float):
                raise ValueError("Ungültiger Zählerstand. Der Wert muss ein Float sein.")

            gaszaehler_str = str(gasZaehlerStand)
            if '.' not in gaszaehler_str or len(gaszaehler_str.split('.')[1]) != 3:
                raise ValueError("Der Gaszählerstand muss genau 3 Nachkommastellen haben.")

            if len(gaszaehler_str.replace('.', '')) != 8:
                raise ValueError("Der Gaszählerstand muss genau 8 Ziffern (inkl. 3 Nachkommastellen) haben.")
            
            if gasZaehlerStand < 0:
                raise ValueError("Der Zählerstand darf nicht negativ sein.")

            logging.info(f"Füge Gaszähler-Daten ein: NR={gasZaehlerNR}, Zeitpunkt={zeitpunkt}, Stand={gasZaehlerStand}.")
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO Gaszaehler (gasZaehlerNR, zeitpunkt, gasZaehlerStand)
                    VALUES (?, ?, ?);""",
                    (gasZaehlerNR, zeitpunkt, gasZaehlerStand),
                )
                conn.commit()
        except sqlite3.IntegrityError as e:
            logging.error(f"Fehler beim Einfügen in die Datenbank: {e}")
            if "RAISE(ABORT" in str(e):
                raise ValueError(f"Ungültige Eingabe für Gaszählerstand: {e}")
            else:
                raise

    def get_stromzaehler_id_last_view(self):
        logging.info("Abfrage: Stromzähler letzter Stand je Zähler.")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stromzaehler_id_last_view;")
            return cursor.fetchall()

    def get_stromzaehler_id_view(self, stromZaehlerNR):
        logging.info(f"Abfrage: Alle Daten für StromzählerNR={stromZaehlerNR}.")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stromzaehler_id_view WHERE stromZaehlerNR = ?;", (stromZaehlerNR,))
            return cursor.fetchall()

    def get_stromzaehler_view(self):
        logging.info("Abfrage: Alle Daten aus der Stromzähler-Tabelle.")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stromzaehler_view;")
            return cursor.fetchall()

    def get_gaszaehler_id_last_view(self):
        logging.info("Abfrage: Gaszähler letzter Stand je Zähler.")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gaszaehler_id_last_view;")
            return cursor.fetchall()

    def get_gaszaehler_id_view(self, gasZaehlerNR):
        logging.info(f"Abfrage: Alle Daten für GaszählerNR={gasZaehlerNR}.")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gaszaehler_id_view WHERE gasZaehlerNR = ?;", (gasZaehlerNR,))
            return cursor.fetchall()

    def get_gaszaehler_view(self):
        logging.info("Abfrage: Alle Daten aus der Gaszähler-Tabelle.")
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gaszaehler_view;")
            return cursor.fetchall()

if __name__ == "__main__":
    # Exploratives Testen
    db = Datenbank()
    db.initialize()

    while True:
        try:
            zaehlernummer_strom = "D3-XX XXXXX"
            zeitpunkt_strom = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            stromzaehlerstand = float(input("Strom-Zählerstand eingeben: "))
            
            if stromzaehlerstand < 0:
                raise ValueError("Der Zählerstand darf nicht negativ sein.")
            
            db.insert_stromzaehler(zaehlernummer_strom, zeitpunkt_strom, stromzaehlerstand)
            logging.info(f"Strom-Zählerstand erfolgreich in die Datenbank geschrieben: {stromzaehlerstand}")

            zaehlernummer_gas = "X XXXXX XXXX XXXX"
            zeitpunkt_gas = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            gaszaehlerstand = float(input("Gas-Zählerstand eingeben: "))

            if gaszaehlerstand < 0:
                raise ValueError("Der Zählerstand darf nicht negativ sein.")

            db.insert_gaszaehler(zaehlernummer_gas, zeitpunkt_gas, gaszaehlerstand)
            logging.info(f"Gas-Zählerstand erfolgreich in die Datenbank geschrieben: {gaszaehlerstand}")

        except ValueError as e:
            logging.warning(f"Ungültige Eingabe: {e}. Bitte erneut versuchen.")
        
        except KeyboardInterrupt:
            logging.info("Datenaufnahme abgebrochen. Programm wird beendet.")
            break