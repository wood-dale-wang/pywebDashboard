# engine.py
import os
import yaml
import importlib
from typing import Dict, List, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

class DashboardEngine:
    def __init__(self, config_path: str = "config.yaml"):
        self.app = FastAPI(title="Modular Dashboard")
        self.config = self.load_config(config_path)
        self.modules = {}
        self.widgets = []
        
        # 设置静态文件和模板
        self.setup_static_files()
        self.setup_templates()
        
        # 初始化模块
        self.initialize_modules()
        
        # 设置路由
        self.setup_routes()

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载YAML配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise Exception(f"配置文件 {config_path} 未找到")
        except yaml.YAMLError as e:
            raise Exception(f"配置文件解析错误: {e}")

    def setup_static_files(self):
        """设置静态文件目录"""
        static_dir = self.config.get('static_dir', 'static')
        if os.path.exists(static_dir):
            self.app.mount("/static", StaticFiles(directory=static_dir), name="static")

    def setup_templates(self):
        """设置模板引擎"""
        template_dir = self.config.get('template_dir', 'templates')
        self.templates = Jinja2Templates(directory=template_dir)

    def initialize_modules(self):
        """根据配置初始化所有模块"""
        modules_config = self.config.get('modules', {})
        
        for module_name, module_config in modules_config.items():
            if not module_config.get('enabled', True):
                continue
                
            try:
                # 动态导入模块
                module_path = f"modules.{module_name}"
                module = importlib.import_module(module_path)
                
                # 获取模块类（假设模块中有一个与模块名相同的类）
                module_class = getattr(module, module_config.get('class_name', module_name.capitalize()))
                
                # 实例化模块
                module_instance = module_class(module_config.get('settings', {}))
                
                # 存储模块实例
                self.modules[module_name] = module_instance
                
                # 注册widget
                if hasattr(module_instance, 'get_widget_config'):
                    self.widgets.append({
                        'name': module_name,
                        'config': module_instance.get_widget_config(),
                        'position': module_config.get('position', 'default')
                    })
                    
            except Exception as e:
                print(f"模块 {module_name} 初始化失败: {e}")

    def setup_routes(self):
        """设置FastAPI路由"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """主仪表盘页面"""
            return self.templates.TemplateResponse(
                "dashboard.html", 
                {
                    "request": request,
                    "widgets": self.widgets,
                    "dashboard_config": self.config.get('dashboard', {})
                }
            )

        @self.app.get("/api/widget/{widget_name}")
        async def get_widget_data(widget_name: str):
            """获取特定widget的数据"""
            if widget_name in self.modules:
                try:
                    data = await self.modules[widget_name].get_data()
                    return {"status": "success", "data": data}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
            return {"status": "error", "message": "Widget not found"}

        @self.app.get("/api/dashboard/status")
        async def get_dashboard_status():
            """获取仪表盘状态"""
            return {
                "status": "running",
                "modules": list(self.modules.keys()),
                "widgets": len(self.widgets)
            }

    def run(self, host: str = None, port: int = None):
        """启动仪表盘"""
        host = host or self.config.get('server', {}).get('host', '0.0.0.0')
        port = port or self.config.get('server', {}).get('port', 8000)
        
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


# 示例模块基类
class BaseModule:
    """所有模块的基类"""
    
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
    
    async def get_data(self) -> Dict[str, Any]:
        """获取模块数据，子类必须实现"""
        raise NotImplementedError
    
    def get_widget_config(self) -> Dict[str, Any]:
        """获取widget配置"""
        return {
            "title": self.settings.get('title', 'Unknown Widget'),
            "type": self.settings.get('type', 'default'),
            "refresh_interval": self.settings.get('refresh_interval', 5000)
        }


# 使用示例
if __name__ == "__main__":
    # 创建引擎实例
    engine = DashboardEngine("config.yaml")
    
    # 运行仪表盘
    engine.run()