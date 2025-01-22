class Stromzaehler:
    """
    Klasse zur Verwaltung der Stromzählerstände.

    User Story: US1_Strom_erfassen
    """
    
    def __init__(self, zaehlerstand_text_pfad = "data/zaehlerstand.txt"):
        self.stand = 0.0
        self.zaehlerstand_text_pfad = zaehlerstand_text_pfad

    def erfasse_zaehlerstand(self, stand):
        """ 
        Überprüfung er Eingabe und Eintragung des Zählerstands 
        User Story: US1_Strom_erfassen
        """
        if isinstance(stand, int):
            stand = float(stand)
        
        if not isinstance(stand, float):
            raise ValueError("Der Zählerstand muss ein Float sein.")
        
        if stand < 0:
            raise ValueError("Der Zählerstand darf nicht negativ sein.")
        
        stand = round(stand, 1)
        self.validiere_zaehlerstand(stand)
        self.stand = stand
        self.speichere_zaehlerstand()

    def anzahl_stellen_mit_dezimalstellen(self, zahl):
        """ 
        Gibt die Anzahl der Ziffern einer Zahl zurück, ohne das Vorzeichen oder den Dezimalpunkt zu berücksichtigen. 
        User Story: US1_Strom_erfassen
        """
        return len(str(zahl).replace('.', '').replace('-', ''))
    
    def validiere_zaehlerstand(self, stand):
        """ 
        Prüft die korrekte Anzahl der Stellen (7 Stellen inkl. Nachkommastelle) 
        User Story: US1_Strom_erfassen
        """
        stand_str = str(stand)
        if '.' not in stand_str:
            raise ValueError("Der Zählerstand muss genau eine Nachkommastelle haben.")
        
        teile = stand_str.split('.')
        if len(teile[1]) != 1:
            raise ValueError("Der Zählerstand muss genau eine Nachkommastelle haben.")
        
        if len(teile[0] + teile[1]) != 7:
            raise ValueError("Der Zählerstand muss insgesamt 7 Stellen haben.")
        
    def speichere_zaehlerstand(self):
            """ 
            Speichert den aktuellen Zählerstand in einer Textdatei. 
            User Story: US1_Strom_erfassen
            """
            with open(self.zaehlerstand_text_pfad, "a") as file:
                file.write(f"Zähler:{self.stand}\n")


if __name__ == "__main__":
    zaehler = Stromzaehler()
    try:
        zaehler.erfasse_zaehlerstand(float(input("Zählerstand eingeben")))
        print(f"Zählerstand erfolgreich erfasst: {zaehler.stand}")
    except ValueError as e:
        print(f"Fehler: {e}")