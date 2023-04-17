import shutil
import textwrap
import typing

import colorama

from system.lib.config import config
from system.localization import locale


def print_feature(
    feature_id: int, name: str, description: str | None = None, console_width: int = -1
):
    text = f" {feature_id} {name}"
    if description:
        text += " " * (console_width // 2 - len(text)) + ": " + description

    print(textwrap.fill(text, console_width))


def print_category(text: str, background_width: int = 10):
    print(
        colorama.Back.GREEN
        + colorama.Fore.BLACK
        + text
        + " " * (background_width - len(text))
        + colorama.Style.RESET_ALL
    )


class Menu:
    class Item:
        def __init__(
            self,
            *,
            name: str,
            handler: typing.Callable,
            description: str | None = None,
        ):
            self.name: str = name
            self.description: str | None = description
            self.handler: typing.Callable = handler

    class Category:
        def __init__(self, _id: int, name: str):
            self.id = _id
            self.name = name
            self.items = []

        def item(self, name: str, description: str | None = None):
            def wrapper(handler: typing.Callable):
                self.add(Menu.Item(name=name, handler=handler, description=description))

            return wrapper

        def add(self, item):
            self.items.append(item)

    def __init__(self):
        self.categories = []

    def add_category(self, category):
        self.categories.append(category)
        return category

    def choice(self):
        console_width = shutil.get_terminal_size().columns
        print(
            (
                colorama.Back.BLACK
                + colorama.Fore.GREEN
                + locale.xcoder_header % config.version
                + colorama.Style.RESET_ALL
            ).center(console_width + 12)
        )
        print("github.com/Vorono4ka/XCoder".center(console_width - 1))
        self._print_divider_line(console_width)

        for category in self.categories:
            print_category(category.name)
            for item_index in range(len(category.items)):
                item = category.items[item_index]
                print_feature(
                    category.id * 10 + item_index + 1,
                    item.name,
                    item.description,
                    console_width,
                )
            self._print_divider_line(console_width)

        choice = input(locale.choice)
        try:
            choice = int(choice) - 1
            if choice < 0:
                return None
        except ValueError:
            return None
        self._print_divider_line(console_width)

        category_id = choice // 10
        item_index = choice % 10
        for category in self.categories:
            if category.id == category_id:
                if len(category.items) > item_index:
                    item = category.items[item_index]
                    return item.handler
                break
        return None

    @staticmethod
    def _print_divider_line(console_width: int) -> None:
        print((console_width - 1) * "-")


menu = Menu()
