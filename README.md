# Building Management System (Web App)

A Flask + SQLite web application for managing a residential building's
charges, shared water bill, general expenses, and overall financial balance.
This is the web version of the original console app — same data model, now
with a browser UI and full edit/delete support everywhere.

## Features

1. **Settings** — first-run setup wizard (total units, people per unit,
   monthly charge amount). Fully editable afterwards: change the charge
   amount, edit people-per-unit, or add new units.
2. **Payments** — record, edit, and delete charge deposits per unit.
3. **Water Bill Calculation** — enter the monthly total; it's split across
   units by people count. Edit a bill's amount/month later and shares are
   recalculated automatically. Delete old bills.
4. **General Expenses** — add, edit, and delete building expenses (title,
   amount, date).
5. **Financial Report** — income vs. expenses and net balance, with a
   one-click Excel (`.xlsx`) export.

All dates use the **Jalali (Shamsi) calendar**, format `YYYY-MM-DD`
(e.g. `1404-06-20`).

## Requirements

- Python 3.9+
- Packages in `requirements.txt` (`Flask`, `openpyxl`, `jdatetime`)

## Setup & run

```bash
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

On first launch you'll be taken straight to the setup wizard. After that,
every visit goes to the dashboard.

## Data storage

All data lives in a local SQLite file, `building.db`, created automatically
next to `app.py`. Excel exports are saved into an `exports/` folder (also
auto-created) and offered as a download from the Report page.

## Project structure

```
webapp/
├── app.py               # Flask routes
├── database.py           # SQLite connection + schema
├── services.py            # All business logic (DB reads/writes)
├── requirements.txt
├── templates/
│   ├── base.html          # Sidebar layout
│   ├── setup.html         # First-run wizard
│   ├── dashboard.html
│   ├── settings.html
│   ├── payments.html
│   ├── payment_form.html
│   ├── water.html
│   ├── water_form.html
│   ├── water_detail.html
│   ├── expenses.html
│   ├── expense_form.html
│   └── report.html
└── static/
    └── style.css
```

## Notes

- This runs the Flask **development server**, which is fine for local,
  single-user use on your own machine. It is not meant to be exposed to
  the internet as-is.
- The app is single-tenant (one building, no login) — same as the console
  version. If you need multiple buildings or multiple users, that would be
  a further extension.
