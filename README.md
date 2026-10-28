# Air Quality Explorer — SIMPLE Python Mini Project

A beginner-friendly desktop app with **3 pages, only 3 Python files**, and a clean dashboard. It uses the Python topics covered in college: functions, classes (one simple Tkinter class), conditions, dictionaries, Pandas, Matplotlib, and Tkinter. The `requests` library gets live air-quality estimates.

## 1. What this app does

| Page | What it shows |
|---|---|
| Dashboard | Select a city, see average **Indian AQI**, worst year-month, worst season, and two charts. |
| Compare Cities | Compare average Indian AQI, monthly patterns and PM2.5/PM10 for two cities. |
| Live AQI | Select Delhi, Ludhiana or another city, and refresh **current modeled US AQI** and pollutants. |

Historical analysis works offline once you've imported a CSV. Live estimates require internet. **Historical Indian AQI and live US AQI are different and must not be compared numerically as if they are the same scale.**

## 2. Folder structure

```text
Air_Quality_Explorer_Simple/
    main.py                 -> Tkinter window, buttons, pages and charts
    analysis.py             -> read CSV, calculate averages and seasons
    live_aqi.py             -> call the free Open-Meteo API
    requirements.txt        -> required packages
    README.md               -> this easy guide
    START_HERE.txt          -> quick instructions
    data/
        PLACE_CSV_HERE.txt  -> tells you where to put real CSV
        city_day.csv        -> YOU download this real dataset
```

There is **no fake historical CSV** in the ZIP.

## 3. Run in VS Code on Windows

1. Extract the ZIP and open `Air_Quality_Explorer_Simple` in VS Code.
2. Open **Terminal → New Terminal**.
3. Install packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Get the real dataset from [Kaggle — Air Quality Data in India](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india). Download it, extract it and find `city_day.csv`.
5. Put `city_day.csv` in the `data` folder. **Or** launch the app and choose **Import CSV** from the Dashboard.
6. Run:

   ```powershell
   python main.py
   ```

The app opens even if the CSV is not available. You can still visit the Live AQI page.

## 4. Understand the project in 5 simple steps

**Step 1 — Read the CSV:** In `analysis.py`, `pd.read_csv(filename)` loads the historical data into a DataFrame (a table).

**Step 2 — Clean the data:** `pd.to_datetime(...)` converts dates, and `pd.to_numeric(...)` converts AQI values to numbers. Missing values are skipped rather than filled with fake measurements.

**Step 3 — Calculate answers:** `mean()` calculates the average; `groupby("Month")` collects records for the same calendar month; `groupby("Season")` collects the four seasons. Winter = Dec-Feb; Summer = Mar-May; Monsoon = Jun-Sep; Post-Monsoon = Oct-Nov.

**Step 4 — Draw graphs:** `main.py` uses Matplotlib's `plot()` for a line graph and `bar()` for a bar graph. `FigureCanvasTkAgg` places these charts inside the Tkinter window.

**Step 5 — Get live data:** `live_aqi.py` uses `requests.get()` to ask Open-Meteo for a JSON response. Tkinter displays the returned numbers. A tiny background thread prevents the window from freezing during the internet request.

### Execution flow

```text
python main.py
   |
   +-- Dashboard/Compare -> analysis.py -> city_day.csv -> Pandas -> charts
   |
   +-- Live AQI -> live_aqi.py -> Open-Meteo API -> current US AQI
```

## 5. What to say while demonstrating

1. “This is my Air Quality Explorer desktop app built using Python and Tkinter.”
2. “On Dashboard, I select Delhi and check its average AQI and seasonal pollution patterns.”
3. “On Compare Cities, I select Delhi and Amritsar and compare their historical averages.”
4. “On Live AQI, I select Ludhiana and click Refresh to get actual Open-Meteo modeled data.”
5. “Historical values come from a Kaggle CSV; live values come from the Open-Meteo API. Their AQI scales are different.”

## 6. Quick viva questions (simple English)

1. **What is your project?** A Python desktop application that analyzes historical air quality and displays current model estimates.
2. **What is Tkinter?** A library for creating windows, buttons, and dropdown lists in Python.
3. **What is Pandas?** A library for reading and analyzing tabular data.
4. **What is a DataFrame?** A table containing rows and columns.
5. **What does `groupby()` do?** It groups rows with the same value so we can calculate averages.
6. **Why use Matplotlib?** To display bar graphs and line graphs.
7. **What is an API?** A service that lets our program request information from another server.
8. **What is JSON?** A common format for exchanging structured data between programs.
9. **Why use `try-except` or error handling?** To handle missing files or failed internet requests without closing the app.
10. **Why is Indian AQI different from US AQI?** They use different index definitions and category thresholds, so their numbers should not be treated as directly equivalent.

## 7. If something goes wrong

- **`python` is not recognized:** Install Python from python.org, enable *Add Python to PATH*, or try `py main.py`.
- **`No module named pandas/matplotlib/requests`:** Run `python -m pip install -r requirements.txt` in the same Python environment used for launching.
- **CSV missing:** Download `city_day.csv` and place it in `data`, or click **Import CSV**.
- **CSV import error:** Make sure the file contains `City`, `Date` and `AQI` columns.
- **Live API error:** Check internet, then retry. No API key is required for ordinary non-commercial use subject to Open-Meteo's terms.
- **No data for a city:** Some dates, cities and pollutants have missing measurements. The app does not invent them.

## 8. Data and limitations

- **Historical observations:** [Kaggle Air Quality Data in India](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india), originally compiled by Rohan Rao from CPCB data. This is older historical data, not current measurements. Ludhiana is not included in the standard `city_day.csv`; use Delhi vs Amritsar/Chandigarh there.
- **Live modeled estimates:** [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api), using CAMS model output at approximate city coordinates. These estimates are **not readings from an individual monitoring station**. Open-Meteo supplies the timestamp shown in the UI (converted to IST by the API option).
- The app compares average AQI over the dates available in each city; cities may have different date coverage. An incomplete year should not be interpreted as a full-year sample.
- For the worst year-month, we require at least **five valid daily AQI values**; small months are excluded from that ranking.
- The historical sample CSV is intentionally not bundled. Download and import genuine records before interpreting results.

## 9. Easy test checklist

- [ ] App launches with `python main.py`.
- [ ] All 3 sidebar pages open.
- [ ] Import a real CSV and check city dropdowns.
- [ ] Dashboard line and bar charts appear.
- [ ] Comparison works with two different cities.
- [ ] Live Refresh shows an AQI and timestamp when internet is available.
- [ ] Live Refresh shows a helpful message if the internet is unavailable.

**Technical testing:** The code was syntax-checked, historical calculations and API JSON parsing were checked with temporary test inputs, and the three Tkinter pages were opened in a virtual display. Actual internet responses could not be verified in this environment. The project does not claim live data tests passed against the remote service.
