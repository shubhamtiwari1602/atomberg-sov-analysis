"""
Configuration settings for Atomberg SoV Analysis Agent
"""

import os
from typing import List

class Config:
    """Configuration class for the SoV analysis agent"""
    
    def __init__(self):
        # API Keys (to be set via environment variables)
        self.YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', None)
        self.TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', None)
        self.TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', None)
        self.TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', None)
        self.TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', None)
        self.TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', None)
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
        
        # Scraping Settings
        self.SCRAPING_DELAY = 2  # Seconds between requests
        self.MAX_RETRIES = 3
        self.REQUEST_TIMEOUT = 10  # Seconds
        
        # User Agent for web scraping
        self.USER_AGENT = (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        )
        
        # Competitor brands to track
        self.COMPETITORS = [
            'Havells', 'Orient', 'Bajaj', 'Crompton', 'Usha', 
            'Symphony', 'Voltas', 'Khaitan', 'Luminous'
        ]
        
        # Keywords to analyze (can be extended)
        self.DEFAULT_KEYWORDS = [
            'smart fan', 'smart ceiling fan', 'IoT fan', 'wifi fan',
            'intelligent fan', 'BLDC fan', 'energy efficient fan'
        ]
        
        # Platform-specific settings
        self.PLATFORM_SETTINGS = {
            'youtube': {
                'max_results_per_request': 50,
                'include_comments': True,
                'max_comments_per_video': 20
            },
            'twitter': {
                'max_results_per_request': 100,
                'include_retweets': True,
                'tweet_fields': ['created_at', 'author_id', 'public_metrics', 'lang']
            },
            'google': {
                'max_pages': 5,
                'results_per_page': 10,
                'include_ads': False
            }
        }
        
        # Analysis settings
        self.ANALYSIS_SETTINGS = {
            'sentiment_threshold': 0.1,  # Minimum confidence for sentiment classification
            'min_engagement_for_quality': 10,  # Minimum engagement for quality posts
            'relevance_keywords': [
                'smart', 'ceiling', 'fan', 'BLDC', 'energy', 'efficient',
                'remote', 'app', 'wifi', 'IoT', 'motor', 'speed', 'quiet'
            ]
        }
        
        # Output settings
        self.OUTPUT_SETTINGS = {
            'save_raw_data': True,
            'create_visualizations': True,
            'generate_report': True,
            'export_formats': ['json', 'csv', 'txt']
        }
        
        # Brand mention patterns (case insensitive)
        self.BRAND_PATTERNS = {
            'atomberg': [
                'atomberg', 'atom berg', 'atomburg', '@atomberg',
                'atomberg fan', 'atomberg ceiling fan'
            ],
            'havells': [
                'havells', 'havell', '@havells', 'havells fan',
                'havells ceiling fan', 'havells smart fan'
            ],
            'orient': [
                'orient', 'orient fan', 'orient electric', '@orient',
                'orient ceiling fan', 'orient smart fan'
            ],
            'bajaj': [
                'bajaj', 'bajaj fan', 'bajaj electricals', '@bajaj',
                'bajaj ceiling fan', 'bajaj smart fan'
            ],
            'crompton': [
                'crompton', 'crompton greaves', '@crompton',
                'crompton fan', 'crompton ceiling fan'
            ],
            'usha': [
                'usha', 'usha international', '@usha',
                'usha fan', 'usha ceiling fan'
            ]
        }
        
        # Quality scoring weights
        self.QUALITY_WEIGHTS = {
            'content_length': 0.2,
            'engagement_rate': 0.3,
            'theme_relevance': 0.2,
            'keyword_relevance': 0.2,
            'platform_authority': 0.1
        }
        
        # SoV calculation weights
        self.SOV_WEIGHTS = {
            'mention_share': 0.4,
            'engagement_share': 0.4,
            'sentiment_share': 0.2
        }
    
    def get_platform_config(self, platform: str) -> dict:
        """Get configuration for a specific platform"""
        return self.PLATFORM_SETTINGS.get(platform, {})
    
    def get_brand_patterns(self, brand: str) -> List[str]:
        """Get search patterns for a specific brand"""
        return self.BRAND_PATTERNS.get(brand.lower(), [brand])
    
    def validate_config(self) -> bool:
        """Validate configuration settings"""
        issues = []
        
        # Check if at least some API keys are available
        api_keys_available = any([
            self.YOUTUBE_API_KEY,
            self.TWITTER_BEARER_TOKEN,
            # Google search doesn't require API key for basic scraping
        ])
        
        if not api_keys_available:
            issues.append("No API keys configured - will use mock data for demonstration")
        
        # Check competitors list
        if not self.COMPETITORS:
            issues.append("No competitors defined")
        
        # Check keywords
        if not self.DEFAULT_KEYWORDS:
            issues.append("No default keywords defined")
        
        if issues:
            print("Configuration issues found:")
            for issue in issues:
                print(f"- {issue}")
            return False
        
        return True
    
    def get_environment_info(self) -> dict:
        """Get information about the current environment"""
        return {
            'youtube_api_available': bool(self.YOUTUBE_API_KEY),
            'twitter_api_available': bool(self.TWITTER_BEARER_TOKEN),
            'openai_api_available': bool(self.OPENAI_API_KEY),
            'competitors_count': len(self.COMPETITORS),
            'default_keywords_count': len(self.DEFAULT_KEYWORDS)
        }
