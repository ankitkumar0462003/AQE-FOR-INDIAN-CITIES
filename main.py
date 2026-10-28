"""Air Quality Explorer: simple Tkinter mini project. Run: python main.py"""
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from analysis import load_data, city_data, city_summary, month_averages, season_averages, SEASON_ORDER
from live_aqi import CITIES, get_live_aqi, aqi_category

# Simple dashboard colors: change these to customize the appearance.
NAVY = "#15233F"
BLUE = "#2864DC"
LIGHT = "#F3F6FB"
WHITE = "#FFFFFF"
TEXT = "#1B2B46"
GRAY = "#60718A"
GREEN = "#0F9B82"
ORANGE = "#EF9A36"

PROJECT_FOLDER = Path(__file__).resolve().parent
DEFAULT_CSV = PROJECT_FOLDER / "data" / "city_day.csv"


class AirQualityApp(tk.Tk):
    """One class keeps the window and its three pages together."""

    def __init__(self):
        super().__init__()
        self.title("Air Quality Explorer")
        self.geometry("1180x740")
        self.minsize(950, 650)
        self.configure(bg=LIGHT)
        self.data = pd.DataFrame()
        self.error_text = ""
        self.selected_city = tk.StringVar(value="Delhi")
        self.first_city = tk.StringVar(value="Delhi")
        self.second_city = tk.StringVar(value="Amritsar")
        self.live_city = tk.StringVar(value="Delhi")
        self.page_name = ""
        self.loading = False
        self.buttons = {}

        # Sidebar and central content are two ordinary Tkinter Frames.
        self.sidebar = tk.Frame(self, bg=NAVY, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.content = tk.Frame(self, bg=LIGHT)
        self.content.pack(side="left", fill="both", expand=True)

        tk.Label(self.sidebar, text="AIR QUALITY\nEXPLORER", bg=NAVY,
                 fg=WHITE, font=("Segoe UI", 20, "bold"), justify="left").pack(
            anchor="w", padx=22, pady=(34, 8))
        tk.Label(self.sidebar, text="Indian Cities  •  Python", bg=NAVY,
                 fg="#A4B9DA", font=("Segoe UI", 10)).pack(anchor="w", padx=22, pady=(0, 35))

        for name in ["Dashboard", "Compare Cities", "Live AQI"]:
            button = tk.Button(self.sidebar, text="   " + name, anchor="w",
                               font=("Segoe UI", 11, "bold"), relief="flat", bd=0,
                               bg=NAVY, fg="#D1DDF0", activeforeground=WHITE,
                               command=lambda page=name: self.show_page(page))
            button.pack(fill="x", padx=10, pady=5, ipady=12)
            self.buttons[name] = button

        tk.Label(self.sidebar, text="Historical: Indian AQI",
                 bg=NAVY, fg="#9FB1CA", justify="left",
                 font=("Segoe UI", 9)).pack(side="bottom", anchor="w", padx=22, pady=26)

        # If CSV is missing, the app still opens and explains what to do.
        try:
            self.data = load_data(DEFAULT_CSV)
        except (OSError, ValueError) as error:
            self.error_text = str(error)
        self.show_page("Dashboard")

    def heading(self, title, description):
        tk.Label(self.content, text=title, bg=LIGHT, fg=TEXT,
                 font=("Segoe UI", 24, "bold")).pack(anchor="w", padx=30, pady=(28, 4))
        tk.Label(self.content, text=description, bg=LIGHT, fg=GRAY,
                 font=("Segoe UI", 11)).pack(anchor="w", padx=30, pady=(0, 22))

    def panel(self, parent=None):
        """White frame used for controls, chart and info cards."""
        return tk.Frame(parent or self.content, bg=WHITE, padx=18, pady=16,
                        highlightbackground="#E0E8F2", highlightthickness=1)

    def button(self, parent, title, command):
        return tk.Button(parent, text=title, command=command, bg=BLUE, fg=WHITE,
                         activebackground="#1E4DA9", activeforeground=WHITE,
                         relief="flat", font=("Segoe UI", 10, "bold"), padx=15, pady=8,
                         cursor="hand2")

    def dropdown(self, parent, variable, choices, changed):
        item = ttk.Combobox(parent, textvariable=variable, values=choices,
                            state="readonly", width=19, font=("Segoe UI", 10))
        item.pack(side="left", padx=(9, 18))
        item.bind("<<ComboboxSelected>>", lambda event: changed())
        return item

    def info_card(self, parent, title, value, color=BLUE):
        frame = self.panel(parent)
        frame.pack(side="left", fill="both", expand=True, padx=(0, 11))
        tk.Label(frame, text=title, bg=WHITE, fg=GRAY,
                 font=("Segoe UI", 10)).pack(anchor="w")
        tk.Label(frame, text=value, bg=WHITE, fg=color,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(6, 0))

    def show_page(self, name):
        self.page_name = name
        for widget in self.content.winfo_children():
            widget.destroy()
        for page, button in self.buttons.items():
            button.configure(bg=BLUE if page == name else NAVY)
        if name == "Dashboard":
            self.dashboard()
        elif name == "Compare Cities":
            self.comparison()
        else:
            self.live_page()

    def import_csv(self):
        filename = filedialog.askopenfilename(
            title="Select the Kaggle city_day.csv", filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        try:
            self.data = load_data(filename)
            self.error_text = ""
            cities = sorted(self.data["City"].dropna().unique().tolist())
            if cities:
                self.selected_city.set("Delhi" if "Delhi" in cities else cities[0])
                self.first_city.set(self.selected_city.get())
                self.second_city.set(cities[1] if len(cities) > 1 else cities[0])
            self.show_page("Dashboard")
        except (OSError, ValueError, pd.errors.ParserError) as error:
            messagebox.showerror("CSV problem", str(error))

    def no_data(self):
        card = self.panel()
        card.pack(fill="x", padx=30, pady=12)
        tk.Label(card, text="Import your real historical CSV to see the charts.",
                 bg=WHITE, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(card, text="Download city_day.csv from Kaggle and click Import CSV.\n"
                 + self.error_text, justify="left", bg=WHITE, fg=GRAY,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=10)
        self.button(card, "Import CSV", self.import_csv).pack(anchor="w")

    def draw_figure(self, figure):
        card = self.panel()
        card.pack(fill="both", expand=True, padx=30, pady=(15, 18))
        canvas = FigureCanvasTkAgg(figure, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def dashboard(self):
        self.heading("Historical Dashboard", "Find seasonal patterns in Indian AQI (Kaggle CSV).")
        if self.data.empty:
            self.no_data()
            return
        cities = sorted(self.data["City"].dropna().unique())
        if self.selected_city.get() not in cities:
            self.selected_city.set(cities[0])
        controls = self.panel()
        controls.pack(fill="x", padx=30)
        tk.Label(controls, text="Choose city:", bg=WHITE, fg=TEXT).pack(side="left")
        self.dropdown(controls, self.selected_city, cities, self.dashboard_refresh)
        self.button(controls, "Import CSV", self.import_csv).pack(side="right")
        self.dashboard_refresh()

    def dashboard_refresh(self):
        # Only remove results; keep the heading and city dropdown.
        for widget in list(self.content.winfo_children())[3:]:
            widget.destroy()
        city = self.selected_city.get()
        avg, worst, season, count = city_summary(self.data, city)
        row = tk.Frame(self.content, bg=LIGHT)
        row.pack(fill="x", padx=(30, 19), pady=(18, 2))
        self.info_card(row, "Average Indian AQI", f"{avg:.0f}" if pd.notna(avg) else "N/A")
        self.info_card(row, "Worst recorded month", worst, ORANGE)
        self.info_card(row, "Worst season", season, GREEN)

        figure = Figure(figsize=(10, 4), dpi=90, facecolor=WHITE)
        ax1, ax2 = figure.subplots(1, 2)
        monthly = month_averages(self.data, city)
        ax1.plot(monthly.index, monthly.values, marker="o", color=BLUE, linewidth=2)
        ax1.set_title("Average AQI by calendar month")
        ax1.set_xlabel("Month (1 = Jan)")
        ax1.set_ylabel("Indian AQI")
        ax1.set_xticks(range(1, 13))
        ax1.grid(alpha=0.2)

        seasons = season_averages(self.data, city)
        ax2.bar(SEASON_ORDER, seasons.values, color=[BLUE, GREEN, "#54A4D2", ORANGE])
        ax2.set_title("Average AQI by season")
        ax2.set_ylabel("Indian AQI")
        ax2.tick_params(axis="x", labelrotation=18)
        figure.tight_layout(pad=2.5)
        self.draw_figure(figure)
        tk.Label(self.content, text=f"Based on {count:,} valid daily AQI readings. "
                 "Worst month requires 5+ readings. Historical AQI uses India's scale.",
                 bg=LIGHT, fg=GRAY, font=("Segoe UI", 9)).pack(
            anchor="w", padx=30, pady=(0, 15))

    def comparison(self):
        self.heading("Compare Cities", "Compare two cities using historical Indian AQI readings.")
        if self.data.empty:
            self.no_data()
            return
        cities = sorted(self.data["City"].dropna().unique())
        for variable in [self.first_city, self.second_city]:
            if variable.get() not in cities:
                variable.set(cities[0])
        control = self.panel()
        control.pack(fill="x", padx=30)
        tk.Label(control, text="City 1", bg=WHITE, fg=TEXT).pack(side="left")
        self.dropdown(control, self.first_city, cities, self.comparison_refresh)
        tk.Label(control, text="City 2", bg=WHITE, fg=TEXT).pack(side="left")
        self.dropdown(control, self.second_city, cities, self.comparison_refresh)
        self.comparison_refresh()

    def comparison_refresh(self):
        for widget in list(self.content.winfo_children())[3:]:
            widget.destroy()
        city1, city2 = self.first_city.get(), self.second_city.get()
        if city1 == city2:
            tk.Label(self.content, text="Choose two different cities.", bg=LIGHT, fg=ORANGE,
                     font=("Segoe UI", 13, "bold")).pack(padx=30, pady=20)
            return
        first, second = city_data(self.data, city1), city_data(self.data, city2)
        m1, m2 = first["AQI"].mean(), second["AQI"].mean()
        row = tk.Frame(self.content, bg=LIGHT)
        row.pack(fill="x", padx=(30, 19), pady=(18, 2))
        self.info_card(row, f"{city1} average AQI", f"{m1:.0f}" if pd.notna(m1) else "N/A")
        self.info_card(row, f"{city2} average AQI", f"{m2:.0f}" if pd.notna(m2) else "N/A", GREEN)

        figure = Figure(figsize=(10, 4), dpi=90, facecolor=WHITE)
        ax1, ax2 = figure.subplots(1, 2)
        ax1.bar([city1, city2], [m1, m2], color=[BLUE, GREEN])
        ax1.set_title("Average Indian AQI")
        ax1.set_ylabel("Indian AQI")
        for city, color in [(city1, BLUE), (city2, GREEN)]:
            monthly = month_averages(self.data, city)
            ax2.plot(monthly.index, monthly.values, marker="o", label=city,
                     color=color, linewidth=2)
        ax2.set_title("Monthly AQI comparison")
        ax2.set_xlabel("Month (1 = Jan)")
        ax2.set_ylabel("Indian AQI")
        ax2.set_xticks(range(1, 13))
        ax2.legend(fontsize=8)
        ax2.grid(alpha=0.2)
        figure.tight_layout(pad=2.4)
        self.draw_figure(figure)

        pm1 = first[["PM2.5", "PM10"]].mean()
        pm2 = second[["PM2.5", "PM10"]].mean()
        def value(v):
            return f"{v:.1f}" if pd.notna(v) else "N/A"
        text = (f"{city1}: PM2.5 {value(pm1['PM2.5'])}, PM10 {value(pm1['PM10'])} μg/m³ "
                f"({first['AQI'].count():,} AQI records)     |     "
                f"{city2}: PM2.5 {value(pm2['PM2.5'])}, PM10 {value(pm2['PM10'])} μg/m³ "
                f"({second['AQI'].count():,} AQI records)")
        tk.Label(self.content, text=text, bg=LIGHT, fg=GRAY, wraplength=850,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=30, pady=(0, 5))
        tk.Label(self.content, text="Note: Historical record coverage may differ between cities.",
                 bg=LIGHT, fg=GRAY, font=("Segoe UI", 9)).pack(anchor="w", padx=30)

    def live_page(self):
        self.heading("Live Air Quality", "Current Open-Meteo model estimate (US AQI, not Indian AQI).")
        control = self.panel()
        control.pack(fill="x", padx=30)
        tk.Label(control, text="City:", bg=WHITE, fg=TEXT).pack(side="left")
        self.dropdown(control, self.live_city, list(CITIES), lambda: None)
        self.refresh_button = self.button(control, "Refresh Live Data", self.refresh_live)
        self.refresh_button.pack(side="left")

        card = self.panel()
        card.pack(fill="x", padx=30, pady=(20, 0))
        tk.Label(card, text="CURRENT US AQI", bg=WHITE, fg=GRAY,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.aqi_label = tk.Label(card, text="--", bg=WHITE, fg=BLUE,
                                  font=("Segoe UI", 42, "bold"))
        self.aqi_label.pack(anchor="w")
        self.category_label = tk.Label(card, text="Press Refresh to get actual data.",
                                       bg=WHITE, fg=TEXT, font=("Segoe UI", 13))
        self.category_label.pack(anchor="w")
        self.time_label = tk.Label(card, text="", bg=WHITE, fg=GRAY,
                                   font=("Segoe UI", 10))
        self.time_label.pack(anchor="w", pady=(8, 0))
        readings = self.panel()
        readings.pack(fill="x", padx=30, pady=15)
        self.pollutants_label = tk.Label(readings, text="PM2.5, PM10, NO₂, CO and O₃ appear here.",
                                         bg=WHITE, fg=TEXT, justify="left", font=("Segoe UI", 12))
        self.pollutants_label.pack(anchor="w")
        self.status_label = tk.Label(self.content,
                 text="Internet required for live estimates. You can select Delhi or Ludhiana.",
                 bg=LIGHT, fg=GRAY, font=("Segoe UI", 10))
        self.status_label.pack(anchor="w", padx=30)
        if self.loading:
            self.refresh_button.config(state="disabled")
            self.status_label.config(text="Loading live estimate...")

    def refresh_live(self):
        """Use a background thread so the window stays responsive."""
        if self.loading:
            return
        city = self.live_city.get()
        self.loading = True
        self.refresh_button.config(state="disabled")
        self.status_label.config(text=f"Loading {city} from Open-Meteo...")

        def worker():
            try:
                answer = get_live_aqi(city)
                self.after(0, lambda: self.show_live_answer(city, answer, None))
            except Exception as error:
                message = str(error)
                try:
                    self.after(0, lambda: self.show_live_answer(city, None, message))
                except RuntimeError:
                    pass  # The user may have closed the app.

        threading.Thread(target=worker, daemon=True).start()

    def show_live_answer(self, city, result, error):
        self.loading = False
        if self.page_name != "Live AQI":
            return  # User navigated away before data arrived.
        self.refresh_button.config(state="normal")
        if error:
            self.status_label.config(text="Unable to get live data. Check your internet and try again.")
            self.category_label.config(text=error)
            return
        values, units = result["values"], result["units"]
        aqi = values.get("us_aqi")
        self.aqi_label.config(text=str(round(aqi)) if aqi is not None else "N/A")
        self.category_label.config(text=f"{city}  •  {aqi_category(aqi)}")
        self.time_label.config(text=f"Model data valid at: {values['time']} IST")
        names = [("PM2.5", "pm2_5"), ("PM10", "pm10"), ("NO₂", "nitrogen_dioxide"),
                 ("CO", "carbon_monoxide"), ("O₃", "ozone")]
        lines = []
        for title, key in names:
            reading = values.get(key)
            display = f"{reading:.1f} {units.get(key, '')}" if isinstance(reading, (int, float)) else "N/A"
            lines.append(f"{title}: {display}")
        self.pollutants_label.config(text="     |     ".join(lines[:3]) + "\n\n" + "     |     ".join(lines[3:]))
        self.status_label.config(text="Source: Open-Meteo / CAMS • modeled estimates, not monitoring-station readings")


if __name__ == "__main__":
    AirQualityApp().mainloop()
