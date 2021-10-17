import shutil

import colorama

from system.lib.config import config
from system.localization import locale


def print_feature(name: str, description: str = None, console_width: int = -1):
    print(name, end='')
    if description:
        print(' ' * (console_width // 2 - len(name)) + ': ' + description, end='')
    print()


def print_category(text):
    return print(colorama.Back.GREEN + colorama.Fore.BLACK + text + ' ' * (10 - len(text)) + colorama.Style.RESET_ALL)


def print_line(console_width):
    print((console_width - 1) * '-')


class Menu:
    class Item:
        def __init__(self, name, description=None, handler=None):
            self.name = name
            self.description = description
            self.handler = handler

    class Category:
        def __init__(self, _id: int, name: str):
            self.id = _id
            self.name = name
            self.items = []

        def item(self, name, description):
            def wrapper(handler):
                self.add(Menu.Item(name, description, handler))
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
        print((
            colorama.Back.BLACK + colorama.Fore.GREEN +
            locale.xcoder_header % config.version +
            colorama.Style.RESET_ALL
        ).center(console_width + 12))
        print('github.com/Vorono4ka/XCoder'.center(console_width - 1))
        print_line(console_width)

        for category in self.categories:
            print_category(category.name)
            for item_index in range(len(category.items)):
                item = category.items[item_index]
                print_feature(f' {category.id * 10 + item_index + 1} {item.name}', item.description, console_width)
            print_line(console_width)

        choice = input(locale.choice)
        try:
            choice = int(choice) - 1
            if choice < 0:
                return None
        except ValueError:
            return None
        print_line(console_width)

        category_id = choice // 10
        item_index = choice % 10
        for category in self.categories:
            if category.id == category_id:
                if len(category.items) > item_index:
                    item = category.items[item_index]
                    return item.handler
                break
        return None


menu = Menu()
