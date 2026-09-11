"""
General building expenses module: title, amount, date.
"""

from database import get_connection
import ui


def add_expense():
    ui.print_header("General Expenses - Add New")

    title = ui.ask_text("Expense title")
    while not title.strip():
        ui.print_error("Title cannot be empty.")
        title = ui.ask_text("Expense title")

    amount = ui.ask_float("Amount")
    while amount <= 0:
        ui.print_error("Amount must be greater than zero.")
        amount = ui.ask_float("Amount")

    expense_date = ui.ask_date("Expense date")

    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (title, amount, expense_date) VALUES (?, ?, ?)",
        (title.strip(), amount, expense_date),
    )
    conn.commit()
    conn.close()

    ui.print_success(f"Expense '{title}' recorded.")
    ui.pause()


def list_expenses():
    ui.print_header("General Expenses - History")
    conn = get_connection()
    rows = conn.execute(
        "SELECT title, amount, expense_date FROM expenses ORDER BY expense_date DESC, id DESC"
    ).fetchall()
    conn.close()

    ui.render_table(
        "All Recorded Expenses",
        ["Title", "Amount", "Date"],
        [(r["title"], ui.format_currency(r["amount"]), r["expense_date"]) for r in rows],
    )

    if rows:
        total = sum(r["amount"] for r in rows)
        ui.console.print(f"\n[bold]Total expenses:[/bold] {ui.format_currency(total)}")

    ui.pause()


def get_total_expenses() -> float:
    conn = get_connection()
    row = conn.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses").fetchone()
    conn.close()
    return row["total"]


def get_all_expenses():
    conn = get_connection()
    rows = conn.execute(
        "SELECT title, amount, expense_date FROM expenses ORDER BY expense_date DESC, id DESC"
    ).fetchall()
    conn.close()
    return rows


def expenses_menu():
    while True:
        ui.print_header("General Expenses")
        ui.console.print(
            "[bold]1[/bold]. Add a new expense"
            "\n[bold]2[/bold]. View expense history"
            "\n[bold]0[/bold]. Back to main menu"
        )
        choice = ui.ask_text("\nSelect an option")

        if choice == "1":
            add_expense()
        elif choice == "2":
            list_expenses()
        elif choice == "0":
            return
        else:
            ui.print_error("Invalid option.")
            ui.pause()
