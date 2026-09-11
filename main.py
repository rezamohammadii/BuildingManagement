"""
Building Management System - Console Application
Entry point: handles first-run setup and the main menu loop.
"""

import sys

import database
import ui
import config_manager
import payment_manager
import water_manager
import expense_manager
import report_manager


MAIN_MENU_TEXT = (
    "[bold]1[/bold]. Settings\n"
    "[bold]2[/bold]. Payments (Charge Deposits)\n"
    "[bold]3[/bold]. Water Bill Calculation\n"
    "[bold]4[/bold]. General Expenses\n"
    "[bold]5[/bold]. Financial Report\n"
    "[bold]0[/bold]. Exit"
)


def main_menu():
    while True:
        ui.print_header("Main Menu")
        ui.console.print(MAIN_MENU_TEXT)
        choice = ui.ask_text("\nSelect an option")

        if choice == "1":
            config_manager.settings_menu()
        elif choice == "2":
            payment_manager.payments_menu()
        elif choice == "3":
            water_manager.water_menu()
        elif choice == "4":
            expense_manager.expenses_menu()
        elif choice == "5":
            report_manager.show_report()
        elif choice == "0":
            ui.console.print("\n[bold cyan]Goodbye![/bold cyan]")
            sys.exit(0)
        else:
            ui.print_error("Invalid option. Please try again.")
            ui.pause()


def main():
    database.init_database()

    if not database.is_configured():
        config_manager.run_setup_wizard()

    main_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ui.console.print("\n\n[bold cyan]Goodbye![/bold cyan]")
        sys.exit(0)
