import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from tkinter import messagebox
import tkinter as tk

from flowmeter.gui.datadisplay import DataDisplayGUI
from flowmeter.gui.providersettings import ProviderSettingsGUI
from flowmeter.gui.electricitymeter import ElectricityMeterGUI
from flowmeter.gui.gasmeter import GasMeterGUI

from flowmeter.logic.meters import ElectricityMeter, GasMeter


class FlowMeterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FlowMeter Menü")
        self.root.geometry("400x350")
        self.root.configure(bg="black")
        self.root.resizable(False, False)
        self.current_window = None
        self.create_main_menu()

    def create_main_menu(self):
        title_label = tk.Label(self.root, text="FlowMeter", font=("Arial", 18), fg="white", bg="black")
        title_label.pack(pady=20)

        gas_button = tk.Button(
            self.root, text="Gas-Zählerstand eingeben", font=("Arial", 12), width=25,
            command=self.open_gas_meter_gui
        )
        gas_button.pack(pady=5)

        show_gas_button = tk.Button(
            self.root, text="Gasdaten anzeigen", font=("Arial", 12), width=25,
            command=self.show_gas_data
        )
        show_gas_button.pack(pady=5)        

        electricity_button = tk.Button(
            self.root, text="Strom-Zählerstand eingeben", font=("Arial", 12), width=25,
            command=self.open_electricity_meter_gui
        )
        electricity_button.pack(pady=5)

        show_electricity_button = tk.Button(
            self.root, text="Stromdaten anzeigen", font=("Arial", 12), width=25,
            command=self.show_electricity_data
        )
        show_electricity_button.pack(pady=5)

        provider_button = tk.Button(
            self.root, text="Energieversorger einstellen", font=("Arial", 12), width=25,
            command=self.open_provider_settings_gui
        )
        provider_button.pack(pady=5)

        reset_button = tk.Button(
            self.root, text="Alles zurücksetzen", font=("Arial", 12), width=25,
            command=self.reset_all_data
        )
        reset_button.pack(pady=5)

        exit_button = tk.Button(
            self.root, text="Beenden", font=("Arial", 12), width=25,
            command=self.root.quit
        )
        exit_button.pack(pady=5)

    def close_current_window(self):
        if self.current_window and self.current_window.winfo_exists():
            self.current_window.destroy()
        self.current_window = None

    def open_gas_meter_gui(self):
        self.open_sub_window("Gas-Zählerstand eingeben", GasMeterGUI)

    def open_electricity_meter_gui(self):
        self.open_sub_window("Strom-Zählerstand eingeben", ElectricityMeterGUI)

    def open_sub_window(self, title, gui_class):
        self.close_current_window()
        self.current_window = tk.Toplevel(self.root)
        self.current_window.title(title)
        self.current_window.configure(bg="black")
        self.current_window.resizable(True, True)
        gui_class(self.current_window)

    def reset_all_data(self):
        confirm = tk.messagebox.askyesno("Bestätigung", "Wirklich alles zurücksetzen?")
        if confirm:
            electricity_meter = ElectricityMeter()
            electricity_meter.reset_all_data()
            tk.messagebox.showinfo("Erledigt!", "Alle Daten wurden erfolgreich zurückgesetzt!")

    def show_gas_data(self):
        try:
            gas_meter = GasMeter()
            records = gas_meter.get_all_records()
            if not records:
                tk.messagebox.showinfo("Gasdaten", "Keine Daten verfügbar.")
                return
            self.open_data_display_window("Gasdaten anzeigen", records, self.delete_gas_entry)
        except Exception as e:
            tk.messagebox.showerror("Fehler", f"Fehler beim Abrufen der Gasdaten: {str(e)}")

    def show_electricity_data(self):
        try:
            electricity_meter = ElectricityMeter()
            records = electricity_meter.get_all_records()
            if not records:
                tk.messagebox.showinfo("Stromdaten", "Keine Daten verfügbar.")
                return
            self.open_data_display_window("Stromdaten anzeigen", records, self.delete_electricity_entry)
        except Exception as e:
            tk.messagebox.showerror("Fehler", f"Fehler beim Abrufen der Stromdaten: {str(e)}")

    def open_data_display_window(self, title, data, delete_callback):
        self.close_current_window()
        self.current_window = tk.Toplevel(self.root)
        DataDisplayGUI(self.current_window, title, data, delete_callback)

    def delete_gas_entry(self, record_id):
        try:
            gas_meter = GasMeter()
            gas_meter.delete_record(record_id)
            tk.messagebox.showinfo("Erfolg", f"Eintrag mit ID {record_id} wurde gelöscht.")
        except Exception as e:
            tk.messagebox.showerror("Fehler", f"Fehler beim Löschen des Eintrags: {str(e)}")

    def delete_electricity_entry(self, record_id):
        try:
            electricity_meter = ElectricityMeter()
            electricity_meter.delete_record(record_id)
            tk.messagebox.showinfo("Erfolg", f"Eintrag mit ID {record_id} wurde gelöscht.")
        except Exception as e:
            tk.messagebox.showerror("Fehler", f"Fehler beim Löschen des Eintrags: {str(e)}")

    def open_provider_settings_gui(self):
        self.open_sub_window("Energieversorger einstellen", ProviderSettingsGUI)


if __name__ == "__main__":
    root = tk.Tk()
    app = FlowMeterGUI(root)
    root.mainloop()