import sys
from typing import Union, Callable

import rich
from rich.prompt import Prompt


console = rich.get_console()


class Menu:
    def __init__(
        self,
        title: str,
        prompt: str,
        choices: dict[str, Union["Menu", Callable]] = {},
        parent: Union["Menu", None] = None,
    ):
        for value in choices.values():
            if isinstance(value, Menu):
                value.parent = self
        self.title = title
        self.choices = choices
        self.prompt = prompt
        self.parent = parent

    @staticmethod
    def ask_choices(prompt: str, choices: list[str]) -> str:
        prompt_choices = []
        for index, choice in enumerate(choices):
            prompt_choices.extend([str(index + 1), choice, choice.lower()])
            rich.print(f"{index + 1}: {choice}")

        console.print()

        result = Prompt.ask(
            prompt,
            choices=prompt_choices,
            show_choices=False,
        )
        if result.isdigit():
            result = choices[int(result) - 1]
        else:
            try:
                index = choices.index(result)
            except ValueError:
                index = [c.lower() for c in choices].index(result)
            result = choices[index]
        return result

    def go_to(self, next_menu: Union["Menu", Callable]) -> bool | None:
        if isinstance(next_menu, Menu):
            next_menu.show()
        else:
            console.clear()
            next_menu()
            console.print()
            console.input("Press enter to go back")
            self.show()

    def go_back(self):
        if self.parent is not None:
            self.go_to(self.parent)

    def show(self):
        # Clear the screen
        console.clear()

        # Show the title
        console.print(f"[blue]{self.title}", justify="center")
        print()

        # Print out the prompt
        console.print(self.prompt)

        # Get the choices
        choices = list(self.choices.keys())

        # Add the back button if it has a parent
        if self.parent is not None:
            choices.append("Back")

        choices.append("Quit")

        # Ask the user to make a choice
        choice = self.ask_choices(">", choices)

        # Go back if they chose to go back
        if choice == "Back":
            return self.go_back()

        if choice == "Quit":
            console.clear()
            return sys.exit()

        # Get the next choice
        next_menu = self.choices.get(choice)

        # If by some miracle it's none return
        if next_menu is None:
            console.print("The choice chosen does not exist, so we are dying now")
            return None

        # Navigate to the next choice
        self.go_to(next_menu)
