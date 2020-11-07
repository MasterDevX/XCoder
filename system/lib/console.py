import sys

import colorama


class Console:
    @staticmethod
    def info(message):
        print(f"[INFO] {message}")

    @staticmethod
    def progress_bar(message, current, total, start=0, end=100):
        sys.stdout.write(f"\r[{((current + 1) * end + start) // total + start}%] {message}")

    @staticmethod
    def percent(current, total):
        return (current + 1) * 100 // total

    @staticmethod
    def ask_integer(a):
        try:
            return int(input(f"[????] {a} "))
        except ValueError:
            return Console.ask_integer(a)

    @staticmethod
    def question(message):
        x = input(f"[????] {message} [y/n] ").lower()
        if x in ("y", "n"):
            return "ny".index(x)
        else:
            return Console.question(message)

    @staticmethod
    def error(message):
        print(colorama.Fore.RED + '[ERROR] ' + message + colorama.Style.RESET_ALL)

    @staticmethod
    def done_text(message):
        print(colorama.Fore.GREEN + message + colorama.Style.RESET_ALL)


if __name__ == '__main__':
    console = Console()
    console.ask_integer('Please, type any integer: ')
