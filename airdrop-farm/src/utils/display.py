import os
import shutil
from colorama import Fore, Style
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import pyfiglet

console = Console()

def get_terminal_width():
    """Получить ширину терминала"""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80

def center_text(text, width=None):
    """Центрировать текст"""
    if width is None:
        width = get_terminal_width()
    
    # Удаляем ANSI коды для правильного подсчета длины
    import re
    clean_text = re.sub(r'\x1B\[[0-9;]*m', '', text)
    text_length = len(clean_text)
    
    if text_length >= width:
        return text
    
    total_padding = width - text_length
    left_padding = total_padding // 2
    right_padding = total_padding - left_padding
    
    return ' ' * left_padding + text + ' ' * right_padding

def print_header(title):
    """Вывести красивый заголовок"""
    width = get_terminal_width()
    border = '─' * (width - 2)
    
    header_text = f"┬{border}┬"
    content_text = f"│ {title.ljust(width - 4)} │"
    footer_text = f"┴{border}┴"
    
    print(f"{Fore.CYAN}{header_text}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{content_text}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{footer_text}{Style.RESET_ALL}")

def print_info(label, value, context=""):
    """Вывести информацию в формате label: value"""
    from .logger import Logger
    Logger.info(f"{label.ljust(15)}: {Fore.CYAN}{value}{Style.RESET_ALL}", emoji="📍 ", context=context)

def print_banner():
    """Вывести баннер приложения"""
    width = get_terminal_width()
    
    # Создаем ASCII art заголовок
    title = pyfiglet.figlet_format("NT EXHAUST", font="block")
    
    # Выводим заголовок
    for line in title.split('\n'):
        if line.strip():
            centered_line = center_text(line, width)
            print(f"{Fore.CYAN}{centered_line}{Style.RESET_ALL}")
    
    # Выводим подзаголовки
    subtitle1 = "=== Telegram Channel 🚀 : NT EXHAUST @NTExhaust ==="
    subtitle2 = "✪ BOT CRYPTAL AI AUTO COMPLETE DAILY TASKS ✪"
    
    print(f"{Fore.MAGENTA}{center_text(subtitle1, width)}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{center_text(subtitle2, width)}{Style.RESET_ALL}")
    print()

def format_task_table(tasks, context=""):
    """Форматировать и вывести таблицу задач"""
    from .logger import Logger
    
    print()
    Logger.info("Task List:", context=context, emoji="📋 ")
    print()
    
    # Создаем таблицу с помощью rich
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Task Name", style="white", no_wrap=False, max_width=20)
    table.add_column("Category", style="blue", max_width=10)
    table.add_column("Point", style="yellow", max_width=7)
    table.add_column("Status", style="green", max_width=9)
    
    for task in tasks:
        # Обрезаем длинные названия задач
        display_name = task.get('description', 'Unknown Task')
        if len(display_name) > 20:
            display_name = display_name[:17] + '...'
        
        category = str(task.get('category', 'N/A'))[:8]
        points = str(task.get('credits_reward', 0))[:5]
        
        status_color = "green" if task.get('status') == 'completed' else "yellow"
        status_text = "Complete" if task.get('status') == 'completed' else "Pending"
        
        table.add_row(
            display_name,
            category,
            points,
            f"[{status_color}]{status_text}[/{status_color}]"
        )
    
    console.print(table)
    print()