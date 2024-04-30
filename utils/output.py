import sys
from colorama import Fore, Style


def info(string: str):
    """
    Print an informational message in blue.

    Args:
        string (str): The message to print.
    """
    preface = "[*] "
    print(Fore.BLUE + preface + string + Style.RESET_ALL)


def error(string: str):
    """
    Print an error message in red and exit the program.

    Args:
        string (str): The error message to print.
    """
    preface = "[!] "
    print(Fore.RED + preface + string + Style.RESET_ALL)
    sys.exit(1)


def warn(string: str):
    """
    Print a warning message in yellow.

    Args:
        string (str): The warning message to print.
    """
    preface = "[-] "
    print(Fore.YELLOW + preface + string + Style.RESET_ALL)


def success(string: str):
    """
    Print a success message in green.

    Args:
        string (str): The success message to print.
    """
    preface = "[+] "
    print(Fore.GREEN + preface + string + Style.RESET_ALL)


def heading(string: str):
    """
    Print a heading message surrounded by decorative characters.

    Args:
        string (str): The heading message to print.
    """
    armor = "----"
    spacing = " "
    print("")
    print(
        Fore.GREEN
        + armor
        + spacing
        + string
        + spacing
        + armor
        + Style.RESET_ALL
    )
