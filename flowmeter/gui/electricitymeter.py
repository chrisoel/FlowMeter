from flowmeter.logic.meters import ElectricityMeter
import tkinter as tk
from flowmeter.gui.rotatingcounter import RotatingCounter
from tkinter import messagebox

class ElectricityMeterGUI:
    def __init__(self, root):
        self.root = root
        self.electricity_meter = ElectricityMeter()
        self.electricity_meter_list = []
        self.create_meter()

    def create_meter(self):
        tk.Label(self.root, text="Strom-Zählerstand eingeben", font=("Arial", 18), fg="white", bg="black").pack(pady=20)
        placeholder = tk.Frame(self.root, width=490, height=20, bg="black")
        placeholder.pack()

        try:
            last_record = self.electricity_meter.get_last_record()
            if isinstance(last_record, float):
                last_record_str = f"{last_record:.1f}"
            else:
                last_record_str = "00000.000"
        except Exception:
            last_record_str = "00000.000"

        electricity_values = list(map(int, last_record_str.replace(".", "").zfill(7)))
        for i, value in enumerate(electricity_values):
            highlight = i == 6
            counter = RotatingCounter(self.root, 50 + i * 60, 100, initial_value=value, highlight=highlight)
            self.electricity_meter_list.append(counter)

        tk.Label(self.root, bg="black").pack(pady=80)

        save_button = tk.Button(self.root, text="Speichern", font=("Arial", 12), command=self.save_values)
        save_button.pack(pady=5)

        reset_button = tk.Button(self.root, text="Zurücksetzen", font=("Arial", 12), command=self.reset_to_last)
        reset_button.pack(pady=5)

    def save_values(self):
        electricity_values = [counter.get_value() for counter in self.electricity_meter_list]
        electricity_number_str = "".join(map(str, electricity_values))

        try:
            electricity_number = float(electricity_number_str[:-1] + "." + electricity_number_str[-1])
            self.electricity_meter.record_reading(electricity_number)
            tk.messagebox.showinfo("Erfolg!", "Strom-Zählerstand gespeichert!")
        except ValueError:
            tk.messagebox.showerror("Fehler", "Ungültiger Zählerstand. Überprüfen Sie die Eingabe.")
        except Exception:
            tk.messagebox.showerror("Fehler", "Ein unerwarteter Fehler ist aufgetreten.")

    def reset_to_last(self):
        try:
            last_record = self.electricity_meter.get_last_record()
            if isinstance(last_record, float):
                last_record_str = f"{last_record:.1f}"
            else:
                last_record_str = "00000.000"
        except Exception:
            last_record_str = "00000.000"

        electricity_values = list(map(int, last_record_str.replace(".", "").zfill(7)))
        for counter, value in zip(self.electricity_meter_list, electricity_values):
            counter.set_value(value)