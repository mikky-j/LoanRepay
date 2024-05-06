from peewee import DoesNotExist, IntegrityError
import rich
from rich.console import Console
from rich.prompt import Prompt, FloatPrompt, Confirm

from loanrepay.models import User

logged_username: str | None = None


def authenticate_user(console: Console) -> User | None:
    if logged_username is None:
        console.print("[red]You are not logged in. Create a user or log in to continue")
        return None
    user: User | None = User.get_or_none(User.username == logged_username)
    if user is None:
        console.print("[red]User does not exist. Create a user or log in to continue")
        return None
    return user


def create_user():
    global logged_username
    console = rich.get_console()
    console.print("[blue]Create a user", justify="center")
    console.print()
    console.print(
        "Enter your user information (Enter `back` inside any of the fields to go back)"
    )
    console.print()
    username = password = ""
    while True:
        username = Prompt.ask("What username do you want")
        if username == "back":
            break
        password = Prompt.ask("Password")
        if password == "back":
            break
        user = User(username=username, password=password)
        try:
            user.save()
            console.print()
            console.print("[green]User successfully created")
            logged_username = username
            break
        except IntegrityError:
            console.print("[red]User already exists")


def login_user():
    global logged_username
    console = rich.get_console()
    console.print("[blue]Login user", justify="center")
    console.print()
    console.print(
        "Enter your user information (Enter `back` inside any of the fields to go back)"
    )
    console.print()
    username = password = ""
    while True:
        username = Prompt.ask("Username")
        if username == "back":
            break
        password = Prompt.ask("Password")
        if password == "back":
            break
        user = User.get_or_none(User.username == username)

        if user is None:
            console.print()
            console.print("[red] Username or Password is incorrect. Try again")
            break

        if user.password == password:
            logged_username = username
            console.print()
            console.print("[green]Logged in successfully")
            break


def get_current_user() -> str | None:
    return logged_username


def get_current_user_menu():
    console = rich.get_console()
    console.print("[blue]Current User", justify="center")
    console.print()
    console.print(f"The current user is [blue]{logged_username}")
