"""
Search Agent - Orchestrates searches across multiple platforms
"""

import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from .youtube_scraper import YouTubeScraper
from .twitter_scraper import TwitterScraper
from .google_scraper import GoogleScraper

logger = logging.getLogger(__name__)

class SearchAgent:
    """Orchestrates search operations across multiple platforms"""
    
    def __init__(self, config):
        self.config = config
        self.scrapers = {
            'youtube': YouTubeScraper(config),
            'twitter': TwitterScraper(config),
            'google': GoogleScraper(config)
        }
    
    def search_platform(self, platform: str, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search a specific platform for the given query
        
        Args:
            platform: Platform name ('youtube', 'twitter', 'google')
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        if platform not in self.scrapers:
            raise ValueError(f"Unsupported platform: {platform}")
        
        scraper = self.scrapers[platform]
        try:
            results = scraper.search(query, max_results)
            logger.info(f"Successfully collected {len(results)} results from {platform}")
            return results
        except Exception as e:
            logger.error(f"Error searching {platform}: {str(e)}")
            return []
    
    def search_all_platforms(self, query: str, platforms: List[str], max_results: int = 50) -> Dict[str, List[Dict]]:
        """
        Search multiple platforms simultaneously
        
        Args:
            query: Search query
            platforms: List of platforms to search
            max_results: Maximum results per platform
            
        Returns:
            Dictionary with platform names as keys and results as values
        """
        results = {}
        
        # Use ThreadPoolExecutor for parallel searches
        with ThreadPoolExecutor(max_workers=len(platforms)) as executor:
            # Submit search tasks
            future_to_platform = {
                executor.submit(self.search_platform, platform, query, max_results): platform
                for platform in platforms if platform in self.scrapers
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    platform_results = future.result()
                    results[platform] = platform_results
                except Exception as e:
                    logger.error(f"Error collecting results from {platform}: {str(e)}")
                    results[platform] = []
        
        return results
    
    def get_supported_platforms(self) -> List[str]:
        """Return list of supported platforms"""
        return list(self.scrapers.keys())
