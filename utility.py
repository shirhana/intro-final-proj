import random


class Colors:
    """Enumeration class for color names.
    """
    red = "red"
    green = "green"
    yellow = "yellow"
    blue = "blue"
    purple = "purple"
    cyan = "cyan"


colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
    }

def get_compress_string() -> str:
  """Returns the ASCII art for compression.
  """
  return r"""
    ____       ____       __  __      _____       _____       ______       _____       _____       _______      __         ___   ___     _______
   / ___|     / __ \     |  \/  |    |  __ \     |  __ \     |  ____|     / ____|     / ____|     |  _____|    |  |        \  \ /  /     \     /
   | |       | |  | |    | \  / |    | |__) |    | |__) |    | |__       | |         | |          |  |__       |  |         \  V  /       \   /
   | |       | |  | |    | |\/| |    |  ___/     |  _  /     |  __|       \____ \     \____ \     |  ___|      |  |          \   /         \ /
   | |___    | |__| |    | |  | |    | |         | | \ \     | |____       ____| |     ____| |    | |          |  |____       | |
   \____|     \____/     |_|  |_|    |_|         |_|  \_\    |______|     |_____/     |_____/     |_|          |_______|      |_|           o

  """


def create_cefd_banner() -> str:
  """Creates a colored banner.

    Returns:
        str: A colored banner representing the action type.
    """
  
  banner = get_compress_string()

  reset = "\033[0m"
  res = ''
  avail_colors = [each for each in colors.keys()]
  for each in banner:
    if each!=' ':
        res+=f'{colors[random.choice(avail_colors)]}{each}{reset}'
    else:
        res+=' '
  return res


def print_colored(text: str, color: str) -> str:
    """Prints colored text based on the specified color.

    Args:
        text (str): The text to be printed.
        color (str): The color name.

    Returns:
        str: The colored text.
    """
    reset = "\033[0m"
    if color in colors:
        return f"{colors[color]}{text}{reset}"
    else:
        return text
