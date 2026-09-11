"""
Console UI helpers built on top of the `rich` library.
Keeps all styling/formatting concerns in one place.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from datetime import datetime
import jdatetime

console = Console()

APP_TITLE = "Building Management System"


def print_header(subtitle: str = ""):
    console.clear()
    title = f"[bold cyan]{APP_TITLE}[/bold cyan]"
    if subtitle:
        title += f"\n[white]{subtitle}[/white]"
    console.print(Panel(title, expand=True, border_style="cyan"))


def print_success(message: str):
    console.print(f"[bold green]✔ {message}[/bold green]")


def print_error(message: str):
    console.print(f"[bold red]✘ {message}[/bold red]")


def print_info(message: str):
    console.print(f"[bold yellow]ℹ {message}[/bold yellow]")


def pause():
    Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="", show_default=False)


def ask_text(label: str, default: str = None) -> str:
    if default is not None:
        return Prompt.ask(label, default=default)
    return Prompt.ask(label)


def ask_int(label: str, default: int = None) -> int:
    if default is not None:
        return IntPrompt.ask(label, default=default)
    return IntPrompt.ask(label)


def ask_float(label: str, default: float = None) -> float:
    if default is not None:
        return FloatPrompt.ask(label, default=default)
    return FloatPrompt.ask(label)


def ask_confirm(label: str, default: bool = True) -> bool:
    return Confirm.ask(label, default=default)


def ask_date(label: str, default_today: bool = True) -> str:
    """Ask for a date in the Jalali (Shamsi) calendar, format YYYY-MM-DD."""
    default = jdatetime.date.today().strftime("%Y-%m-%d") if default_today else None
    while True:
        value = ask_text(f"{label} (Jalali YYYY-MM-DD)", default=default)
        try:
            jdatetime.datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print_error("Invalid date format. Please use Jalali YYYY-MM-DD (e.g. 1404-06-20).")


def render_table(title: str, columns: list, rows: list, styles: list = None):
    """
    Render a rich table.
    columns: list of column header strings
    rows: list of tuples/lists (row values, already formatted as strings)
    styles: optional list of column styles (same length as columns)
    """
    table = Table(title=title, border_style="cyan", header_style="bold cyan")
    for i, col in enumerate(columns):
        style = styles[i] if styles and i < len(styles) else None
        table.add_column(col, style=style)

    if not rows:
        table.add_row(*(["-"] * len(columns)))
    else:
        for row in rows:
            table.add_row(*[str(v) for v in row])

    console.print(table)


def format_currency(amount: float) -> str:
    return f"{amount:,.0f}"
