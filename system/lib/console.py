class Console:
    @staticmethod
    def progress_bar(message, current, total):
        percentage = (current + 1) * 100 // total
        print("\r", end="")
        print(f"[{percentage}%] {message}", end="")
        if current + 1 == total:
            print()

    @staticmethod
    def percent(current: int, total: int) -> int:
        return (current + 1) * 100 // total

    @staticmethod
    def ask_integer(message: str):
        while True:
            try:
                return int(input(f"[????] {message}: "))
            except ValueError:
                pass

    @staticmethod
    def question(message):
        while True:
            answer = input(f"[????] {message} [Y/n] ").lower()
            if answer in "ny":
                break

        return "ny".index(answer)


if __name__ == "__main__":
    console = Console()
    console.ask_integer("Please, type any integer")

    for i in range(1000):
        console.progress_bar("Test progress bar", i, 1000)
