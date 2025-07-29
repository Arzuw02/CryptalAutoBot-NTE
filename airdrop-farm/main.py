#!/usr/bin/env python3
"""
NT EXHAUST - CRYPTAL AI AUTO BOT
Python версия автобота для выполнения ежедневных задач Cryptal AI
"""

import asyncio
import os
import sys
from colorama import Fore, Style

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.config_manager import ConfigManager
from src.modules.account_manager import AccountManager
from src.utils.logger import Logger
from src.utils.display import print_banner
from src.utils.helpers import delay

class CryptalBot:
    """Основной класс бота Cryptal AI"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.account_manager = None
        self.config = {}
    
    async def initialize(self):
        """Инициализация бота"""
        try:
            # Загружаем конфигурацию
            self.config = await self.config_manager.load_config()
            
            # Создаем менеджер аккаунтов
            self.account_manager = AccountManager(self.config)
            
            # Инициализируем конфигурацию прокси
            await self.config_manager.initialize_proxy_config()
            
            Logger.info("Bot initialization completed", emoji="✅")
            return True
            
        except Exception as e:
            Logger.error(f"Failed to initialize bot: {e}", emoji="❌")
            return False
    
    async def run_cycle(self):
        """Выполнить один цикл обработки всех аккаунтов"""
        try:
            # Загружаем токены
            tokens = await self.config_manager.load_tokens()
            if not tokens:
                Logger.error("No tokens found. Please add tokens to data/token.txt", emoji="❌")
                return False
            
            # Получаем прокси если они используются
            proxies = self.config_manager.get_proxies()
            
            # Обрабатываем аккаунты
            results = await self.account_manager.process_multiple_accounts(tokens, proxies)
            
            # Выводим сводку результатов
            successful_accounts = sum(1 for result in results if result.get('success', False))
            failed_accounts = len(results) - successful_accounts
            
            Logger.info(
                f"Cycle completed: {successful_accounts} successful, {failed_accounts} failed accounts",
                emoji="📊"
            )
            
            return True
            
        except Exception as e:
            Logger.error(f"Error during cycle execution: {e}", emoji="❌")
            return False
    
    async def run_continuous(self):
        """Запустить бота в непрерывном режиме"""
        cycle_count = 1
        
        while True:
            try:
                Logger.info(f"Starting cycle #{cycle_count}", emoji="🔄")
                
                success = await self.run_cycle()
                if not success:
                    Logger.warn("Cycle failed, but continuing...", emoji="⚠️")
                
                # Получаем задержку между циклами
                cycle_delay = self.config.get('delays', {}).get('cycle_delay', 86400)  # 24 часа по умолчанию
                
                Logger.info(
                    f"Cycle #{cycle_count} completed. Waiting {cycle_delay/3600:.1f} hours for next cycle...",
                    emoji="⏰"
                )
                
                await delay(cycle_delay)
                cycle_count += 1
                
            except KeyboardInterrupt:
                Logger.info("Bot stopped by user", emoji="👋")
                break
            except Exception as e:
                Logger.error(f"Unexpected error in continuous mode: {e}", emoji="❌")
                Logger.info("Retrying in 60 seconds...", emoji="🔄")
                await delay(60)
    
    async def run_once(self):
        """Выполнить бота один раз"""
        try:
            Logger.info("Running bot in single execution mode", emoji="🎯")
            success = await self.run_cycle()
            
            if success:
                Logger.success("Single execution completed successfully", emoji="🎉")
            else:
                Logger.error("Single execution failed", emoji="❌")
                return False
            
            return True
            
        except Exception as e:
            Logger.error(f"Error in single execution mode: {e}", emoji="❌")
            return False

async def main():
    """Главная функция"""
    try:
        # Выводим баннер
        print_banner()
        
        # Создаем и инициализируем бота
        bot = CryptalBot()
        
        if not await bot.initialize():
            Logger.error("Bot initialization failed. Exiting.", emoji="❌")
            return
        
        # Проверяем переменные окружения для режима работы
        run_mode = os.getenv('RUN_MODE', 'continuous').lower()
        
        if run_mode == 'once':
            await bot.run_once()
        else:
            await bot.run_continuous()
            
    except KeyboardInterrupt:
        Logger.info("Application stopped by user", emoji="👋")
    except Exception as e:
        Logger.error(f"Fatal error: {e}", emoji="💥")
    finally:
        Logger.info("Application shutdown", emoji="🔻")

if __name__ == "__main__":
    # Проверяем версию Python
    if sys.version_info < (3, 7):
        print(f"{Fore.RED}Error: Python 3.7+ required. Current version: {sys.version}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Создаем директории если они не существуют
    os.makedirs("data", exist_ok=True)
    
    # Запускаем приложение
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Application interrupted{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)