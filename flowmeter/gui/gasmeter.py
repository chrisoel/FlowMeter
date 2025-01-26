from flowmeter.logic.meters import GasMeter
import tkinter as tk
from flowmeter.gui.rotatingcounter import RotatingCounter
from tkinter import messagebox

class GasMeterGUI:
    def __init__(self, root):
        self.root = root
        self.gas_meter = GasMeter()
        self.gas_meter_list = []
        self.create_meter()

    def create_meter(self):
        tk.Label(self.root, text="Gas-Zählerstand eingeben", font=("Arial", 18), fg="white", bg="black").pack(pady=20)
        placeholder = tk.Frame(self.root, width=590, height=20, bg="black")
        placeholder.pack()

        try:
            last_record = self.gas_meter.get_last_record()
            if isinstance(last_record, float):
                last_record_str = f"{last_record:.3f}"
            else:
                last_record_str = "00000.000"
        except Exception:
            last_record_str = "00000.000"

        gas_values = list(map(int, last_record_str.replace(".", "").zfill(8)))
        for i, value in enumerate(gas_values):
            highlight = i >= 5
            counter = RotatingCounter(self.root, 50 + i * 60, 100, initial_value=value, highlight=highlight)
            self.gas_meter_list.append(counter)

        tk.Label(self.root, bg="black").pack(pady=80)

        save_button = tk.Button(self.root, text="Speichern", font=("Arial", 12), command=self.save_values)
        save_button.pack(pady=5)

        reset_button = tk.Button(self.root, text="Zurücksetzen", font=("Arial", 12), command=self.reset_to_last)
        reset_button.pack(pady=5)

    def save_values(self):
        gas_values = [counter.get_value() for counter in self.gas_meter_list]
        gas_number_str = "".join(map(str, gas_values))

        try:
            gas_number = float(gas_number_str[:-3] + "." + gas_number_str[-3:])
            self.gas_meter.record_reading(gas_number)
            tk.messagebox.showinfo("Erfolg!", "Gas-Zählerstand gespeichert!")
        except ValueError:
            tk.messagebox.showerror("Fehler", "Ungültiger Zählerstand. Überprüfen Sie die Eingabe.")
        except Exception:
            tk.messagebox.showerror("Fehler", "Ein unerwarteter Fehler ist aufgetreten.")

    def reset_to_last(self):
        try:
            last_record = self.gas_meter.get_last_record()
            if isinstance(last_record, float):
                last_record_str = f"{last_record:.3f}"
            else:
                last_record_str = "00000.000"
        except Exception:
            last_record_str = "00000.000"

        gas_values = list(map(int, last_record_str.replace(".", "").zfill(8)))
        for counter, value in zip(self.gas_meter_list, gas_values):
            counter.set_value(value)