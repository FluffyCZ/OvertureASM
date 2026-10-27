import datetime
from colorama import init, Fore, Style

init(autoreset=True)

class Logger:
    COLORS = {
        "DEBUG": Fore.LIGHTBLACK_EX,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "SYSTEM": Fore.BLUE
    }

    @staticmethod
    def _print_log(level: str, msg: str) -> None:
        color = Logger.COLORS.get(level, Fore.WHITE)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # Clock format: [14:05:22] [DEBUG] Message
        sys_time = f"{Fore.LIGHTBLACK_EX}({timestamp})"
        lvl_tag = f"{Style.BRIGHT}{Fore.WHITE}[{color}{level}{Fore.WHITE}]{Fore.RESET}"

        print(f"{sys_time} {lvl_tag} {Fore.WHITE}{msg}")

    @staticmethod
    def debug(msg: str) -> None:
        Logger._print_log("DEBUG", msg)

    @staticmethod
    def info(msg: str) -> None:
        Logger._print_log("INFO", msg)

    @staticmethod
    def warning(msg: str) -> None:
        Logger._print_log("WARNING", msg)

    @staticmethod
    def error(msg: str) -> None:
        Logger._print_log("ERROR", msg)

    @staticmethod
    def system(msg: str) -> None:
        Logger._print_log("SYSTEM", msg)