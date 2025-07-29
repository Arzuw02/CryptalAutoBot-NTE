import asyncio
from typing import List, Dict, Any, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from ..core.http_client import HttpClient
from ..utils.logger import Logger
from ..utils.helpers import get_random_email, get_random_feedback, delay

class TaskManager:
    """Менеджер для работы с задачами"""
    
    def __init__(self, config: dict, http_client: HttpClient):
        self.config = config
        self.http_client = http_client
        self.base_url = config.get('api', {}).get('base_url', 'https://api.cryptal.ai')
    
    async def fetch_tasks(self, token: str, context: str = "") -> List[Dict[str, Any]]:
        """Получить список задач"""
        try:
            # Получаем все задачи
            all_tasks_url = f"{self.base_url}/apis/v2/vibe-credit/tasks?take=100&skip=0"
            all_tasks_response = await self.http_client.get(all_tasks_url, token=token, context=context)
            
            if not all_tasks_response['success']:
                raise Exception('Failed to fetch full task list')
            
            if not all_tasks_response['response'].get('response', {}).get('data'):
                raise Exception('Invalid task list response format')
            
            all_tasks = all_tasks_response['response']['response']['data']
            
            # Получаем доступные для пользователя задачи
            user_available_url = f"{self.base_url}/apis/v2/vibe-credit/tasks/user-available?take=100&skip=0"
            user_available_response = await self.http_client.get(user_available_url, token=token, context=context)
            
            if not user_available_response['success']:
                raise Exception('Failed to fetch user-available tasks')
            
            if not user_available_response['response'].get('response', {}).get('data'):
                raise Exception('Invalid user-available tasks response format')
            
            user_available_task_ids = [
                task['id'] for task in user_available_response['response']['response']['data']
            ]
            
            # Фильтруем и форматируем задачи
            tasks = []
            for task in all_tasks:
                # Исключаем задачи с приглашениями и репостами
                if task.get('task_type') in ['invite_friend', 'share_post']:
                    continue
                
                formatted_task = {
                    'id': task.get('id'),
                    'name': task.get('task_name'),
                    'description': task.get('task_description'),
                    'category': task.get('task_type'),
                    'credits_reward': task.get('credits_reward', 0),
                    'is_daily': task.get('is_daily', False),
                    'is_one_time': task.get('is_one_time', False),
                    'status': 'pending' if task.get('id') in user_available_task_ids else 'completed'
                }
                tasks.append(formatted_task)
            
            return tasks
            
        except Exception as e:
            Logger.error(f"Failed to fetch tasks: {e}", context=context)
            return []
    
    async def complete_task(self, token: str, task: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Выполнить задачу"""
        task_context = f"{context}|T{str(task['id'])[-6:]}"
        task_name = task.get('name', 'Unknown Task')
        category = task.get('category', 'unknown')
        
        Logger.info(f"Processing task: {task_name} [{category}]", emoji="🔄", context=task_context)
        
        try:
            response = None
            
            # Обрабатываем разные типы задач
            if category == 'daily_login':
                url = f"{self.base_url}/apis/v2/vibe-credit/tasks/daily-login"
                response = await self.http_client.get(url, token=token, context=task_context)
                
            elif category == 'follow_cryptal':
                url = f"{self.base_url}/apis/v2/vibe-credit/tasks/follow-cryptal"
                response = await self.http_client.get(url, token=token, context=task_context)
                
            elif category == 'join_discord':
                url = f"{self.base_url}/apis/v2/vibe-credit/tasks/follow-discord"
                response = await self.http_client.get(url, token=token, context=task_context)
                
            elif category == 'join_waitlist':
                email = get_random_email()
                payload = {'email': email, 'first_name': ''}
                url = f"{self.base_url}/apis/v2/vibe-credit/tasks/waitlist"
                response = await self.http_client.post(url, payload, token=token, context=task_context)
                
            elif category == 'submit_feedback':
                feedback = get_random_feedback()
                payload = {'feedback': feedback}
                url = f"{self.base_url}/apis/v2/vibe-credit/tasks/feedback"
                response = await self.http_client.post(url, payload, token=token, context=task_context)
                
            else:
                Logger.warn(f"Skipped: {task_name} [Category: {category}] - Task not supported", context=task_context)
                return {'success': False, 'message': f'Skipped: {category} not supported'}
            
            # Обрабатываем ответ
            if response and response['success']:
                response_data = response.get('response', {})
                if response_data.get('success') or 'already completed' in str(response_data.get('message', '')).lower():
                    Logger.success(f"Completed: {task_name} [Category: {category}]", context=task_context)
                    return {'success': True, 'message': f'Task "{task_name}" completed or already completed'}
                else:
                    error_msg = response_data.get('message', 'Unknown error')
                    Logger.warn(f"Failed to complete {task_name}: {error_msg} [Category: {category}]", context=task_context)
                    return {'success': False, 'message': f'Failed: {error_msg}'}
                    
            elif response and response.get('status') == 404:
                Logger.warn(f"Skipped: {task_name} [Category: {category}] - Task endpoint not found", context=task_context)
                return {'success': False, 'message': 'Skipped: Task endpoint not found'}
                
            else:
                error_msg = response.get('message', 'Unknown error') if response else 'No response'
                Logger.warn(f"Failed to complete {task_name}: {error_msg} [Category: {category}]", context=task_context)
                return {'success': False, 'message': f'Failed: {error_msg}'}
                
        except Exception as e:
            Logger.error(f"Failed to complete {task_name}: {e} [Category: {category}]", context=task_context)
            return {'success': False, 'message': f'Failed to complete: {e}'}
    
    async def process_tasks(self, token: str, tasks: List[Dict[str, Any]], context: str = "") -> Dict[str, int]:
        """Обработать все задачи"""
        if not tasks:
            Logger.info("No tasks available", emoji="⚠️", context=context)
            return {'completed': 0, 'skipped': 0, 'failed': 0}
        
        # Фильтруем только незавершенные задачи
        pending_tasks = [task for task in tasks if task.get('status') == 'pending']
        
        if not pending_tasks:
            Logger.info("All tasks already completed", emoji="✅", context=context)
            return {'completed': 0, 'skipped': 0, 'failed': 0}
        
        completed_count = 0
        skipped_count = 0
        failed_count = 0
        
        # Создаем прогресс бар
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=Logger.console if hasattr(Logger, 'console') else None
        ) as progress:
            
            task_progress = progress.add_task(
                "Processing tasks...", 
                total=len(pending_tasks)
            )
            
            for task in pending_tasks:
                try:
                    result = await self.complete_task(token, task, context)
                    
                    if result['success']:
                        task['status'] = 'completed'
                        completed_count += 1
                    elif 'Skipped' in result.get('message', ''):
                        skipped_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    Logger.error(f"Error processing task {task.get('id', 'unknown')}: {e}", context=context)
                    failed_count += 1
                
                progress.update(task_progress, advance=1)
                
                # Задержка между задачами
                delay_time = self.config.get('delays', {}).get('between_tasks', 2)
                await delay(delay_time)
        
        Logger.info(
            f"Processed {len(pending_tasks)} tasks: {completed_count} completed, {skipped_count} skipped, {failed_count} failed",
            emoji="📊",
            context=context
        )
        
        return {
            'completed': completed_count,
            'skipped': skipped_count,
            'failed': failed_count
        }