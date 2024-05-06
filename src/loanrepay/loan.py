"""
This is the loan payment module that holds all the menus of loan stuff
"""

import random
from rich.console import Console
from matplotlib import pyplot as plt
import rich
from rich.prompt import FloatPrompt, Confirm
from rich.table import Table
from loanrepay.menu import Menu
from loanrepay.models import Loan, Payment, User
from loanrepay.user import authenticate_user


def take_loan():
    console = rich.get_console()
    console.print("[blue]Take a loan", justify="center")
    console.print()
    user = authenticate_user(console)
    if user is None:
        return

    previous_loan: Loan | None = (
        Loan.select()
        .join(User)
        .where(((User.id == user.id) & (Loan.loan_amount > 0)))
        .get_or_none()
    )
    if previous_loan is not None:
        console.print(
            f"[red]{user.username} already has a loan of ${previous_loan.loan_amount}."
        )
        return

    loan_amount = FloatPrompt.ask("How much do you want to loan")
    have_interest_rate = Confirm.ask("Do you have an interest rate")
    interest_rate = 0
    if have_interest_rate:
        interest_rate = FloatPrompt.ask("What is the monthly interest")
    else:
        console.print("Choosing a random interest rate")
        interest_rate = 2 + (random.random() * 8)

    interest_rate = round(interest_rate, 2)

    is_fixed = Confirm.ask("Do you want fixed payment")

    fixed_payment = 0

    if is_fixed:
        fixed_payment = FloatPrompt.ask("How much do you want to pay monthly")
        console.print(f"You are going to pay ${fixed_payment} every month")

    Loan.create(
        loan_amount=loan_amount * (1 + interest_rate / 100),
        interest_rate=interest_rate,
        user=user.id,
        fixed=is_fixed,
        fixed_pay_amount=fixed_payment,
        original_loan_amount=loan_amount,
    )
    console.print(
        f"[green]Successfuly taken a loan of ${loan_amount} at an interest rate of {interest_rate}. Hope you can pay it back sha"
    )

    console.print()


def pay_loan():
    console = rich.get_console()
    console.print("[blue]Pay loan", justify="center")
    console.print()
    user = authenticate_user(console)
    if user is None:
        return

    previous_loan: Loan | None = (
        Loan.select()
        .join(User)
        .where(((User.id == user.id) & (Loan.loan_amount > 0)))
        .get_or_none()
    )

    if previous_loan is None:
        console.print(
            "[red]You do not have a previous loan. Take our money first before you come here"
        )
        return

    console.print(f"You have [blue]${previous_loan.loan_amount} [default]left to pay")
    if previous_loan.fixed:
        fixed_payment_menu(previous_loan, console)
    else:
        normal_payment_menu(previous_loan, console)


def fixed_payment_menu(loan: Loan, console: Console):
    previous_payments: list[int] = [
        payment.month
        for payment in Payment.select(Payment.month)
        .join(Loan)
        .where(((Loan.id == loan.id) & (Loan.loan_amount > 0)))
    ]
    last_month = 0
    if len(previous_payments) != 0:
        last_month = max(previous_payments)
    paying_this_month = Confirm.ask(
        f"Are you paying ${loan.fixed_pay_amount} for month [default]{last_month + 1}"
    )
    if paying_this_month:
        loan.loan_amount -= loan.fixed_pay_amount
        loan.loan_amount *= 1 + loan.interest_rate / 100
        Payment.create(
            amount=loan.fixed_pay_amount,
            month=last_month + 1,
            current_balance=loan.loan_amount,
            user=loan.user,
            loan=loan.id,
        )
    else:
        loan.loan_amount *= 1 + loan.interest_rate / 100
        Payment.create(
            amount=0,
            month=last_month + 1,
            current_balance=loan.loan_amount,
            user=loan.user,
            loan=loan.id,
        )

    loan.save()

    console.print(
        f"[green]Successfuly paid [blue]${loan.fixed_pay_amount if paying_this_month else 0}"
    )
    if loan.loan_amount <= 0:
        console.print("[green]You have finished paying your loan 🥳🥳🥳")
    else:
        console.print(
            f"[green]You have [blue]${loan.loan_amount:.2f} [default]left to pay"
        )


def normal_payment_menu(loan: Loan, console: Console):
    previous_payments: list[int] = [
        payment.month
        for payment in Payment.select(Payment.month)
        .join(Loan)
        .where(((Loan.id == loan.id) & (Loan.loan_amount > 0)))
    ]
    last_month = 0
    if len(previous_payments) != 0:
        last_month = max(previous_payments)

    payment_amount = FloatPrompt.ask(
        f"How much do you want to pay for month [default]{last_month + 1}"
    )

    loan.loan_amount -= payment_amount
    loan.loan_amount *= 1 + loan.interest_rate / 100
    Payment.create(
        amount=payment_amount,
        month=last_month + 1,
        current_balance=loan.loan_amount,
        user=loan.user,
        loan=loan.id,
    )

    loan.save()

    console.print(f"[green]Successfuly paid [blue]${payment_amount:.2f}")
    if loan.loan_amount <= 0:
        console.print("[green]You have finished paying your loan 🥳🥳🥳")
    else:
        console.print(
            f"[green]You have [blue]${loan.loan_amount:.2f} [default]left to pay"
        )


def loan_history():
    console = rich.get_console()
    console.print("[blue]Loan History", justify="center")
    console.print()
    user = authenticate_user(console)
    if user is None:
        return
    loans: list[Loan] = Loan.select().join(User).where(User.id == user.id)
    for index, loan in enumerate(loans):
        table = Table(title=f"Loan {index + 1}")
        payments: list[Payment] = Payment.select().join(Loan).where(Loan.id == loan.id)
        table.add_column("Month")
        table.add_column("Amount Paid", no_wrap=True)
        table.add_column("Remaining Amount", justify="right", no_wrap=True)

        for payment in payments:
            if isinstance(payment, Payment):
                table.add_row(
                    str(payment.month),
                    "$" + format(payment.amount, ".2f"),
                    "$" + format(payment.current_balance, ".2f"),
                )

        console.print(table, justify="center")


def current_trend():
    console = rich.get_console()
    console.print("[blue]Graph Payment History", justify="center")
    console.print()
    user = authenticate_user(console)
    if user is None:
        return
    loans: list[Loan] = Loan.select().join(User).where(User.id == user.id)
    loan_titles = [f"Loan - {loan.created_at}" for loan in loans]
    choice = Menu.ask_choices("Which loan do you want to look at", loan_titles)
    selected_loan = loans[loan_titles.index(choice)]
    payments: list[Payment] = (
        Payment.select().join(Loan).where(Loan.id == selected_loan.id)
    )
    month_range = [payment.month for payment in payments]
    loan_balance = [payment.current_balance for payment in payments]
    plt.plot(month_range, loan_balance, marker="o", linestyle="-")
    plt.xlabel("Months")
    plt.ylabel("Loan payment")
    plt.title("Loan Repayment graph - Months against loan")
    plt.grid(True)
    plt.show()


# def loan_repayment(name: str) -> list[list[int | float]]:
#     loan_amount = FloatPrompt.ask(f"What is the loan amount {name}? (in dollars)")
#     interest_rate = FloatPrompt.ask("What is the monthly interest rate")
#     is_fixed = Confirm.ask("Do you want to do fixed payments each month")
#
#     data: list[list[int | float]] = []
#     month = 0
#     if is_fixed:
#         monthly_payment_amount = FloatPrompt.ask(
#             "How much do you want to pay each month"
#         )
#         while loan_amount > 0:
#             # Add the interest this month
#             loan_amount = loan_amount + (loan_amount * interest_rate / 100)
#             loan_amount -= monthly_payment_amount
#             month += 1
#
#             data.append([month, loan_amount, monthly_payment_amount])
#     else:
#         while loan_amount > 0:
#             monthly_payment_amount = FloatPrompt.ask(
#                 "How much do you want to pay this month"
#             )
#             loan_amount = loan_amount + (loan_amount * interest_rate / 100)
#             loan_amount -= monthly_payment_amount
#             month += 1
#             next_month_loan_amount = loan_amount + (loan_amount * (interest_rate / 100))
#
#             rich.print(
#                 f"You just paid ${monthly_payment_amount:.2f}, you have ${next_month_loan_amount:.2f} left to pay"
#             )
#             data.append([month, loan_amount, monthly_payment_amount])
#
#     rich.print("Completed calculating your payments!!!🥳🥳🥳🥳🥳")
#
#     print()
#
#     print(
#         tabulate(
#             data,
#             ["Month", "Remaining amount", "Amount Paid"],
#             floatfmt=".2f",
#             tablefmt="grid",
#         )
#     )
#
#     print()
#
#     show_graph = Confirm.ask("Do you want to see a graph")
#
#     if show_graph:
#         month_range = range(1, month + 1)
#         loan_balance = [payment_info[1] for payment_info in data]
#         plt.plot(month_range, loan_balance, marker="o", linestyle="-")
#         plt.xlabel("Months")
#         plt.ylabel("Loan payment")
#         plt.title("Loan Repayment graph - Months against loan")
#         plt.grid(True)
#         plt.show()
#     return data
