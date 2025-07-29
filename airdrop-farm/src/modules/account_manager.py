import asyncio
from typing import Dict, Any, Optional, List
from ..core.http_client import HttpClient
from ..modules.task_manager import TaskManager
from ..utils.logger import Logger
from ..utils.display import print_header, print_info, format_task_table
from ..utils.helpers import truncate_token, format_number, delay

class AccountManager:
    """Менеджер для работы с аккаунтами"""
    
    def __init__(self, config: dict):
        self.config = config
        self.base_url = config.get('api', {}).get('base_url', 'https://api.cryptal.ai')
    
    async def fetch_user_info(self, token: str, http_client: HttpClient, context: str = "") -> Dict[str, Any]:
        """Получить информацию о пользователе"""
        try:
            url = f"{self.base_url}/apis/v2/auth/social-profiles"
            response = await http_client.get(url, token=token, context=context)
            
            if not response['success']:
                Logger.warn('Failed to fetch user info, using token identifier', context=context)
                return {'username': f"Token_{truncate_token(token)}"}
            
            response_data = response.get('response', {})
            profiles = response_data.get('response', [])
            
            if not isinstance(profiles, list) or len(profiles) == 0:
                Logger.warn('No social profiles found, using token identifier', context=context)
                return {'username': f"Token_{truncate_token(token)}"}
            
            username = profiles[0].get('display_name', f"Token_{truncate_token(token)}")
            return {'username': username}
            
        except Exception as e:
            Logger.error(f"Failed to fetch user info: {e}", context=context)
            return {'username': f"Token_{truncate_token(token)}"}
    
    async def fetch_statistics(self, token: str, http_client: HttpClient, context: str = "") -> Dict[str, Any]:
        """Получить статистику пользователя"""
        try:
            url = f"{self.base_url}/apis/v2/vibe-credit"
            response = await http_client.get(url, token=token, context=context)
            
            if not response['success']:
                raise Exception('Failed to fetch statistics')
            
            response_data = response.get('response', {})
            data = response_data.get('response', {})
            
            return {
                'total_credits': format_number(data.get('total_credits', 'N/A')),
                'leaderboard_rank': format_number(data.get('leaderboard_rank', 'N/A'))
            }
            
        except Exception as e:
            Logger.error(f"Failed to fetch statistics: {e}", context=context)
            return {'error': f'Failed: {e}'}
    
    async def process_account(
        self,
        token: str,
        index: int,
        total: int,
        proxy: Optional[str] = None
    ) -> Dict[str, Any]:
        """Обработать один аккаунт"""
        context = f"Account {index + 1}/{total}"
        
        Logger.info("Starting account processing", emoji="🚀", context=context)
        
        try:
            # Создаем HTTP клиент
            async with HttpClient(self.config, proxy) as http_client:
                
                # Получаем информацию об аккаунте
                print_header(f"Account Info {context}")
                
                user_info = await self.fetch_user_info(token, http_client, context)
                ip = await http_client.get_public_ip(context)
                
                print_info('Username', user_info['username'], context)
                print_info('IP', ip, context)
                print()
                
                # Создаем менеджер задач
                task_manager = TaskManager(self.config, http_client)
                
                # Получаем и обрабатываем задачи
                tasks = await task_manager.fetch_tasks(token, context)
                
                if not tasks:
                    Logger.error("Failed to fetch tasks", context=context)
                    return {'success': False, 'error': 'Failed to fetch tasks'}
                
                # Обрабатываем задачи
                task_results = await task_manager.process_tasks(token, tasks, context)
                
                # Показываем таблицу задач
                format_task_table(tasks, context)
                
                # Получаем статистику
                print_header(f"Account Stats {context}")
                stats = await self.fetch_statistics(token, http_client, context)
                
                if 'error' in stats:
                    Logger.error(f"Failed to fetch stats: {stats['error']}", context=context)
                else:
                    print_info('Total Credits', stats['total_credits'], context)
                    print_info('Leaderboard Rank', stats['leaderboard_rank'], context)
                
                Logger.success("Completed account processing", emoji="🎉", context=context)
                
                return {
                    'success': True,
                    'username': user_info['username'],
                    'task_results': task_results,
                    'stats': stats
                }
                
        except Exception as e:
            Logger.error(f"Error processing account: {e}", context=context)
            return {'success': False, 'error': str(e)}
    
    async def process_multiple_accounts(
        self,
        tokens: List[str],
        proxies: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Обработать несколько аккаунтов"""
        results = []
        
        if not tokens:
            Logger.error("No tokens provided", emoji="❌")
            return results
        
        for i, token in enumerate(tokens):
            proxy = None
            if proxies and len(proxies) > 0:
                proxy = proxies[i % len(proxies)]
            
            try:
                result = await self.process_account(token, i, len(tokens), proxy)
                results.append(result)
                
                # Задержка между аккаунтами
                if i < len(tokens) - 1:
                    print("\n\n")
                    delay_time = self.config.get('delays', {}).get('between_accounts', 5)
                    await delay(delay_time)
                    
            except Exception as e:
                Logger.error(f"Error processing account {i + 1}: {e}", emoji="❌")
                results.append({'success': False, 'error': str(e)})
        
        return results