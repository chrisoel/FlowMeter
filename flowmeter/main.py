class BasisZaehler:
    """
    Basisklasse zur Verwaltung von Zählerständen.

    Unterstützte User Stories:
    - US1_Strom_erfassen
    - US2_Gas_erfassen
    - US3_Stromzählernummer
    - US4_Gaszählernummer
    """

    def __init__(self, zaehlerstand_text_pfad, zaehlernummer, dezimalstellen, gesamtlänge):
        self.stand = 0.0
        self.zaehlerstand_text_pfad = zaehlerstand_text_pfad
        self.zaehlernummer = zaehlernummer
        self.dezimalstellen = dezimalstellen
        self.gesamtlänge = gesamtlänge

    def erfasse_zaehlerstand(self, stand):
        """
        Überprüfung der Eingabe und Eintragung des Zählerstands.

        Unterstützte User Stories:
        - US1_Strom_erfassen
        - US2_Gas_erfassen
        """
        if isinstance(stand, int):
            stand = float(stand)
        
        if not isinstance(stand, float):
            raise ValueError("Der Zählerstand muss ein Float sein.")
        
        if stand < 0:
            raise ValueError("Der Zählerstand darf nicht negativ sein.")
        
        stand = round(stand, self.dezimalstellen)
        self.validiere_zaehlerstand(stand)
        self.stand = stand
        self.speichere_zaehlerstand()

    def validiere_zaehlerstand(self, stand):
        """
        Prüft die korrekte Anzahl der Stellen inkl. Nachkommastellen.

        Unterstützte User Stories:
        - US1_Strom_erfassen
        - US2_Gas_erfassen
        """
        stand_str = f"{stand:.{self.dezimalstellen}f}"
        if '.' not in stand_str:
            raise ValueError(f"Der Zählerstand muss genau {self.dezimalstellen} Nachkommastellen haben.")
        
        teile = stand_str.split('.')
        if len(teile[1]) != self.dezimalstellen:
            raise ValueError(f"Der Zählerstand muss genau {self.dezimalstellen} Nachkommastellen haben.")
        
        if len(teile[0] + teile[1]) != self.gesamtlänge:
            raise ValueError(f"Der Zählerstand muss insgesamt {self.gesamtlänge} Stellen haben.")

    def speichere_zaehlerstand(self):
        """
        Speichert den aktuellen Zählerstand in einer Textdatei.

        Unterstützte User Stories:
        - US1_Strom_erfassen
        - US2_Gas_erfassen
        - US3_Stromzählernummer
        - US4_Gaszählernummer
        """
        with open(self.zaehlerstand_text_pfad, "a") as file:
            file.write(f"{self.zaehlernummer}: {self.stand:.{self.dezimalstellen}f}\n")

class Stromzaehler(BasisZaehler):
    """
    Klasse zur Verwaltung der Stromzählerstände.

    Unterstützte User Stories:
    - US1_Strom_erfassen
    - US3_Stromzählernummer
    """
    def __init__(self, zaehlerstand_text_pfad="data/stromzaehler.txt", zaehlernummer="D3-XX XXXXX"):
        super().__init__(zaehlerstand_text_pfad, zaehlernummer, dezimalstellen=1, gesamtlänge=7)

class Gaszaehler(BasisZaehler):
    """
    Klasse zur Verwaltung der Gaszählerstände.

    Unterstützte User Stories:
    - US2_Gas_erfassen
    - US4_Gaszählernummer
    """
    def __init__(self, zaehlerstand_text_pfad="data/gaszaehler.txt", zaehlernummer="X XXXXX XXXX XXXX"):
        super().__init__(zaehlerstand_text_pfad, zaehlernummer, dezimalstellen=3, gesamtlänge=8)

if __name__ == "__main__":
    strom_zaehler = Stromzaehler()
    gas_zaehler = Gaszaehler()

    try:
        strom_zaehler.erfasse_zaehlerstand(float(input("Strom-Zählerstand eingeben: ")))
        print(f"Strom-Zählerstand erfolgreich erfasst: {strom_zaehler.stand}")
    except ValueError as e:
        print(f"Fehler: {e}")

    try:
        gas_zaehler.erfasse_zaehlerstand(float(input("Gas-Zählerstand eingeben: ")))
        print(f"Gas-Zählerstand erfolgreich erfasst: {gas_zaehler.stand}")
    except ValueError as e:
        print(f"Fehler: {e}")