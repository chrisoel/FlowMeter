import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar
from flowmeter.logic import EnergyProvider
import os


class ProviderSettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Energieversorger einstellen")
        self.root.geometry("290x700")
        self.root.configure(bg="black")
        self.root.resizable(False, False) 
        self.provider = EnergyProvider(database=None)

        container = ttk.Frame(self.root)
        canvas = tk.Canvas(container, bg="black", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        container.pack(fill="both", expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.create_provider_settings()

    def create_provider_settings(self):
        tk.Label(self.scrollable_frame, text="Energieversorger einstellen", font=("Arial", 16), fg="white", bg="black").pack(pady=10)

        tk.Label(self.scrollable_frame, text="Strom Vertrag", font=("Arial", 14), fg="white", bg="black").pack(pady=5)
        tk.Label(self.scrollable_frame, text="Vertragsstart:", fg="white", bg="black").pack()
        self.electricity_calendar = Calendar(self.scrollable_frame, selectmode="day", date_pattern="yyyy-MM-dd")
        self.electricity_calendar.pack(pady=5)
        tk.Label(self.scrollable_frame, text="Jährliche Energie (kWh):", fg="white", bg="black").pack()
        self.electricity_annual_energy = tk.Entry(self.scrollable_frame, width=30)
        self.electricity_annual_energy.pack(pady=5)

        tk.Label(self.scrollable_frame, text="Gas Vertrag", font=("Arial", 14), fg="white", bg="black").pack(pady=10)
        tk.Label(self.scrollable_frame, text="Vertragsstart:", fg="white", bg="black").pack()
        self.gas_calendar = Calendar(self.scrollable_frame, selectmode="day", date_pattern="yyyy-MM-dd")
        self.gas_calendar.pack(pady=5)
        tk.Label(self.scrollable_frame, text="Jährliche Energie (kWh):", fg="white", bg="black").pack()
        self.gas_annual_energy = tk.Entry(self.scrollable_frame, width=30)
        self.gas_annual_energy.pack(pady=5)

        save_button = tk.Button(self.scrollable_frame, text="Speichern", font=("Arial", 12), command=self.save_provider_settings)
        save_button.pack(pady=10)
        close_button = tk.Button(self.scrollable_frame, text="Schließen", font=("Arial", 12), command=self.root.destroy)
        close_button.pack(pady=5)


    def save_provider_settings(self):
        try:
            electricity_start_date = self.electricity_calendar.get_date()
            gas_start_date = self.gas_calendar.get_date()
            electricity_annual_energy = self.electricity_annual_energy.get()
            gas_annual_energy = self.gas_annual_energy.get()

            if not electricity_annual_energy.isdigit():
                raise ValueError("Die jährliche Energie für Strom muss eine ganze Zahl sein.")
            if not gas_annual_energy.isdigit():
                raise ValueError("Die jährliche Energie für Gas muss eine ganze Zahl sein.")

            self.provider.add_provider("electricity", int(electricity_annual_energy), electricity_start_date)
            self.provider.add_provider("gas", int(gas_annual_energy), gas_start_date)

            tk.messagebox.showinfo("Erfolg", "Einstellungen wurden erfolgreich gespeichert!")
        except ValueError as e:
            tk.messagebox.showerror("Fehler", str(e))
        except Exception as e:
            tk.messagebox.showerror("Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {str(e)}")