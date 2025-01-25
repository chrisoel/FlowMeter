import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from datetime import datetime
import logging
from flowmeter.datenbank import Datenbank

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class BasisZaehler:
    def __init__(self, zaehlernummer, dezimalstellen, gesamtlänge, db: Datenbank):
        self.stand = 0.0
        self.zaehlernummer = zaehlernummer
        self.dezimalstellen = dezimalstellen
        self.gesamtlänge = gesamtlänge
        self.db = db
        logging.info(f"BasisZaehler initialisiert: {self.zaehlernummer}")

    def erfasse_zaehlerstand(self, stand):
        logging.info(f"Erfasse Zählerstand: {stand}")
        if isinstance(stand, int):
            stand = float(stand)
        if not isinstance(stand, float):
            logging.error("Der Zählerstand muss ein Float sein.")
            raise ValueError("Der Zählerstand muss ein Float sein.")
        if stand < 0:
            logging.error("Der Zählerstand darf nicht negativ sein.")
            raise ValueError("Der Zählerstand darf nicht negativ sein.")

        self.validiere_zaehlerstand(stand)
        self.stand = stand
        logging.info(f"Zählerstand erfolgreich validiert und gesetzt: {self.stand}")
        self.speichere_zaehlerstand()

    def validiere_zaehlerstand(self, stand):
        logging.info(f"Validiere Zählerstand: {stand}")
        stand_str = str(stand)

        if '.' not in stand_str:
            logging.error("Der Zählerstand muss Nachkommastellen haben.")
            raise ValueError(f"Der Zählerstand muss genau {self.dezimalstellen} Nachkommastellen haben.")

        vor_komma, nach_komma = stand_str.split('.')

        if len(vor_komma + nach_komma) != self.gesamtlänge:
            logging.error("Falsche Gesamtlänge des Zählerstands.")
            raise ValueError(f"Der Zählerstand muss insgesamt {self.gesamtlänge} Stellen haben.")

        if len(nach_komma) != self.dezimalstellen:
            logging.error("Falsche Anzahl an Nachkommastellen.")
            raise ValueError(f"Der Zählerstand muss genau {self.dezimalstellen} Nachkommastellen haben.")

        logging.info("Zählerstand erfolgreich validiert.")

    def speichere_zaehlerstand(self):
        logging.info("Speichere Zählerstand in die Datenbank.")
        zeitstempel = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            if isinstance(self, Stromzaehler):
                self.db.insert_stromzaehler(self.zaehlernummer, zeitstempel, self.stand)
            elif isinstance(self, Gaszaehler):
                self.db.insert_gaszaehler(self.zaehlernummer, zeitstempel, self.stand)
            logging.info("Zählerstand erfolgreich in die Datenbank gespeichert.")
        except Exception as e:
            logging.error(f"Fehler beim Speichern des Zählerstands in die Datenbank: {e}")
            raise

    def get_letzter_stand(self):
        logging.info(f"Rufe letzten Stand für Zählernummer {self.zaehlernummer} ab.")
        try:
            if isinstance(self, Stromzaehler):
                return self.db.get_stromzaehler_id_last_view()
            elif isinstance(self, Gaszaehler):
                return self.db.get_gaszaehler_id_last_view()
        except Exception as e:
            logging.error(f"Fehler beim Abrufen des letzten Stands: {e}")
            raise

    def get_alle_stände(self):
        logging.info(f"Rufe alle Stände für Zählernummer {self.zaehlernummer} ab.")
        try:
            if isinstance(self, Stromzaehler):
                return self.db.get_stromzaehler_view()
            elif isinstance(self, Gaszaehler):
                return self.db.get_gaszaehler_view()
        except Exception as e:
            logging.error(f"Fehler beim Abrufen aller Stände: {e}")
            raise

class Stromzaehler(BasisZaehler):
    def __init__(self, zaehlernummer="D3-XX XXXXX", db=None):
        if db is None:
            db = Datenbank()
            db.initialize()
        super().__init__(zaehlernummer, dezimalstellen=1, gesamtlänge=7, db=db)
        logging.info(f"Stromzaehler initialisiert: {self.zaehlernummer}")

class Gaszaehler(BasisZaehler):
    def __init__(self, zaehlernummer="X XXXXX XXXX XXXX", db=None):
        if db is None:
            db = Datenbank()
            db.initialize()
        super().__init__(zaehlernummer, dezimalstellen=3, gesamtlänge=8, db=db)
        logging.info(f"Gaszaehler initialisiert: {self.zaehlernummer}")

if __name__ == "__main__":
    # Exploratives Testen
    strom_zaehler = Stromzaehler()
    gas_zaehler = Gaszaehler()

    while True:
        try:
            strom_zaehler.erfasse_zaehlerstand(float(input("Strom-Zählerstand eingeben: ")))
            logging.info(f"Strom-Zählerstand erfolgreich erfasst: {strom_zaehler.stand}")
            logging.info("Letzter Stand:")
            logging.info(strom_zaehler.get_letzter_stand())
            logging.info("Alle Stände:")
            logging.info(strom_zaehler.get_alle_stände())
            break
        except ValueError as e:
            logging.warning(f"Fehler: {e}. Bitte erneut eingeben.")
        except KeyboardInterrupt:
            logging.info("Eingabe abgebrochen. Programm wird beendet.")
            break

    while True:
        try:
            gas_zaehler.erfasse_zaehlerstand(float(input("Gas-Zählerstand eingeben: ")))
            logging.info(f"Gas-Zählerstand erfolgreich erfasst: {gas_zaehler.stand}")
            logging.info("Letzter Stand:")
            logging.info(gas_zaehler.get_letzter_stand())
            logging.info("Alle Stände:")
            logging.info(gas_zaehler.get_alle_stände())
            break
        except ValueError as e:
            logging.warning(f"Fehler: {e}. Bitte erneut eingeben.")
        except KeyboardInterrupt:
            logging.info("Eingabe abgebrochen. Programm wird beendet.")
            break