import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from flowmeter.logic import ElectricityMeter, GasMeter
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class DataDisplayGUI:
    def __init__(self, root, title, data, delete_callback=None):
        self.root = root
        self.root.title(title)
        self.root.geometry("700x400")
        self.root.configure(bg="black")
        self.data = data
        self.delete_callback = delete_callback
        self.create_table()

    def create_table(self):
        tk.Label(self.root, text="Datenanzeige", font=("Arial", 18), fg="white", bg="black").pack(pady=10)
        table_frame = tk.Frame(self.root, bg="black")
        table_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("ID", "Datum", "Wert")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Datum", text="Datum")
        self.tree.heading("Wert", text="Wert")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for record in self.data:
            self.tree.insert("", tk.END, values=record)

        button_frame = tk.Frame(self.root, bg="black")
        button_frame.pack(fill=tk.X, pady=10)
        delete_button = tk.Button(
            button_frame,
            text="Ausgewählten Eintrag löschen",
            font=("Arial", 12),
            command=self.delete_selected_entry
        )
        delete_button.pack(side=tk.LEFT, padx=5)

        close_button = tk.Button(
            button_frame,
            text="Schließen",
            font=("Arial", 12),
            command=self.root.destroy
        )
        close_button.pack(side=tk.LEFT, padx=5)

    def delete_selected_entry(self):
        selected_item = self.tree.selection()
        if not selected_item:
            tk.messagebox.showwarning("Warnung", "Bitte wählen Sie einen Eintrag aus, um ihn zu löschen.")
            return

        confirm = tk.messagebox.askyesno("Bestätigung", "Möchten Sie diesen Eintrag wirklich löschen?")
        if confirm:
            for item in selected_item:
                record = self.tree.item(item, "values")
                record_id = record[0]
                self.tree.delete(item)

                if self.delete_callback:
                    self.delete_callback(record_id)

class RotatingCounter:
    def __init__(self, root, x, y, initial_value=0, highlight=False):
        self.canvas = tk.Canvas(root, width=50, height=150, bg="black", highlightthickness=2)
        self.canvas.place(x=x, y=y)
        self.canvas.config(highlightbackground="red" if highlight else "black")
        self.current_value = initial_value
        self.render_counter()
        self.canvas.bind("<Button-1>", self.scroll_up)
        self.canvas.bind("<Button-3>", self.scroll_down)

    def render_counter(self):
        self.canvas.delete("all")
        self.canvas.create_text(25, 25, text=(self.current_value - 1) % 10, fill="gray", font=("Arial", 24))
        self.canvas.create_text(25, 75, text=self.current_value, fill="white", font=("Arial", 32))
        self.canvas.create_text(25, 125, text=(self.current_value + 1) % 10, fill="gray", font=("Arial", 24))

    def scroll_up(self, event=None):
        self.current_value = (self.current_value + 1) % 10
        self.render_counter()

    def scroll_down(self, event=None):
        self.current_value = (self.current_value - 1) % 10
        self.render_counter()

    def set_value(self, value):
        self.current_value = value
        self.render_counter()

    def get_value(self):
        return self.current_value


class FlowMeterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FlowMeter Menü")
        self.root.geometry("400x300")
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


if __name__ == "__main__":
    root = tk.Tk()
    app = FlowMeterGUI(root)
    root.mainloop()