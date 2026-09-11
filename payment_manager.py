"""
Payments module: register and list charge deposits made by units.
"""

from database import get_connection
import ui
import config_manager


def add_payment():
    ui.print_header("Payments - Register New Deposit")
    unit_numbers = config_manager.get_unit_numbers()

    if not unit_numbers:
        ui.print_error("No units configured yet. Please configure settings first.")
        ui.pause()
        return

    unit_number = ui.ask_int(f"Unit number {unit_numbers}")
    if unit_number not in unit_numbers:
        ui.print_error("Unit not found.")
        ui.pause()
        return

    amount = ui.ask_float("Amount deposited")
    while amount <= 0:
        ui.print_error("Amount must be greater than zero.")
        amount = ui.ask_float("Amount deposited")

    payment_date = ui.ask_date("Payment date")

    conn = get_connection()
    conn.execute(
        "INSERT INTO payments (unit_number, amount, payment_date) VALUES (?, ?, ?)",
        (unit_number, amount, payment_date),
    )
    conn.commit()
    conn.close()

    ui.print_success(
        f"Payment of {ui.format_currency(amount)} recorded for unit {unit_number}."
    )
    ui.pause()


def list_payments():
    ui.print_header("Payments - History")
    conn = get_connection()
    rows = conn.execute(
        "SELECT unit_number, amount, payment_date FROM payments "
        "ORDER BY payment_date DESC, id DESC"
    ).fetchall()
    conn.close()

    ui.render_table(
        "All Recorded Payments",
        ["Unit", "Amount", "Date"],
        [(r["unit_number"], ui.format_currency(r["amount"]), r["payment_date"]) for r in rows],
    )

    if rows:
        total = sum(r["amount"] for r in rows)
        ui.console.print(f"\n[bold]Total collected:[/bold] {ui.format_currency(total)}")

    ui.pause()


def get_total_payments() -> float:
    conn = get_connection()
    row = conn.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM payments").fetchone()
    conn.close()
    return row["total"]


def get_all_payments():
    conn = get_connection()
    rows = conn.execute(
        "SELECT unit_number, amount, payment_date FROM payments "
        "ORDER BY payment_date DESC, id DESC"
    ).fetchall()
    conn.close()
    return rows


def payments_menu():
    while True:
        ui.print_header("Payments")
        ui.console.print(
            "[bold]1[/bold]. Register a new deposit"
            "\n[bold]2[/bold]. View payment history"
            "\n[bold]0[/bold]. Back to main menu"
        )
        choice = ui.ask_text("\nSelect an option")

        if choice == "1":
            add_payment()
        elif choice == "2":
            list_payments()
        elif choice == "0":
            return
        else:
            ui.print_error("Invalid option.")
            ui.pause()
