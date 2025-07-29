import datetime
from colorama import Fore, Style, init
from rich.console import Console

# Инициализация colorama
init(autoreset=True)

console = Console()

class Logger:
    """Класс для цветного логирования с временными метками"""
    
    @staticmethod
    def _get_timestamp():
        """Получить текущее время в формате строки"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def _format_message(level, message, emoji="", context=""):
        """Форматировать сообщение с временной меткой и контекстом"""
        timestamp = Logger._get_timestamp()
        context_str = f"[{context}] " if context else ""
        return f"[ {Fore.WHITE}{timestamp}{Style.RESET_ALL} ] {emoji}{level} {context_str.ljust(20)}{Fore.WHITE}{message}{Style.RESET_ALL}"
    
    @staticmethod
    def info(message, emoji="ℹ️ ", context=""):
        """Вывести информационное сообщение"""
        level = f"{Fore.GREEN}INFO{Style.RESET_ALL}"
        formatted_msg = Logger._format_message(level, message, emoji, context)
        print(formatted_msg)
    
    @staticmethod
    def warn(message, emoji="⚠️ ", context=""):
        """Вывести предупреждение"""
        level = f"{Fore.YELLOW}WARN{Style.RESET_ALL}"
        formatted_msg = Logger._format_message(level, message, emoji, context)
        print(formatted_msg)
    
    @staticmethod
    def error(message, emoji="❌ ", context=""):
        """Вывести сообщение об ошибке"""
        level = f"{Fore.RED}ERROR{Style.RESET_ALL}"
        formatted_msg = Logger._format_message(level, message, emoji, context)
        print(formatted_msg)
    
    @staticmethod
    def success(message, emoji="✅ ", context=""):
        """Вывести сообщение об успехе"""
        level = f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}"
        formatted_msg = Logger._format_message(level, message, emoji, context)
        print(formatted_msg)