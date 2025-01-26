import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from flowmeter.logic import EnergyProvider
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import tkinter as tk
from tkinter import ttk


class DataDisplayGUI:
    def __init__(self, root, title, data, delete_callback=None):
        self.root = root
        self.root.title(title)
        self.root.geometry("900x600")
        self.root.configure(bg="black")
        self.data = data
        self.delete_callback = delete_callback
        self.plot_window = None

        # Instanz von EnergyProvider erstellen
        self.provider = EnergyProvider()

        # Lade Energieziele aus der Datenbank
        self.energy_targets = self.load_energy_targets()

        self.create_table()
        self.show_plot_window()
        self.bind_window_events()

    def load_energy_targets(self):
        """
        Lädt die Energieziele (monatliche Werte) für Strom und Gas aus der Datenbank.
        """
        try:
            electricity_provider = self.provider.get_provider("electricity")
            gas_provider = self.provider.get_provider("gas")

            electricity_target = (
                electricity_provider[2] / 12 if electricity_provider else None
            )  # Jährliche Energie durch 12 teilen
            gas_target = (
                gas_provider[2] / 12 if gas_provider else None
            )  # Jährliche Energie durch 12 teilen

            return {"electricity": electricity_target, "gas": gas_target}
        except Exception as e:
            print(f"Fehler beim Laden der Energieziele: {str(e)}")
            return {"electricity": None, "gas": None}

    def create_table(self):
        tk.Label(self.root, text="Datenanzeige", font=("Arial", 18), fg="white", bg="black").pack(pady=10)
        table_frame = tk.Frame(self.root, bg="black")
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = ("ID", "Datum", "Wert")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
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

    def create_plot_window(self):
        self.plot_window = tk.Toplevel(self.root)
        self.plot_window.title("Datenverlauf")
        self.plot_window.geometry("700x500")
        self.plot_window.configure(bg="white")

        sorted_data = sorted(self.data, key=lambda x: x[1])
        timestamps = [record[1] for record in sorted_data]
        values = [record[2] for record in sorted_data]

        sns.set_theme(style="darkgrid")
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

        sns.lineplot(x=timestamps, y=values, ax=ax, marker="o", color="blue", linewidth=2.5, label="Verbrauchsdaten")

        # Ziel-Linien für Strom und Gas einfügen
        if self.energy_targets["electricity"]:
            ax.axhline(y=self.energy_targets["electricity"], color="green", linestyle="--", label="Ziel (Strom)")
        if self.energy_targets["gas"]:
            ax.axhline(y=self.energy_targets["gas"], color="red", linestyle="--", label="Ziel (Gas)")

        ax.set_title("Datenverlauf", fontsize=16, weight="bold", color="#333333")
        ax.set_xlabel("Zeit", fontsize=12, color="#555555")
        ax.set_ylabel("Wert", fontsize=12, color="#555555")
        ax.tick_params(axis="x", rotation=45, labelsize=10, colors="#333333")
        ax.tick_params(axis="y", labelsize=10, colors="#333333")
        ax.legend(fontsize=10)

        canvas = FigureCanvasTkAgg(fig, master=self.plot_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

        self.update_plot_window_position()

    def show_plot_window(self):
        if self.plot_window is None or not self.plot_window.winfo_exists():
            self.create_plot_window()
        else:
            self.plot_window.deiconify()

    def update_plot_window_position(self):
        self.root.update_idletasks()
        x = self.root.winfo_x() + self.root.winfo_width()
        y = self.root.winfo_y()
        self.plot_window.geometry(f"+{x}+{y}")

    def bind_window_events(self):
        self.root.bind("<Configure>", lambda event: self.update_plot_window_position())
        if self.plot_window:
            self.plot_window.protocol("WM_DELETE_WINDOW", lambda: self.plot_window.withdraw())

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
                self.data = [entry for entry in self.data if entry[0] != int(record_id)]

            if self.plot_window and self.plot_window.winfo_exists():
                self.plot_window.destroy()
                self.plot_window = None
            self.show_plot_window()