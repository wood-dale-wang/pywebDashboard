# modules/system.py
from typing import Any
import psutil
import platform
from datetime import datetime
from engine import BaseModule

class SystemModule(BaseModule):
    def __init__(self, settings):
        super().__init__(settings)
        self.history_size = settings.get('history_size', 60)

    async def get_data(self) -> dict[str, Any]:
        """获取系统状态数据"""
        try:
            # 获取CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 获取内存信息
            memory = psutil.virtual_memory()
            
            # 获取磁盘信息
            disk = psutil.disk_usage('/')
            
            # 获取网络信息
            net_io = psutil.net_io_counters()
            
            # 获取系统启动时间
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'cpu': {
                    'type': 'stacked-bar-chart',
                    'usage': cpu_percent,
                    'total': psutil.cpu_count()
                },
                'memory': {
                    'type': 'stacked-bar-chart',
                    'total': memory.total,
                    'used': memory.used,
                },
                'disk': {
                    'type': 'stacked-bar-chart',
                    'total': disk.total,
                    'used': disk.used,
                },
                'network': {
                    'type': 'table',
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                },
                'system': {
                    'type': 'table',
                    'platform': platform.system(),
                    'hostname': platform.node(),
                    'uptime': str(uptime).split('.')[0],  # 去除微秒
                    'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S')
                },
            }
        except Exception as e:
            return {'error': str(e)}

    def get_widget_config(self) -> dict[str, Any]:
        """获取widget配置"""
        config = super().get_widget_config()
        config.update({
            'type': 'card',
            'metrics': ['cpu', 'memory', 'disk'],
            'refresh_interval': 10000  # 10秒
        })
        return config