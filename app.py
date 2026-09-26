"""
Building Management System - Web App (Flask)
Run with: python app.py, then open http://127.0.0.1:5000
"""

import os

from flask import (
    Flask, render_template, request, redirect, url_for, flash, send_file
)

import database
import services

app = Flask(__name__)
app.secret_key = "building-management-local-secret"  # local single-user app


# --------------------------------------------------------------------------
# Setup gate: every request must go through /setup until configured
# --------------------------------------------------------------------------

@app.before_request
def require_setup():
    if request.endpoint in ("setup", "static"):
        return None
    if not database.is_configured():
        return redirect(url_for("setup"))


@app.route("/setup", methods=["GET", "POST"])
def setup():
    if database.is_configured():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        try:
            total_units = int(request.form.get("total_units", 0))
            charge_amount = float(request.form.get("charge_amount", 0))
        except (TypeError, ValueError):
            flash("Please enter valid numbers.", "error")
            return redirect(url_for("setup"))

        if total_units <= 0:
            flash("Total units must be greater than zero.", "error")
            return redirect(url_for("setup"))
        if charge_amount < 0:
            flash("Charge amount cannot be negative.", "error")
            return redirect(url_for("setup"))

        units_people = []
        for i in range(1, total_units + 1):
            try:
                people = int(request.form.get(f"people_{i}", 1))
            except (TypeError, ValueError):
                people = 1
            if people < 0:
                people = 0
            units_people.append((i, people))

        services.complete_setup(total_units, charge_amount, units_people)
        flash("Setup completed successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("setup.html", total_units=None, charge_amount=None, people_values={})


# --------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------

@app.route("/")
def dashboard():
    units = services.get_units()
    settings = services.get_settings()
    summary = services.build_summary()
    total_people = sum(u["people_count"] for u in units)
    return render_template(
        "dashboard.html",
        active="dashboard",
        units=units,
        settings=settings,
        summary=summary,
        total_people=total_people,
        today=services.today_jalali(),
    )


# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------

@app.route("/settings")
def settings_page():
    units = services.get_units()
    settings = services.get_settings()
    existing = [u["unit_number"] for u in units]
    suggested = max(existing, default=0) + 1
    return render_template(
        "settings.html",
        active="settings",
        units=units,
        settings=settings,
        suggested_unit_number=suggested,
    )


@app.route("/settings/charge", methods=["POST"])
def update_charge():
    try:
        amount = float(request.form.get("charge_amount", 0))
    except (TypeError, ValueError):
        flash("Please enter a valid amount.", "error")
        return redirect(url_for("settings_page"))
    if amount < 0:
        flash("Amount cannot be negative.", "error")
        return redirect(url_for("settings_page"))
    services.update_charge_amount(amount)
    flash("Charge amount updated.", "success")
    return redirect(url_for("settings_page"))


@app.route("/settings/units/<int:unit_number>", methods=["POST"])
def update_unit(unit_number):
    try:
        people_count = int(request.form.get("people_count", 0))
    except (TypeError, ValueError):
        flash("Please enter a valid number of people.", "error")
        return redirect(url_for("settings_page"))
    if people_count < 0:
        flash("People count cannot be negative.", "error")
        return redirect(url_for("settings_page"))
    services.update_unit_people(unit_number, people_count)
    flash(f"Unit {unit_number} updated.", "success")
    return redirect(url_for("settings_page"))


@app.route("/settings/units/add", methods=["POST"])
def add_unit_route():
    try:
        unit_number = int(request.form.get("unit_number", 0))
        people_count = int(request.form.get("people_count", 0))
    except (TypeError, ValueError):
        flash("Please enter valid numbers.", "error")
        return redirect(url_for("settings_page"))
    if unit_number <= 0 or people_count < 0:
        flash("Please enter valid values.", "error")
        return redirect(url_for("settings_page"))

    added = services.add_unit(unit_number, people_count)
    if added:
        flash(f"Unit {unit_number} added.", "success")
    else:
        flash(f"Unit {unit_number} already exists.", "error")
    return redirect(url_for("settings_page"))


# --------------------------------------------------------------------------
# Payments
# --------------------------------------------------------------------------

@app.route("/payments")
def payments_page():
    payments = services.list_payments()
    units = services.get_units()
    total = services.get_total_payments()
    return render_template(
        "payments.html",
        active="payments",
        payments=payments,
        units=units,
        total=total,
        today=services.today_jalali(),
    )


def _validate_payment_form(form):
    unit_numbers = services.get_unit_numbers()
    try:
        unit_number = int(form.get("unit_number", 0))
        amount = float(form.get("amount", 0))
    except (TypeError, ValueError):
        return None, "Please enter valid numbers."
    payment_date = form.get("payment_date", "").strip()

    if unit_number not in unit_numbers:
        return None, "Unit not found."
    if amount <= 0:
        return None, "Amount must be greater than zero."
    if not services.is_valid_jalali_date(payment_date):
        return None, "Invalid date. Please use Jalali YYYY-MM-DD."

    return (unit_number, amount, payment_date), None


@app.route("/payments/add", methods=["POST"])
def add_payment_route():
    data, error = _validate_payment_form(request.form)
    if error:
        flash(error, "error")
        return redirect(url_for("payments_page"))
    services.add_payment(*data)
    flash("Payment recorded.", "success")
    return redirect(url_for("payments_page"))


@app.route("/payments/<int:payment_id>/edit")
def edit_payment_page(payment_id):
    payment = services.get_payment(payment_id)
    if not payment:
        flash("Payment not found.", "error")
        return redirect(url_for("payments_page"))
    units = services.get_units()
    return render_template("payment_form.html", active="payments", payment=payment, units=units)


@app.route("/payments/<int:payment_id>/edit", methods=["POST"])
def update_payment_route(payment_id):
    data, error = _validate_payment_form(request.form)
    if error:
        flash(error, "error")
        return redirect(url_for("edit_payment_page", payment_id=payment_id))
    services.update_payment(payment_id, *data)
    flash("Payment updated.", "success")
    return redirect(url_for("payments_page"))


@app.route("/payments/<int:payment_id>/delete", methods=["POST"])
def delete_payment_route(payment_id):
    services.delete_payment(payment_id)
    flash("Payment deleted.", "success")
    return redirect(url_for("payments_page"))


# --------------------------------------------------------------------------
# Water bills
# --------------------------------------------------------------------------

@app.route("/water")
def water_page():
    bills = services.list_water_bills()
    units = services.get_units()
    total_people = sum(u["people_count"] for u in units)
    return render_template(
        "water.html",
        active="water",
        bills=bills,
        total_people=total_people,
        current_month=services.today_jalali()[:7],
    )


@app.route("/water/add", methods=["POST"])
def add_water_bill_route():
    bill_month = request.form.get("bill_month", "").strip()
    try:
        total_amount = float(request.form.get("total_amount", 0))
    except (TypeError, ValueError):
        flash("Please enter a valid amount.", "error")
        return redirect(url_for("water_page"))

    if not bill_month:
        flash("Please enter a bill month.", "error")
        return redirect(url_for("water_page"))
    if total_amount <= 0:
        flash("Amount must be greater than zero.", "error")
        return redirect(url_for("water_page"))

    result = services.calculate_water_bill(bill_month, total_amount)
    if result is None:
        flash("Cannot calculate: total people count is zero.", "error")
    else:
        flash(f"Water bill for {bill_month} calculated and saved.", "success")
    return redirect(url_for("water_page"))


@app.route("/water/<int:water_bill_id>")
def water_bill_detail(water_bill_id):
    bill = services.get_water_bill(water_bill_id)
    if not bill:
        flash("Water bill not found.", "error")
        return redirect(url_for("water_page"))
    shares = services.get_water_bill_shares(water_bill_id)
    return render_template("water_detail.html", active="water", bill=bill, shares=shares)


@app.route("/water/<int:water_bill_id>/edit")
def edit_water_bill_page(water_bill_id):
    bill = services.get_water_bill(water_bill_id)
    if not bill:
        flash("Water bill not found.", "error")
        return redirect(url_for("water_page"))
    return render_template("water_form.html", active="water", bill=bill)


@app.route("/water/<int:water_bill_id>/edit", methods=["POST"])
def update_water_bill_route(water_bill_id):
    bill_month = request.form.get("bill_month", "").strip()
    try:
        total_amount = float(request.form.get("total_amount", 0))
    except (TypeError, ValueError):
        flash("Please enter a valid amount.", "error")
        return redirect(url_for("edit_water_bill_page", water_bill_id=water_bill_id))

    if not bill_month or total_amount <= 0:
        flash("Please enter valid values.", "error")
        return redirect(url_for("edit_water_bill_page", water_bill_id=water_bill_id))

    services.update_water_bill(water_bill_id, bill_month, total_amount)
    flash("Water bill updated and shares recalculated.", "success")
    return redirect(url_for("water_page"))


@app.route("/water/<int:water_bill_id>/delete", methods=["POST"])
def delete_water_bill_route(water_bill_id):
    services.delete_water_bill(water_bill_id)
    flash("Water bill deleted.", "success")
    return redirect(url_for("water_page"))


# --------------------------------------------------------------------------
# General expenses
# --------------------------------------------------------------------------

@app.route("/expenses")
def expenses_page():
    expenses = services.list_expenses()
    total = services.get_total_expenses()
    return render_template(
        "expenses.html",
        active="expenses",
        expenses=expenses,
        total=total,
        today=services.today_jalali(),
    )


def _validate_expense_form(form):
    title = form.get("title", "").strip()
    try:
        amount = float(form.get("amount", 0))
    except (TypeError, ValueError):
        return None, "Please enter a valid amount."
    expense_date = form.get("expense_date", "").strip()

    if not title:
        return None, "Title cannot be empty."
    if amount <= 0:
        return None, "Amount must be greater than zero."
    if not services.is_valid_jalali_date(expense_date):
        return None, "Invalid date. Please use Jalali YYYY-MM-DD."

    return (title, amount, expense_date), None


@app.route("/expenses/add", methods=["POST"])
def add_expense_route():
    data, error = _validate_expense_form(request.form)
    if error:
        flash(error, "error")
        return redirect(url_for("expenses_page"))
    services.add_expense(*data)
    flash("Expense recorded.", "success")
    return redirect(url_for("expenses_page"))


@app.route("/expenses/<int:expense_id>/edit")
def edit_expense_page(expense_id):
    expense = services.get_expense(expense_id)
    if not expense:
        flash("Expense not found.", "error")
        return redirect(url_for("expenses_page"))
    return render_template("expense_form.html", active="expenses", expense=expense)


@app.route("/expenses/<int:expense_id>/edit", methods=["POST"])
def update_expense_route(expense_id):
    data, error = _validate_expense_form(request.form)
    if error:
        flash(error, "error")
        return redirect(url_for("edit_expense_page", expense_id=expense_id))
    services.update_expense(expense_id, *data)
    flash("Expense updated.", "success")
    return redirect(url_for("expenses_page"))


@app.route("/expenses/<int:expense_id>/delete", methods=["POST"])
def delete_expense_route(expense_id):
    services.delete_expense(expense_id)
    flash("Expense deleted.", "success")
    return redirect(url_for("expenses_page"))


# --------------------------------------------------------------------------
# Financial report
# --------------------------------------------------------------------------

@app.route("/report")
def report_page():
    summary = services.build_summary()
    return render_template("report.html", active="report", summary=summary)


@app.route("/report/export", methods=["POST"])
def export_report_route():
    filepath = services.export_to_excel()
    return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))


if __name__ == "__main__":
    database.init_database()
    app.run(debug=True, host="127.0.0.1", port=5000)
