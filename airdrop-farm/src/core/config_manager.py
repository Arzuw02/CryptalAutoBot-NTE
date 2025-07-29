import json
import os
from typing import List, Dict, Any
from ..utils.helpers import read_file_lines, load_config
from ..utils.logger import Logger

class ConfigManager:
    """Менеджер конфигурации приложения"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = {}
        self.tokens = []
        self.proxies = []
        self.use_proxy = False
    
    async def load_config(self) -> Dict[str, Any]:
        """Загрузить основную конфигурацию"""
        try:
            self.config = await load_config(self.config_path)
            if not self.config:
                Logger.error(f"Failed to load config from {self.config_path}")
                # Используем конфигурацию по умолчанию
                self.config = self._get_default_config()
            return self.config
        except Exception as e:
            Logger.error(f"Error loading config: {e}")
            self.config = self._get_default_config()
            return self.config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Получить конфигурацию по умолчанию"""
        return {
            "app": {
                "name": "NT EXHAUST - CRYPTAL AI AUTO BOT",
                "version": "1.0.0",
                "description": "CRYPTAL AI Auto Bot Daily Task"
            },
            "api": {
                "base_url": "https://api.cryptal.ai",
                "timeout": 60,
                "retries": 3,
                "backoff_factor": 1.5
            },
            "delays": {
                "between_accounts": 5,
                "between_tasks": 2,
                "cycle_delay": 86400
            },
            "headers": {
                "accept": "application/json",
                "cache_control": "no-cache",
                "origin": "https://api.cryptal.ai",
                "referer": "https://api.cryptal.ai/"
            },
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/102.0"
            ]
        }
    
    async def load_tokens(self, tokens_file: str = "data/token.txt") -> List[str]:
        """Загрузить токены из файла"""
        try:
            self.tokens = await read_file_lines(tokens_file)
            if self.tokens:
                Logger.info(f"Loaded {len(self.tokens)} token{'s' if len(self.tokens) != 1 else ''}", emoji="📄")
            else:
                Logger.warn(f"No tokens found in {tokens_file}", emoji="⚠️")
            return self.tokens
        except Exception as e:
            Logger.error(f"Failed to read tokens from {tokens_file}: {e}", emoji="❌")
            return []
    
    async def load_proxies(self, proxies_file: str = "data/proxy.txt") -> List[str]:
        """Загрузить прокси из файла"""
        try:
            self.proxies = await read_file_lines(proxies_file)
            if self.proxies:
                Logger.info(f"Loaded {len(self.proxies)} prox{'ies' if len(self.proxies) != 1 else 'y'}", emoji="🌐")
            else:
                Logger.warn(f"No proxies found in {proxies_file}", emoji="⚠️")
            return self.proxies
        except Exception as e:
            Logger.warn(f"Could not read proxies from {proxies_file}: {e}", emoji="⚠️")
            return []
    
    def get_user_input(self, prompt: str) -> str:
        """Получить ввод от пользователя"""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return ""
    
    async def initialize_proxy_config(self) -> bool:
        """Инициализировать конфигурацию прокси"""
        try:
            # В background режиме автоматически определяем использование прокси
            # на основе наличия файла прокси
            await self.load_proxies()
            
            if self.proxies:
                self.use_proxy = True
                Logger.info("Proxy configuration enabled", emoji="🔌")
                return True
            else:
                self.use_proxy = False
                Logger.info("Proceeding without proxy", emoji="ℹ️")
                return False
                
        except Exception as e:
            Logger.error(f"Error initializing proxy config: {e}")
            self.use_proxy = False
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Получить текущую конфигурацию"""
        return self.config
    
    def get_tokens(self) -> List[str]:
        """Получить загруженные токены"""
        return self.tokens
    
    def get_proxies(self) -> List[str]:
        """Получить загруженные прокси"""
        return self.proxies if self.use_proxy else []
    
    def should_use_proxy(self) -> bool:
        """Проверить, следует ли использовать прокси"""
        return self.use_proxy