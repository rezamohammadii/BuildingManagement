"""
Settings management: initial setup wizard + editable settings menu.
Handles: total units, people count per unit, monthly charge amount.
"""

from database import get_connection
import ui


def run_setup_wizard():
    """First-run configuration wizard. Collects total units, people per unit,
    and the monthly charge amount."""
    ui.print_header("Initial Setup")
    ui.print_info("Welcome! Let's configure your building before we start.")
    console = ui.console

    total_units = ui.ask_int("Total number of units in the building")
    while total_units <= 0:
        ui.print_error("Total units must be greater than zero.")
        total_units = ui.ask_int("Total number of units in the building")

    console.print()
    ui.print_info("Now enter how many people live in each unit.")
    units_data = []
    for unit_number in range(1, total_units + 1):
        people = ui.ask_int(f"  Unit {unit_number} - number of people", default=1)
        while people < 0:
            ui.print_error("Number of people cannot be negative.")
            people = ui.ask_int(f"  Unit {unit_number} - number of people", default=1)
        units_data.append((unit_number, people))

    console.print()
    charge_amount = ui.ask_float("Monthly charge amount per unit")
    while charge_amount < 0:
        ui.print_error("Charge amount cannot be negative.")
        charge_amount = ui.ask_float("Monthly charge amount per unit")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO settings (id, total_units, charge_amount, is_configured)
           VALUES (1, ?, ?, 1)""",
        (total_units, charge_amount),
    )
    cur.executemany(
        "INSERT INTO units (unit_number, people_count) VALUES (?, ?)",
        units_data,
    )
    conn.commit()
    conn.close()

    ui.print_success("Setup completed successfully!")
    ui.pause()


def get_settings():
    conn = get_connection()
    row = conn.execute("SELECT * FROM settings WHERE id = 1").fetchone()
    conn.close()
    return row


def get_units():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM units ORDER BY unit_number").fetchall()
    conn.close()
    return rows


def get_unit_numbers():
    return [row["unit_number"] for row in get_units()]


def get_people_count(unit_number: int) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT people_count FROM units WHERE unit_number = ?", (unit_number,)
    ).fetchone()
    conn.close()
    return row["people_count"] if row else 0


def settings_menu():
    """Interactive menu: view / edit settings."""
    while True:
        ui.print_header("Settings")
        settings = get_settings()
        units = get_units()

        ui.render_table(
            "Current Configuration",
            ["Total Units", "Monthly Charge per Unit"],
            [(settings["total_units"], ui.format_currency(settings["charge_amount"]))],
        )
        ui.render_table(
            "Units",
            ["Unit Number", "People Count"],
            [(u["unit_number"], u["people_count"]) for u in units],
        )

        ui.console.print(
            "\n[bold]1[/bold]. Edit monthly charge amount"
            "\n[bold]2[/bold]. Edit people count for a unit"
            "\n[bold]3[/bold]. Add a new unit"
            "\n[bold]0[/bold]. Back to main menu"
        )
        choice = ui.ask_text("\nSelect an option")

        if choice == "1":
            _edit_charge_amount()
        elif choice == "2":
            _edit_unit_people(units)
        elif choice == "3":
            _add_unit()
        elif choice == "0":
            return
        else:
            ui.print_error("Invalid option.")
            ui.pause()


def _edit_charge_amount():
    settings = get_settings()
    new_amount = ui.ask_float(
        "New monthly charge amount", default=settings["charge_amount"]
    )
    conn = get_connection()
    conn.execute(
        "UPDATE settings SET charge_amount = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
        (new_amount,),
    )
    conn.commit()
    conn.close()
    ui.print_success("Charge amount updated.")
    ui.pause()


def _edit_unit_people(units):
    unit_numbers = [u["unit_number"] for u in units]
    unit_number = ui.ask_int(f"Unit number to edit {unit_numbers}")
    if unit_number not in unit_numbers:
        ui.print_error("Unit not found.")
        ui.pause()
        return
    new_people = ui.ask_int("New number of people", default=1)
    conn = get_connection()
    conn.execute(
        "UPDATE units SET people_count = ? WHERE unit_number = ?",
        (new_people, unit_number),
    )
    conn.commit()
    conn.close()
    ui.print_success("Unit updated.")
    ui.pause()


def _add_unit():
    conn = get_connection()
    existing = [r["unit_number"] for r in conn.execute("SELECT unit_number FROM units")]
    suggested = max(existing, default=0) + 1
    unit_number = ui.ask_int("New unit number", default=suggested)
    if unit_number in existing:
        ui.print_error("This unit number already exists.")
        conn.close()
        ui.pause()
        return
    people = ui.ask_int("Number of people in this unit", default=1)
    conn.execute(
        "INSERT INTO units (unit_number, people_count) VALUES (?, ?)",
        (unit_number, people),
    )
    conn.execute(
        "UPDATE settings SET total_units = total_units + 1, updated_at = CURRENT_TIMESTAMP WHERE id = 1"
    )
    conn.commit()
    conn.close()
    ui.print_success("Unit added.")
    ui.pause()
