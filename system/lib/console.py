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
    def ask_integer(message):
        try:
            return int(input(f'[????] {message}: '))
        except ValueError:
            return Console.ask_integer(message)

    @staticmethod
    def question(message):
        answer = input(f'[????] {message} [Y/n] ').lower()
        if answer in 'ny':
            return 'ny'.index(answer)
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
