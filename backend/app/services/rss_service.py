"""
RSS Feed Service
經濟通 RSS 抓取服務
"""
import aiohttp
import feedparser
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class RSSService:
    """Fetch and parse RSS feeds from etnet"""
    
    def __init__(self):
        self.feeds = {
            "rumour": "https://www.etnet.com.hk/www/tc/news/rss.php?section=rumour",
            "instant_news": "https://www.etnet.com.hk/www/tc/news/rss.php?section=instant_news",
            "stock": "https://www.etnet.com.hk/www/tc/stocks/rss.php?section=realtime_news",
            "tech": "https://www.etnet.com.hk/www/tc/news/rss.php?section=technology",
        }
    
    async def fetch_feed(self, category: str = "rumour", limit: int = 10) -> List[Dict]:
        """
        Fetch RSS feed
        
        Args:
            category: Feed category (rumour/instant_news/stock/tech)
            limit: Max number of items to return
            
        Returns:
            List of news items
        """
        feed_url = self.feeds.get(category, self.feeds["rumour"])
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_url, timeout=10) as response:
                    if response.status == 200:
                        rss_data = await response.text()
                        return self._parse_feed(rss_data, limit)
                    else:
                        print(f"[RSS] Error fetching {category}: {response.status}")
                        return []
        except Exception as e:
            print(f"[RSS] Exception: {e}")
            return []
    
    def _parse_feed(self, rss_data: str, limit: int) -> List[Dict]:
        """Parse RSS XML data"""
        feed = feedparser.parse(rss_data)
        
        news_items = []
        for entry in feed.entries[:limit]:
            # Extract publish time
            published = None
            if hasattr(entry, 'published_parsed'):
                try:
                    published = datetime(*entry.published_parsed[:6])
                except:
                    published = datetime.now()
            
            # Clean content
            content = entry.get('description', '')
            if not content and hasattr(entry, 'summary'):
                content = entry.summary
            
            # Remove HTML tags
            content = self._clean_html(content)
            
            news_items.append({
                "title": entry.title,
                "link": entry.link,
                "content": content,
                "published": published.isoformat() if published else None,
                "source": "經濟通",
                "category": "财经"
            })
        
        return news_items
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        import re
        # Remove HTML tags
        clean = re.sub('<.*?>', '', text)
        # Remove extra whitespace
        clean = ' '.join(clean.split())
        return clean
    
    async def get_latest_news(self, categories: List[str] = None, total_limit: int = 20) -> List[Dict]:
        """
        Get latest news from multiple categories
        
        Args:
            categories: List of categories to fetch
            total_limit: Total max items across all categories
            
        Returns:
            Combined and sorted list of news items
        """
        if not categories:
            categories = ["rumour", "instant_news", "tech"]
        
        all_news = []
        for category in categories:
            news = await self.fetch_feed(category, limit=total_limit // len(categories))
            all_news.extend(news)
        
        # Sort by published time (newest first)
        all_news.sort(
            key=lambda x: x['published'] if x['published'] else '',
            reverse=True
        )
        
        return all_news[:total_limit]


# Global RSS service instance
rss_service = RSSService()
