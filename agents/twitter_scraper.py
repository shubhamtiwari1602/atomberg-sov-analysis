"""
Twitter/X Scraper - Collects data from Twitter/X search results
"""

import logging
import time
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class TwitterScraper:
    """Scraper for Twitter/X posts and engagement data"""
    
    def __init__(self, config):
        self.config = config
        self.api_key = getattr(config, 'TWITTER_API_KEY', None)
        self.api_secret = getattr(config, 'TWITTER_API_SECRET', None)
        self.access_token = getattr(config, 'TWITTER_ACCESS_TOKEN', None)
        self.access_token_secret = getattr(config, 'TWITTER_ACCESS_TOKEN_SECRET', None)
        self.bearer_token = getattr(config, 'TWITTER_BEARER_TOKEN', None)
        
        # Initialize Twitter API client if credentials are available
        self.client = None
        if self.bearer_token:
            try:
                import tweepy
                self.client = tweepy.Client(bearer_token=self.bearer_token)
            except ImportError:
                logger.warning("Tweepy not available, using web scraping")
            except Exception as e:
                logger.warning(f"Failed to initialize Twitter API: {e}")
    
    def search(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search Twitter/X for posts related to the query
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of post data dictionaries
        """
        if self.client:
            return self._search_with_api(query, max_results)
        else:
            return self._search_with_scraping(query, max_results)
    
    def _search_with_api(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Twitter API v2"""
        try:
            # Search for tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),  # API limit
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations', 'lang'],
                user_fields=['username', 'name', 'public_metrics'],
                expansions=['author_id']
            )
            
            posts = []
            
            if tweets.data:
                # Create user lookup
                users = {user.id: user for user in tweets.includes.get('users', [])}
                
                for tweet in tweets.data:
                    author = users.get(tweet.author_id)
                    metrics = tweet.public_metrics
                    
                    post_data = {
                        'platform': 'twitter',
                        'id': tweet.id,
                        'text': tweet.text,
                        'author': author.username if author else 'unknown',
                        'author_name': author.name if author else 'Unknown',
                        'author_followers': author.public_metrics['followers_count'] if author else 0,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else '',
                        'url': f"https://twitter.com/user/status/{tweet.id}",
                        'retweets': metrics.get('retweet_count', 0),
                        'likes': metrics.get('like_count', 0),
                        'replies': metrics.get('reply_count', 0),
                        'quotes': metrics.get('quote_count', 0),
                        'engagement_rate': 0.0,
                        'mentions_atomberg': False,
                        'mentions_competitors': [],
                        'text_content': tweet.text,
                        'language': getattr(tweet, 'lang', 'en')
                    }
                    
                    # Calculate engagement rate
                    if post_data['author_followers'] > 0:
                        total_engagement = (post_data['retweets'] + post_data['likes'] + 
                                          post_data['replies'] + post_data['quotes'])
                        post_data['engagement_rate'] = total_engagement / post_data['author_followers']
                    
                    # Analyze brand mentions
                    post_data['mentions_atomberg'] = self._check_brand_mentions(tweet.text, 'atomberg')
                    post_data['mentions_competitors'] = self._find_competitor_mentions(tweet.text)
                    
                    posts.append(post_data)
            
            logger.info(f"Collected {len(posts)} tweets using Twitter API")
            return posts
            
        except Exception as e:
            logger.error(f"Error in Twitter API search: {e}")
            return self._search_with_scraping(query, max_results)
    
    def _search_with_scraping(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback web scraping method (limited due to Twitter's restrictions)"""
        logger.info("Using mock data for Twitter search (API access limited)")
        
        # Note: Twitter heavily restricts web scraping, so we'll generate mock data
        # In a real implementation, you'd need proper API access or alternative data sources
        return self._generate_mock_data(query, max_results)
    
    def _generate_mock_data(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock Twitter data for demonstration"""
        logger.info("Generating mock Twitter data for demonstration")
        
        posts = []
        hashtags = ['#smartfan', '#smarthome', '#IoT', '#ceilingfan', '#hometech']
        competitors = ['Havells', 'Orient', 'Bajaj', 'Crompton', 'Usha']
        
        sample_tweets = [
            "Just installed my new smart fan from {} - the app control is amazing! #smartfan #smarthome",
            "Comparing smart ceiling fans - {} vs {} vs {}. Which one should I choose? #help",
            "My {} smart fan broke after 6 months 😞 Looking for better alternatives #smartfan",
            "Review: {} Smart Fan - 5 stars! Energy efficient and whisper quiet operation",
            "Smart home setup complete! {} fan integrated with Alexa perfectly #smarthome #IoT",
            "Disappointed with {} customer service. Fan making noise after 3 months 😡",
            "Best smart fan deals this month? Looking at {} and {} models",
            "Weather's getting hot! Time to upgrade to a {} smart fan with IoT controls",
            "Energy bill reduced by 30% after switching to {} smart fans! Highly recommend",
            "Installation review: {} smart fan - easy setup, great app interface #review"
        ]
        
        for i in range(min(max_results, 30)):  # Limit mock data
            # Randomly select brands for the tweet
            brand_mentions = []
            mentions_atomberg = False
            
            if i % 4 == 0:  # Every 4th tweet mentions Atomberg
                brand_mentions.append('Atomberg')
                mentions_atomberg = True
            
            # Add some competitor mentions
            if i % 3 == 0:
                brand_mentions.extend([competitors[i % len(competitors)]])
            
            # Format tweet text
            tweet_template = sample_tweets[i % len(sample_tweets)]
            if len(brand_mentions) == 1:
                tweet_text = tweet_template.format(brand_mentions[0])
            elif len(brand_mentions) >= 3:
                tweet_text = tweet_template.format(brand_mentions[0], brand_mentions[1], brand_mentions[2])
            else:
                tweet_text = tweet_template.format(*brand_mentions, *['SomeBrand'] * (3 - len(brand_mentions)))
            
            # Add hashtag
            tweet_text += f" {hashtags[i % len(hashtags)]}"
            
            post_data = {
                'platform': 'twitter',
                'id': f'mock_tw_{i}',
                'text': tweet_text,
                'author': f'user_{i+1}',
                'author_name': f'Smart Home User {i+1}',
                'author_followers': 500 + (i * 100),
                'created_at': '2024-01-01T00:00:00Z',
                'url': f'https://twitter.com/user_{i+1}/status/mock_{i}',
                'retweets': 5 + (i % 20),
                'likes': 15 + (i % 50),
                'replies': 2 + (i % 10),
                'quotes': 1 + (i % 5),
                'engagement_rate': (5 + i % 20 + 15 + i % 50 + 2 + i % 10 + 1 + i % 5) / (500 + i * 100),
                'mentions_atomberg': mentions_atomberg,
                'mentions_competitors': [brand for brand in brand_mentions if brand != 'Atomberg'],
                'text_content': tweet_text,
                'language': 'en'
            }
            
            posts.append(post_data)
        
        return posts
    
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
