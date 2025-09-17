# modules/news.py
from typing import Any
import aiohttp
import feedparser
from datetime import datetime
from engine import WidgetBaseModule

class NewsModule(WidgetBaseModule):
    def __init__(self, settings):
        super().__init__(settings)
        self.source = settings.get('source', 'tech')
        self.max_items = settings.get('max_items', 5)
        self.feed_urls = {
            'tech': 'https://sspai.com/feed',
            'general': 'https://tingtalk.me/atom.xml',
            'finance': 'https://www.mobile01.com/rss/news.xml'
        }

    async def get_data(self) -> dict[str, Any]:
        """获取新闻数据"""
        try:
            feed_url = self.feed_urls.get(self.source, self.feed_urls['tech'])
            
            # 使用feedparser解析RSS
            feed = feedparser.parse(feed_url)
            #print(feed)
            items = []
            for entry in feed.entries[:self.max_items]:
                items.append({
                    'title': entry.title,
                    'author': entry.author,
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else '',
                    'summary': entry.summary if hasattr(entry, 'summary') else '',
                    'meta': self.format_published_date(entry.published) if hasattr(entry, 'published') else ''
                })
            
            return {
                'items': items,
                'source': self.source,
                'total': len(items),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def format_published_date(self, published_str):
        """格式化发布日期"""
        try:
            # 尝试解析不同格式的日期
            for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S GMT']:
                try:
                    dt = datetime.strptime(published_str, fmt)
                    return dt.strftime('%m月%d日 %H:%M')
                except ValueError:
                    continue
            return published_str
        except:
            return published_str

    def get_widget_config(self) -> dict[str, Any]:
        """获取widget配置"""
        config = super().get_widget_config()
        config.update({
            'type': 'list',
            'refresh_interval': 600000  # 10分钟
        })
        return config