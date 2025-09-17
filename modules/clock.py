# modules/clock.py
from datetime import datetime
from typing import Any
import pytz
from engine import WidgetBaseModule

class ClockModule(WidgetBaseModule):
    def __init__(self, settings):
        super().__init__(settings)
        self.timezone = pytz.timezone(settings.get('timezone', 'UTC'))
        self.format = settings.get('format', '24h')

    async def get_data(self) -> dict[str, Any]:
        """获取当前时间数据"""
        try:
            now = datetime.now(self.timezone)
            
            # 格式化时间
            if self.format == '12h':
                time_str = now.strftime('%I:%M:%S %p')
            else:
                time_str = now.strftime('%H:%M:%S')
            
            return {
                'time': time_str,
                'date': now.strftime('%Y年%m月%d日'),
                'weekday': self.get_weekday_name(now.weekday()),
                'timezone': str(self.timezone),
                'format': self.format
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_weekday_name(self, weekday):
        """获取星期几的中文名称"""
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        return weekdays[weekday]

    def get_widget_config(self) -> dict[str, Any]:
        """获取widget配置"""
        config = super().get_widget_config()
        config.update({
            'type': 'digital',
            'refresh_interval': 1000  # 1秒
        })
        return config