"""
This is the main application that coordinates everything
"""

from loanrepay.menu import Menu
from loanrepay import admin, user, loan, db

admin_status_menu = Menu(
    title="Loan Repay - Company Status",
    prompt="What do you want to see",
    choices={
        "Company Statistics": admin.company_status,
        "Company Projections": admin.company_projections,
    },
)

admin_menu = Menu(
    title="Loan Repay - Admin Platform",
    prompt="What do you want to do",
    choices={
        "Status": admin_status_menu,
    },
)


user_menu = Menu(
    title="Loan Repay - User Plaform",
    prompt="What do you want to do",
    choices={
        "Create User": user.create_user,
        "Login User": user.login_user,
        "Current User": user.get_current_user_menu,
        "Take loan": loan.take_loan,
        "Pay loan": loan.pay_loan,
        "Loan History": loan.loan_history,
        "See Loan Graph": loan.current_trend,
    },
)

initial_menu = Menu(
    title="Welcome to Loan Repay",
    prompt="Which platform do you want to go",
    choices={"Admin": admin_menu, "User": user_menu},
)


def main():
    """
    This is the starting point of the program
    """
    db.init()
    initial_menu.show()
