import sys


class Console:
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


if __name__ == '__main__':
    console = Console()
    console.ask_integer('Please, type any integer: ')
