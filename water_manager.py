"""
Shared water bill calculation module.
Total monthly water bill is divided across units based on how many
people live in each unit.
"""

from database import get_connection
import ui
import config_manager


def calculate_water_bill():
    ui.print_header("Water Bill - Calculate Shared Cost")
    units = config_manager.get_units()

    if not units:
        ui.print_error("No units configured yet. Please configure settings first.")
        ui.pause()
        return

    total_people = sum(u["people_count"] for u in units)
    if total_people <= 0:
        ui.print_error("Total people count is zero. Cannot divide the bill.")
        ui.pause()
        return

    bill_month = ui.ask_text("Bill month (Jalali, e.g. 1404-06)")
    total_amount = ui.ask_float("Total water bill amount")
    while total_amount <= 0:
        ui.print_error("Amount must be greater than zero.")
        total_amount = ui.ask_float("Total water bill amount")

    cost_per_person = total_amount / total_people

    shares = [
        (u["unit_number"], u["people_count"], round(cost_per_person * u["people_count"], 2))
        for u in units
    ]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO water_bills (bill_month, total_amount, total_people, cost_per_person)
           VALUES (?, ?, ?, ?)""",
        (bill_month, total_amount, total_people, cost_per_person),
    )
    water_bill_id = cur.lastrowid
    cur.executemany(
        """INSERT INTO water_bill_shares (water_bill_id, unit_number, people_count, share_amount)
           VALUES (?, ?, ?, ?)""",
        [(water_bill_id, un, pc, share) for un, pc, share in shares],
    )
    conn.commit()
    conn.close()

    ui.print_success(f"Water bill for {bill_month} calculated and saved.")
    ui.console.print(
        f"[bold]Total people:[/bold] {total_people}   "
        f"[bold]Cost per person:[/bold] {ui.format_currency(cost_per_person)}"
    )
    ui.render_table(
        "Water Bill Shares per Unit",
        ["Unit", "People", "Share Amount"],
        [(un, pc, ui.format_currency(amt)) for un, pc, amt in shares],
    )
    ui.pause()


def list_water_bills():
    ui.print_header("Water Bill - History")
    conn = get_connection()
    bills = conn.execute(
        "SELECT * FROM water_bills ORDER BY id DESC"
    ).fetchall()

    ui.render_table(
        "Water Bills",
        ["ID", "Month", "Total Amount", "Total People", "Cost / Person"],
        [
            (b["id"], b["bill_month"], ui.format_currency(b["total_amount"]),
             b["total_people"], ui.format_currency(b["cost_per_person"]))
            for b in bills
        ],
    )

    if bills:
        bill_id = ui.ask_text("\nEnter a bill ID to view unit shares (or leave empty)", default="")
        if bill_id.strip():
            shares = conn.execute(
                "SELECT * FROM water_bill_shares WHERE water_bill_id = ? ORDER BY unit_number",
                (bill_id.strip(),),
            ).fetchall()
            ui.render_table(
                f"Shares for Bill #{bill_id}",
                ["Unit", "People", "Share Amount"],
                [(s["unit_number"], s["people_count"], ui.format_currency(s["share_amount"])) for s in shares],
            )

    conn.close()
    ui.pause()


def get_total_water_bills() -> float:
    conn = get_connection()
    row = conn.execute("SELECT COALESCE(SUM(total_amount), 0) AS total FROM water_bills").fetchone()
    conn.close()
    return row["total"]


def get_all_water_bills():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM water_bills ORDER BY id DESC").fetchall()
    conn.close()
    return rows


def water_menu():
    while True:
        ui.print_header("Water Bill")
        ui.console.print(
            "[bold]1[/bold]. Calculate a new shared water bill"
            "\n[bold]2[/bold]. View water bill history"
            "\n[bold]0[/bold]. Back to main menu"
        )
        choice = ui.ask_text("\nSelect an option")

        if choice == "1":
            calculate_water_bill()
        elif choice == "2":
            list_water_bills()
        elif choice == "0":
            return
        else:
            ui.print_error("Invalid option.")
            ui.pause()
