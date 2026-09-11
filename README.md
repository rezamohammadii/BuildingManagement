# Building Management System (Console App)

A Python console application for managing a residential building's charges,
shared water bill, general expenses, and overall financial balance.

## Features

1. **Settings** — first-run wizard that asks for the total number of units,
   how many people live in each unit, and the monthly charge amount.
   Fully editable afterwards (charge amount, people per unit, add new units).
2. **Payments** — record charge deposits per unit (amount, unit number,
   payment date) and view full payment history.
3. **Water Bill Calculation** — enter the monthly water bill total; it is
   automatically split across units based on how many people live in each one.
4. **General Expenses** — record building expenses with a title, amount,
   and date.
5. **Financial Report** — shows total income vs. total expenses (general +
   water) and the net balance, with an option to export everything to an
   Excel (`.xlsx`) file.

## Requirements

- Python 3.9+
- Packages listed in `requirements.txt` (`rich`, `openpyxl`)

## Setup

```bash
pip install -r requirements.txt
python main.py
```

On the very first run, the app will walk you through configuring the
building (units, people per unit, charge amount). After that, it goes
straight to the main menu on every launch.

## Data storage

All data is stored locally in a SQLite database file (`building.db`),
created automatically in the same folder as the app. Excel exports are
saved to an `exports/` folder that is also created automatically.

## Project structure

```
building_manager/
├── main.py              # Entry point / main menu loop
├── database.py          # SQLite connection + schema
├── config_manager.py    # Settings wizard + settings menu
├── payment_manager.py   # Charge deposit tracking
├── water_manager.py     # Shared water bill calculation
├── expense_manager.py   # General expenses tracking
├── report_manager.py    # Financial summary + Excel export
├── ui.py                # Console UI helpers (rich-based)
└── requirements.txt
```
