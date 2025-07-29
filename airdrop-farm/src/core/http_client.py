import aiohttp
import asyncio
import random
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse
import socks
from aiohttp_socks import ProxyConnector
from ..utils.logger import Logger
from ..utils.helpers import get_random_user_agent, delay

class HttpClient:
    """HTTP клиент с поддержкой прокси и повторных попыток"""
    
    def __init__(self, config: dict, proxy: Optional[str] = None):
        self.config = config
        self.proxy = proxy
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=config.get('api', {}).get('timeout', 60))
        
    async def __aenter__(self):
        await self.create_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()
    
    async def create_session(self):
        """Создать HTTP сессию"""
        connector = None
        
        if self.proxy:
            try:
                # Определяем тип прокси
                if self.proxy.startswith(('socks4://', 'socks5://')):
                    connector = ProxyConnector.from_url(self.proxy)
                elif self.proxy.startswith(('http://', 'https://')):
                    connector = aiohttp.TCPConnector()
                else:
                    Logger.warn(f"Unsupported proxy format: {self.proxy}")
                    connector = aiohttp.TCPConnector()
            except Exception as e:
                Logger.error(f"Failed to create proxy connector: {e}")
                connector = aiohttp.TCPConnector()
        else:
            connector = aiohttp.TCPConnector()
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout
        )
    
    async def close_session(self):
        """Закрыть HTTP сессию"""
        if self.session:
            await self.session.close()
    
    def get_headers(self, token: Optional[str] = None, use_global_headers: bool = True) -> Dict[str, str]:
        """Получить заголовки для запроса"""
        user_agents = self.config.get('user_agents', [])
        
        if use_global_headers and token:
            headers = self.config.get('headers', {}).copy()
            headers.update({
                'authorization': f'Bearer {token}',
                'user-agent': get_random_user_agent(user_agents)
            })
        else:
            headers = {
                'User-Agent': get_random_user_agent(user_agents),
                'Accept': 'application/json'
            }
        
        return headers
    
    async def request_with_retry(
        self,
        method: str,
        url: str,
        payload: Optional[Dict[str, Any]] = None,
        token: Optional[str] = None,
        use_global_headers: bool = True,
        context: str = "",
        retries: Optional[int] = None,
        backoff_factor: Optional[float] = None
    ) -> Dict[str, Any]:
        """Выполнить HTTP запрос с повторными попытками"""
        
        if retries is None:
            retries = self.config.get('api', {}).get('retries', 3)
        if backoff_factor is None:
            backoff_factor = self.config.get('api', {}).get('backoff_factor', 1.5)
        
        headers = self.get_headers(token, use_global_headers)
        backoff = 2.0
        
        for attempt in range(retries):
            try:
                kwargs = {
                    'headers': headers,
                    'proxy': self.proxy if self.proxy and self.proxy.startswith(('http://', 'https://')) else None
                }
                
                if payload is not None:
                    kwargs['json'] = payload
                
                async with self.session.request(method.upper(), url, **kwargs) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {'success': True, 'response': data}
                    elif response.status == 404:
                        return {'success': False, 'message': 'Task endpoint not found', 'status': 404}
                    else:
                        error_text = await response.text()
                        return {'success': False, 'message': f'HTTP {response.status}: {error_text}', 'status': response.status}
                        
            except asyncio.TimeoutError:
                error_msg = "Request timeout"
            except aiohttp.ClientError as e:
                error_msg = f"Client error: {str(e)}"
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
            
            if attempt < retries - 1:
                Logger.warn(f"Retrying {method.upper()} {url} ({attempt + 1}/{retries})", emoji="🔄", context=context)
                await delay(backoff)
                backoff *= backoff_factor
            else:
                Logger.error(f"Request failed after {retries} attempts: {error_msg}", context=context)
                return {'success': False, 'message': error_msg}
        
        return {'success': False, 'message': 'Max retries exceeded'}
    
    async def get(self, url: str, token: Optional[str] = None, context: str = "") -> Dict[str, Any]:
        """Выполнить GET запрос"""
        return await self.request_with_retry('GET', url, token=token, context=context)
    
    async def post(self, url: str, payload: Dict[str, Any], token: Optional[str] = None, context: str = "") -> Dict[str, Any]:
        """Выполнить POST запрос"""
        return await self.request_with_retry('POST', url, payload=payload, token=token, context=context)
    
    async def get_public_ip(self, context: str = "") -> str:
        """Получить публичный IP адрес"""
        try:
            result = await self.request_with_retry(
                'GET', 
                'https://api.ipify.org?format=json',
                use_global_headers=False,
                context=context
            )
            if result['success']:
                return result['response'].get('ip', 'Unknown')
            else:
                return 'Error retrieving IP'
        except Exception as e:
            Logger.error(f"Failed to get IP: {e}", emoji="❌", context=context)
            return 'Error retrieving IP'