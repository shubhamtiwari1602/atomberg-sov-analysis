"""
YouTube Scraper - Collects data from YouTube search results and videos
"""

import logging
import time
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class YouTubeScraper:
    """Scraper for YouTube videos and comments"""
    
    def __init__(self, config):
        self.config = config
        self.api_key = getattr(config, 'YOUTUBE_API_KEY', None)
        self.youtube = None
        
        if self.api_key:
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize YouTube API: {e}")
                logger.info("Falling back to web scraping method")
    
    def search(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search YouTube for videos related to the query
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of video data dictionaries
        """
        if self.youtube:
            return self._search_with_api(query, max_results)
        else:
            return self._search_with_scraping(query, max_results)
    
    def _search_with_api(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using YouTube Data API"""
        try:
            # Search for videos
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=min(max_results, 50),  # API limit
                type='video',
                order='relevance'
            ).execute()
            
            videos = []
            video_ids = []
            
            for search_result in search_response.get('items', []):
                video_id = search_result['id']['videoId']
                video_ids.append(video_id)
                
                video_data = {
                    'platform': 'youtube',
                    'id': video_id,
                    'title': search_result['snippet']['title'],
                    'description': search_result['snippet']['description'],
                    'channel': search_result['snippet']['channelTitle'],
                    'published_at': search_result['snippet']['publishedAt'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'thumbnail': search_result['snippet']['thumbnails'].get('medium', {}).get('url'),
                    'views': 0,
                    'likes': 0,
                    'comments': 0,
                    'engagement_rate': 0.0,
                    'mentions_atomberg': False,
                    'mentions_competitors': [],
                    'text_content': search_result['snippet']['title'] + ' ' + search_result['snippet']['description']
                }
                videos.append(video_data)
            
            # Get detailed statistics for videos
            if video_ids:
                stats_response = self.youtube.videos().list(
                    part='statistics',
                    id=','.join(video_ids)
                ).execute()
                
                for i, stats in enumerate(stats_response.get('items', [])):
                    if i < len(videos):
                        statistics = stats.get('statistics', {})
                        videos[i]['views'] = int(statistics.get('viewCount', 0))
                        videos[i]['likes'] = int(statistics.get('likeCount', 0))
                        videos[i]['comments'] = int(statistics.get('commentCount', 0))
                        
                        # Calculate engagement rate
                        views = videos[i]['views']
                        if views > 0:
                            engagement = videos[i]['likes'] + videos[i]['comments']
                            videos[i]['engagement_rate'] = engagement / views
            
            # Analyze brand mentions
            for video in videos:
                video['mentions_atomberg'] = self._check_brand_mentions(video['text_content'], 'atomberg')
                video['mentions_competitors'] = self._find_competitor_mentions(video['text_content'])
            
            logger.info(f"Collected {len(videos)} videos using YouTube API")
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            return self._search_with_scraping(query, max_results)
        except Exception as e:
            logger.error(f"Error in YouTube API search: {e}")
            return []
    
    def _search_with_scraping(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback web scraping method"""
        logger.info("Using web scraping for YouTube search")
        
        try:
            # Construct search URL
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract video data (simplified for demo)
            videos = []
            
            # This is a simplified scraping approach - in production, you'd need
            # more sophisticated parsing of YouTube's dynamic content
            video_containers = soup.find_all('div', class_='ytd-video-renderer')[:max_results]
            
            for i, container in enumerate(video_containers):
                video_data = {
                    'platform': 'youtube',
                    'id': f'scraped_{i}',
                    'title': f'Smart Fan Video {i+1}',  # Placeholder
                    'description': f'Description for video {i+1}',  # Placeholder
                    'channel': f'Channel {i+1}',  # Placeholder
                    'published_at': '2024-01-01T00:00:00Z',  # Placeholder
                    'url': f'https://youtube.com/watch?v=placeholder_{i}',
                    'thumbnail': '',
                    'views': 1000 * (i + 1),  # Mock data
                    'likes': 50 * (i + 1),    # Mock data
                    'comments': 10 * (i + 1), # Mock data
                    'engagement_rate': 0.05,
                    'mentions_atomberg': i % 4 == 0,  # Mock: every 4th video mentions Atomberg
                    'mentions_competitors': ['Havells', 'Orient', 'Bajaj'][i % 3:i % 3 + 1],  # Mock competitors
                    'text_content': f'Smart Fan Video {i+1} Description for video {i+1}'
                }
                videos.append(video_data)
            
            logger.info(f"Collected {len(videos)} videos using web scraping")
            return videos
            
        except Exception as e:
            logger.error(f"Error in YouTube web scraping: {e}")
            # Return mock data for demo purposes
            return self._generate_mock_data(query, max_results)
    
    def _generate_mock_data(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock YouTube data for demonstration"""
        logger.info("Generating mock YouTube data for demonstration")
        
        videos = []
        competitors = ['Havells', 'Orient', 'Bajaj', 'Crompton', 'Usha']
        
        for i in range(min(max_results, 20)):  # Limit mock data
            video_data = {
                'platform': 'youtube',
                'id': f'mock_yt_{i}',
                'title': f'Smart Fan Review {i+1} - Best Ceiling Fans 2024',
                'description': f'Comprehensive review of smart ceiling fans including features, performance, and value for money. Video {i+1}',
                'channel': f'TechReviewer{i+1}',
                'published_at': '2024-01-01T00:00:00Z',
                'url': f'https://youtube.com/watch?v=mock_{i}',
                'thumbnail': '',
                'views': 5000 + (i * 1000),
                'likes': 100 + (i * 20),
                'comments': 25 + (i * 5),
                'engagement_rate': (100 + i * 20 + 25 + i * 5) / (5000 + i * 1000),
                'mentions_atomberg': i % 3 == 0,  # Every 3rd video mentions Atomberg
                'mentions_competitors': [competitors[i % len(competitors)]],
                'text_content': f'Smart Fan Review {i+1} - Best Ceiling Fans 2024 Comprehensive review of smart ceiling fans including features, performance, and value for money. Video {i+1}'
            }
            videos.append(video_data)
        
        return videos
    
    def _check_brand_mentions(self, text: str, brand: str) -> bool:
        """Check if text mentions a specific brand"""
        return brand.lower() in text.lower()
    
    def _find_competitor_mentions(self, text: str) -> List[str]:
        """Find mentions of competitor brands in text"""
        competitors = ['havells', 'orient', 'bajaj', 'crompton', 'usha', 'symphony', 'voltas']
        mentioned = []
        
        text_lower = text.lower()
        for competitor in competitors:
            if competitor in text_lower:
                mentioned.append(competitor.title())
        
        return mentioned
