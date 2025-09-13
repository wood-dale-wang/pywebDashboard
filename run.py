# run.py
#!/usr/bin/env python3
"""
模块化仪表盘启动脚本
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='启动模块化仪表盘')
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.yaml',
        help='配置文件路径 (默认: config.yaml)'
    )
    parser.add_argument(
        '--host',
        type=str,
        help='服务器主机地址 (默认: 使用配置文件中的设置)'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        help='服务器端口 (默认: 使用配置文件中的设置)'
    )
    parser.add_argument(
        '--reload',
        action='store_true',
        help='开发模式下启用自动重载'
    )
    parser.add_argument(
        '--check-config',
        action='store_true',
        help='检查配置文件并退出'
    )
    
    args = parser.parse_args()
    
    # 检查配置文件是否存在
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"错误: 配置文件 {config_path} 不存在")
        sys.exit(1)
    
    # 检查必要的目录是否存在
    directories = ['modules', 'templates', 'static', 'static/css', 'static/js']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # 如果只有检查配置文件的参数
    if args.check_config:
        print(f"配置文件 {config_path} 检查通过")
        return
    
    # 导入并启动引擎
    try:
        from engine import DashboardEngine
        
        # 创建引擎实例
        engine = DashboardEngine(str(config_path))
        
        # 运行仪表盘
        if args.reload:
            # 开发模式
            import uvicorn
            uvicorn.run(
                "engine:DashboardEngine.run",
                host=args.host or "0.0.0.0",
                port=args.port or 8000,
                reload=True,
                factory=True
            )
        else:
            # 生产模式
            engine.run(host=args.host, port=args.port)
            
    except ImportError as e:
        print(f"错误: 缺少依赖包 - {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()