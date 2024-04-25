import random


class Colors:
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

def get_compress_string():
  return r"""
    ____       ____       __  __      _____       _____       ______       _____       _____      _______
   / ___|     / __ \     |  \/  |    |  __ \     |  __ \     |  ____|     / ____|     / ____|     \     /
   | |       | |  | |    | \  / |    | |__) |    | |__) |    | |__       | |         | |           \   /
   | |       | |  | |    | |\/| |    |  ___/     |  _  /     |  __|       \____ \     \____ \       \ /
   | |___    | |__| |    | |  | |    | |         | | \ \     | |____       ____| |     ____| |       
   \____|     \____/     |_|  |_|    |_|         |_|  \_\    |______|     |_____/     |_____/        o

  """

def get_decompress_string():
  return r"""
     ____       ______      ____       ____       __  __      _____       _____       ______       _____       _____      _______
    |  _ \     |  ____|    / ___|     / __ \     |  \/  |    |  __ \     |  __ \     |  ____|     / ____|     / ____|     \     /
    | | | |    | |         | |       | |  | |    | \  / |    | |__) |    | |__) |    | |__       | |         | |           \   /
    | | | |    |  __|      | |       | |  | |    | |\/| |    |  ___/     |  _  /     |  __|       \____ \     \____ \       \ /
    | |_| |    | |____     | |___    | |__| |    | |  | |    | |         | | \ \     | |____       ____| |     ____| |       
    |____/     |______|    \____|     \____/     |_|  |_|    |_|         |_|  \_\    |______|     |_____/     |_____/        o

  """


def create_cefd_banner(action_type: str):
  if action_type == 'decompress':
     banner = get_decompress_string()
  else:
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


def print_colored(text, color):
    reset = "\033[0m"
    if color in colors:
        return f"{colors[color]}{text}{reset}"
    else:
        return text
