import httpx
import asyncio
import os
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import json
from datetime import datetime

class WikipediaClient:
    """Client for Wikipedia API integration"""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/api/rest_v1"
        self.search_url = "https://en.wikipedia.org/w/api.php"
    
    async def search_articles(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for articles on Wikipedia"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First, search for relevant page titles
                search_params = {
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": limit,
                    "srprop": "snippet|titlesnippet"
                }
                
                search_response = await client.get(self.search_url, params=search_params)
                search_response.raise_for_status()
                search_data = search_response.json()
                
                articles = []
                
                if "query" in search_data and "search" in search_data["query"]:
                    for result in search_data["query"]["search"][:limit]:
                        title = result["title"]
                        
                        # Get article content
                        content_url = f"{self.base_url}/page/summary/{quote(title)}"
                        content_response = await client.get(content_url)
                        
                        if content_response.status_code == 200:
                            content_data = content_response.json()
                            
                            articles.append({
                                "title": title,
                                "url": f"https://en.wikipedia.org/wiki/{quote(title)}",
                                "content": content_data.get("extract", ""),
                                "source": "Wikipedia"
                            })
                
                return articles
                
        except Exception as e:
            print(f"Wikipedia API error: {str(e)}")
            return []

class NewsAPIClient:
    """Client for NewsAPI integration"""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
    
    async def search_articles(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for news articles"""
        if not self.api_key:
            print("NewsAPI key not configured, skipping NewsAPI integration")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    "q": query,
                    "apiKey": self.api_key,
                    "language": "en",
                    "sortBy": "relevancy",
                    "pageSize": limit
                }
                
                response = await client.get(f"{self.base_url}/everything", params=params)
                response.raise_for_status()
                data = response.json()
                
                articles = []
                
                if data.get("status") == "ok" and "articles" in data:
                    for article in data["articles"][:limit]:
                        if article.get("title") and article.get("description"):
                            articles.append({
                                "title": article["title"],
                                "url": article.get("url", ""),
                                "content": article.get("description", "") + " " + (article.get("content", "") or ""),
                                "source": "NewsAPI"
                            })
                
                return articles
                
        except Exception as e:
            print(f"NewsAPI error: {str(e)}")
            return []

class HackerNewsClient:
    """Client for HackerNews API integration"""
    
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.algolia_url = "https://hn.algolia.com/api/v1"
    
    async def search_articles(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for HackerNews stories"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Use Algolia HN Search API for better search results
                params = {
                    "query": query,
                    "tags": "story",
                    "hitsPerPage": limit
                }
                
                response = await client.get(f"{self.algolia_url}/search", params=params)
                response.raise_for_status()
                data = response.json()
                
                articles = []
                
                if "hits" in data:
                    for hit in data["hits"][:limit]:
                        if hit.get("title"):
                            # Create content from title and any available text
                            content = hit.get("title", "")
                            if hit.get("story_text"):
                                content += " " + hit["story_text"]
                            
                            articles.append({
                                "title": hit["title"],
                                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                                "content": content,
                                "source": "HackerNews"
                            })
                
                return articles
                
        except Exception as e:
            print(f"HackerNews API error: {str(e)}")
            return []

class RedditClient:
    """Client for Reddit API integration (no API key required for public posts)"""
    
    def __init__(self):
        self.base_url = "https://www.reddit.com"
    
    async def search_articles(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for Reddit posts"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Search across multiple relevant subreddits
                subreddits = ["technology", "science", "news", "worldnews", "todayilearned"]
                articles = []
                
                for subreddit in subreddits:
                    if len(articles) >= limit:
                        break
                    
                    url = f"{self.base_url}/r/{subreddit}/search.json"
                    params = {
                        "q": query,
                        "restrict_sr": "1",
                        "sort": "relevance",
                        "limit": 2
                    }
                    
                    headers = {
                        "User-Agent": "AI Research Agent 1.0"
                    }
                    
                    response = await client.get(url, params=params, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if "data" in data and "children" in data["data"]:
                            for post in data["data"]["children"]:
                                post_data = post.get("data", {})
                                
                                if post_data.get("title") and not post_data.get("is_self", False):
                                    articles.append({
                                        "title": post_data["title"],
                                        "url": post_data.get("url", f"https://reddit.com{post_data.get('permalink', '')}"),
                                        "content": post_data.get("selftext", "") or post_data.get("title", ""),
                                        "source": f"Reddit r/{subreddit}"
                                    })
                                    
                                    if len(articles) >= limit:
                                        break
                
                return articles[:limit]
                
        except Exception as e:
            print(f"Reddit API error: {str(e)}")
            return []

class ExternalAPIManager:
    """Manager class to coordinate multiple external API clients"""
    
    def __init__(self):
        self.clients = {
            "wikipedia": WikipediaClient(),
            "newsapi": NewsAPIClient(),
            "hackernews": HackerNewsClient(),
            "reddit": RedditClient()
        }
    
    async def fetch_articles(self, query: str, total_limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch articles from multiple sources"""
        articles_per_source = max(2, total_limit // len(self.clients))
        all_articles = []
        
        # Create tasks for concurrent API calls
        tasks = []
        for client_name, client in self.clients.items():
            task = asyncio.create_task(
                client.search_articles(query, articles_per_source),
                name=client_name
            )
            tasks.append(task)
        
        # Wait for all API calls to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results from all sources
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error from {list(self.clients.keys())[i]}: {result}")
                continue
            
            if isinstance(result, list):
                all_articles.extend(result)
        
        # Remove duplicates based on title similarity
        unique_articles = self._remove_duplicates(all_articles)
        
        # Return up to the requested limit
        return unique_articles[:total_limit]
    
    def _remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title = article.get("title", "").lower().strip()
            
            # Simple duplicate detection based on title
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        return unique_articles
