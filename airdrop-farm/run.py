#!/usr/bin/env python3
"""
Упрощенный скрипт запуска для NT EXHAUST - CRYPTAL AI AUTO BOT
"""

import os
import sys
import argparse
from colorama import Fore, Style, init

# Инициализация colorama
init(autoreset=True)

def print_logo():
    """Вывести логотип"""
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'NT EXHAUST - CRYPTAL AI AUTO BOT':^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'Python Version':^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print()

def main():
    """Главная функция"""
    print_logo()
    
    # Настройка аргументов командной строки
    parser = argparse.ArgumentParser(description='NT EXHAUST - CRYPTAL AI Auto Bot')
    parser.add_argument('--mode', choices=['continuous', 'once'], default='continuous',
                       help='Режим работы: continuous (непрерывно) или once (один раз)')
    parser.add_argument('--no-proxy', action='store_true',
                       help='Отключить использование прокси')
    parser.add_argument('--config', default='config.json',
                       help='Путь к файлу конфигурации')
    
    args = parser.parse_args()
    
    # Проверка версии Python
    if sys.version_info < (3, 7):
        print(f"{Fore.RED}❌ Ошибка: Требуется Python 3.7+. Текущая версия: {sys.version}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Создание директорий
    os.makedirs("data", exist_ok=True)
    
    # Проверка наличия файлов
    if not os.path.exists("data/token.txt"):
        print(f"{Fore.YELLOW}⚠️  Создан файл data/token.txt. Пожалуйста, добавьте ваши токены.{Style.RESET_ALL}")
        with open("data/token.txt", "w") as f:
            f.write("# Добавьте ваши токены сюда, по одному на строку\n")
    
    if not os.path.exists("data/proxy.txt"):
        print(f"{Fore.YELLOW}⚠️  Создан файл data/proxy.txt. При необходимости добавьте прокси.{Style.RESET_ALL}")
        with open("data/proxy.txt", "w") as f:
            f.write("# Добавьте прокси сюда, по одному на строку\n# Форматы: http://user:pass@host:port или socks5://user:pass@host:port\n")
    
    # Установка переменных окружения
    os.environ['RUN_MODE'] = args.mode
    
    if args.no_proxy:
        os.environ['NO_PROXY'] = '1'
    
    # Информация о запуске
    print(f"{Fore.GREEN}🚀 Запуск бота в режиме: {args.mode}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}📁 Конфигурация: {args.config}{Style.RESET_ALL}")
    
    if args.no_proxy:
        print(f"{Fore.YELLOW}🌐 Прокси отключены{Style.RESET_ALL}")
    
    print()
    
    # Запуск основного скрипта
    try:
        import main
        import asyncio
        asyncio.run(main.main())
    except ImportError as e:
        print(f"{Fore.RED}❌ Ошибка импорта: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Убедитесь, что все зависимости установлены: pip install -r requirements.txt{Style.RESET_ALL}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️  Бот остановлен пользователем{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}💥 Критическая ошибка: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()