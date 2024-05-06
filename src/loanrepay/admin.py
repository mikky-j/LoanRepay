"""
This is the admin menus for the app
"""

import numpy as np
from matplotlib import pyplot as plt
import rich
from rich.prompt import IntPrompt
from rich.table import Table
from loanrepay.models import Loan, Payment


def get_sum_payments() -> dict[int, int]:
    group: dict[int, int] = {}

    for payment in Payment.select():
        group[payment.month] = (
            payment.amount
            if group.get(payment.month) is None
            else group[payment.month] + payment.amount
        )

    return group


def company_status():
    console = rich.get_console()
    console.print("[blue]Company Status", justify="center")
    console.print()

    table = Table(title="Company Statistics")
    table.add_column("Total money lent out")
    table.add_column("Average monthly income")
    table.add_column("Highest Earning month")

    total_money = sum(loan.original_loan_amount for loan in Loan.select())
    average_monthly_income = np.average(
        [payment.amount for payment in Payment.select()]
    )
    group = get_sum_payments()

    highest_month = 0
    highest_month_value = 0
    try:
        highest_month = max(group, key=group.get)
        highest_month_value = max(group.values())
    except ValueError:
        highest_month = 0
        highest_month_value = 0

    table.add_row(
        f"${total_money}",
        f"${average_monthly_income}",
        f"Month {highest_month} - ${highest_month_value:.2f}",
    )

    console.print(table, justify="center")


def company_projections():
    console = rich.get_console()
    console.print("[blue]Company Projections", justify="center")
    console.print()

    group = get_sum_payments()
    months = np.array(list(group.keys()))
    company_income = np.array(list(group.values()))

    poly = np.polynomial.Polynomial.fit(months, company_income, 1)

    # x_mean = np.mean(months)
    # y_mean = np.mean(company_income)
    # numerator = np.sum((months - x_mean) * (company_income - y_mean))
    # denominator = np.sum((months - x_mean) ** 2)
    # slope = numerator / denominator
    # intercept = y_mean - (slope * x_mean)
    #

    future_months = IntPrompt.ask("How many months into the future do you want to go")

    console.print("[yellow]Calculating")

    future_months = range(months.max() + 1, months.max() + future_months + 1)

    predicted_income = []

    for month in future_months:
        predicted_income.append(poly(month))

    # future = np.array(range(months.max() + 1, months.max() + future_months))
    # predicted_income = (slope * future) + intercept

    # Connect the original to the predicted
    plt.plot(
        [months[-1], future_months.start],
        [company_income[-1], predicted_income[0]],
        marker="o",
        linestyle="-",
        color=(0, 1, 0),
    )
    plt.plot(months, company_income, marker="o", linestyle="-", color=(0, 0, 1))
    plt.plot(
        future_months, predicted_income, marker="o", linestyle="-", color=(0, 1, 0)
    )
    plt.xlabel("Months")
    plt.ylabel("Loan payment")
    plt.title("Company Monthly Income")
    plt.grid(True)
    plt.show()


# def raw_user_info():
#     Menu.ask_choices()
#
#     pass
