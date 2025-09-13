# modules/weather.py
from typing import Any
import aiohttp
import asyncio
from datetime import datetime
from engine import BaseModule

class WeatherModule(BaseModule):
    def __init__(self, settings):
        super().__init__(settings)
        self.api_key = settings.get('api_key')
        self.city = settings.get('city', '北京')
        self.base_url = "http://api.openweathermap.org/data/2.5"

    async def get_data(self) -> dict[str, Any]:
        """获取天气数据"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/weather"
                params = {
                    'q': self.city,
                    'appid': self.api_key,
                    'units': 'metric',
                    'lang': 'zh_cn'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'value': f"{data['main']['temp']}°C",
                            'label': data['weather'][0]['description'],
                            'subtitle': f"湿度: {data['main']['humidity']}%",
                            'icon': data['weather'][0]['icon'],
                            'city': self.city
                        }
                    else:
                        return {'error': f'API错误: {response.status}'}
        except Exception as e:
            return {'error': str(e)}

    def get_widget_config(self) -> dict[str, Any]:
        """获取widget配置"""
        config = super().get_widget_config()
        config.update({
            'type': 'card',
            'icon': 'weather',
            'refresh_interval': 300000  # 5分钟
        })
        return config