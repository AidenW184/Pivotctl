"""ANSI terminal colours used by Pivotctl."""


class Colour:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_CYAN = "\033[96m"


def colour_text(text, colour):
    """Return text wrapped in an ANSI colour."""
    return f"{colour}{text}{Colour.RESET}"


if __name__ == "__main__":
    print(colour_text("[+] Success", Colour.BRIGHT_GREEN))
    print(colour_text("[-] Error", Colour.BRIGHT_RED))
    print(colour_text("[!] Warning", Colour.BRIGHT_YELLOW))
    print(colour_text("[*] Information", Colour.BRIGHT_CYAN))