from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BasisZaehler:
    def __init__(self, zaehlerstand_text_pfad, zaehlernummer, dezimalstellen, gesamtlänge):
        self.stand = 0.0
        self.zaehlerstand_text_pfad = zaehlerstand_text_pfad
        self.zaehlernummer = zaehlernummer
        self.dezimalstellen = dezimalstellen
        self.gesamtlänge = gesamtlänge
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

        stand = round(stand, self.dezimalstellen)
        self.validiere_zaehlerstand(stand)
        self.stand = stand
        logging.info(f"Zählerstand erfolgreich validiert und gesetzt: {self.stand}")
        self.speichere_zaehlerstand()

    def validiere_zaehlerstand(self, stand):
        logging.info(f"Validiere Zählerstand: {stand}")
        stand_str = f"{stand:.{self.dezimalstellen}f}"
        if '.' not in stand_str:
            logging.error("Der Zählerstand muss Nachkommastellen haben.")
            raise ValueError(f"Der Zählerstand muss genau {self.dezimalstellen} Nachkommastellen haben.")
        teile = stand_str.split('.')
        if len(teile[1]) != self.dezimalstellen:
            logging.error("Falsche Anzahl an Nachkommastellen.")
            raise ValueError(f"Der Zählerstand muss genau {self.dezimalstellen} Nachkommastellen haben.")
        if len(teile[0] + teile[1]) != self.gesamtlänge:
            logging.error("Falsche Gesamtlänge des Zählerstands.")
            raise ValueError(f"Der Zählerstand muss insgesamt {self.gesamtlänge} Stellen haben.")
        logging.info("Zählerstand erfolgreich validiert.")

    def speichere_zaehlerstand(self):
        logging.info("Speichere Zählerstand in Datei.")
        zeitstempel = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.zaehlerstand_text_pfad, "a") as file:
                file.write(f"{zeitstempel} | {self.zaehlernummer} | {self.stand:.{self.dezimalstellen}f}\n")
            logging.info("Zählerstand erfolgreich gespeichert.")
        except Exception as e:
            logging.error(f"Fehler beim Speichern des Zählerstands: {e}")
            raise

class Stromzaehler(BasisZaehler):
    def __init__(self, zaehlerstand_text_pfad="data/stromzaehler.txt", zaehlernummer="D3-XX XXXXX"):
        super().__init__(zaehlerstand_text_pfad, zaehlernummer, dezimalstellen=1, gesamtlänge=7)
        logging.info(f"Stromzaehler initialisiert: {self.zaehlernummer}")

class Gaszaehler(BasisZaehler):
    def __init__(self, zaehlerstand_text_pfad="data/gaszaehler.txt", zaehlernummer="X XXXXX XXXX XXXX"):
        super().__init__(zaehlerstand_text_pfad, zaehlernummer, dezimalstellen=3, gesamtlänge=8)
        logging.info(f"Gaszaehler initialisiert: {self.zaehlernummer}")

if __name__ == "__main__":
    strom_zaehler = Stromzaehler()
    gas_zaehler = Gaszaehler()

    while True:
        try:
            strom_zaehler.erfasse_zaehlerstand(float(input("Strom-Zählerstand eingeben: ")))
            logging.info(f"Strom-Zählerstand erfolgreich erfasst: {strom_zaehler.stand}")
            break
        except ValueError as e:
            logging.warning(f"Fehler: {e}. Bitte erneut eingeben.")

    while True:
        try:
            gas_zaehler.erfasse_zaehlerstand(float(input("Gas-Zählerstand eingeben: ")))
            logging.info(f"Gas-Zählerstand erfolgreich erfasst: {gas_zaehler.stand}")
            break
        except ValueError as e:
            logging.warning(f"Fehler: {e}. Bitte erneut eingeben.")