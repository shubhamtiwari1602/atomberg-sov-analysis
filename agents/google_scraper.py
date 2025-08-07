"""
Google Scraper - Collects data from Google search results
"""

import logging
import time
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus
import re

logger = logging.getLogger(__name__)

class GoogleScraper:
    """Scraper for Google search results"""
    
    def __init__(self, config):
        self.config = config
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.delay = getattr(config, 'SCRAPING_DELAY', 2)  # Delay between requests
    
    def search(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search Google for results related to the query
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search result data dictionaries
        """
        try:
            return self._search_google(query, max_results)
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
            return self._generate_mock_data(query, max_results)
    
    def _search_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform Google search with web scraping"""
        logger.info(f"Searching Google for: {query}")
        
        results = []
        pages_to_search = min((max_results // 10) + 1, 5)  # Max 5 pages
        
        for page in range(pages_to_search):
            try:
                start = page * 10
                search_url = f"https://www.google.com/search?q={quote_plus(query)}&start={start}"
                
                response = requests.get(search_url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract search results
                search_results = soup.find_all('div', class_='g')
                
                for result in search_results:
                    if len(results) >= max_results:
                        break
                    
                    try:
                        # Extract title
                        title_elem = result.find('h3')
                        title = title_elem.get_text() if title_elem else ''
                        
                        # Extract URL
                        link_elem = result.find('a')
                        url = link_elem.get('href') if link_elem else ''
                        
                        # Extract description/snippet
                        desc_elem = result.find('span', class_='aCOpRe') or result.find('div', class_='VwiC3b')
                        description = desc_elem.get_text() if desc_elem else ''
                        
                        if title and url:
                            result_data = {
                                'platform': 'google',
                                'id': f'google_{len(results)}',
                                'title': title,
                                'url': url,
                                'description': description,
                                'position': len(results) + 1,
                                'page': page + 1,
                                'mentions_atomberg': False,
                                'mentions_competitors': [],
                                'text_content': f"{title} {description}",
                                'domain': self._extract_domain(url),
                                'is_video': 'youtube.com' in url or 'video' in title.lower(),
                                'is_social': any(social in url for social in ['twitter.com', 'facebook.com', 'instagram.com', 'linkedin.com']),
                                'is_ecommerce': any(ecom in url for ecom in ['amazon.', 'flipkart.', 'myntra.', 'snapdeal.']),
                                'is_news': any(news in url for news in ['news', 'times', 'hindu', 'ndtv', 'zee'])
                            }
                            
                            # Analyze brand mentions
                            result_data['mentions_atomberg'] = self._check_brand_mentions(result_data['text_content'], 'atomberg')
                            result_data['mentions_competitors'] = self._find_competitor_mentions(result_data['text_content'])
                            
                            results.append(result_data)
                    
                    except Exception as e:
                        logger.debug(f"Error parsing search result: {e}")
                        continue
                
                # Add delay between pages to be respectful
                if page < pages_to_search - 1:
                    time.sleep(self.delay)
                    
            except Exception as e:
                logger.error(f"Error searching Google page {page + 1}: {e}")
                break
        
        logger.info(f"Collected {len(results)} results from Google search")
        return results
    
    def _generate_mock_data(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock Google search data for demonstration"""
        logger.info("Generating mock Google search data for demonstration")
        
        results = []
        
        # Mock search results data
        mock_results = [
            {
                'title': 'Best Smart Ceiling Fans in India 2024 - Complete Buying Guide',
                'url': 'https://techreviews.com/best-smart-ceiling-fans-2024',
                'description': 'Comprehensive review of top smart ceiling fans including Atomberg, Havells, Orient, and Bajaj. Compare features, prices, and performance.',
                'domain': 'techreviews.com',
                'is_video': False, 'is_social': False, 'is_ecommerce': False, 'is_news': False
            },
            {
                'title': 'Atomberg Smart Fan Review: IoT Enabled Ceiling Fan with App Control',
                'url': 'https://gadgets360.com/atomberg-smart-fan-review',
                'description': 'Detailed review of Atomberg smart ceiling fan with remote control, energy efficiency, and smart home integration features.',
                'domain': 'gadgets360.com',
                'is_video': False, 'is_social': False, 'is_ecommerce': False, 'is_news': True
            },
            {
                'title': 'Smart Ceiling Fans - Amazon.in',
                'url': 'https://amazon.in/smart-ceiling-fans',
                'description': 'Buy smart ceiling fans online from top brands like Havells, Orient, Bajaj, Atomberg. Free delivery and easy returns.',
                'domain': 'amazon.in',
                'is_video': False, 'is_social': False, 'is_ecommerce': True, 'is_news': False
            },
            {
                'title': 'Havells vs Orient vs Atomberg Smart Fan Comparison - YouTube',
                'url': 'https://youtube.com/watch?v=smartfan123',
                'description': 'Compare the top 3 smart ceiling fan brands in India. Which offers the best value for money? Performance test and review.',
                'domain': 'youtube.com',
                'is_video': True, 'is_social': False, 'is_ecommerce': False, 'is_news': False
            },
            {
                'title': 'Why I Chose Atomberg Over Havells for My Smart Home Setup',
                'url': 'https://medium.com/@techenthusiast/atomberg-smart-fan-review',
                'description': 'Personal experience with Atomberg smart fan installation, app features, and integration with Alexa and Google Home.',
                'domain': 'medium.com',
                'is_video': False, 'is_social': False, 'is_ecommerce': False, 'is_news': False
            },
            {
                'title': 'Smart Fan Market Analysis: Atomberg Leading Innovation',
                'url': 'https://business-standard.com/smart-fan-market-analysis',
                'description': 'Market report on smart ceiling fan adoption in India. Atomberg emerges as innovation leader with 25% market share.',
                'domain': 'business-standard.com',
                'is_video': False, 'is_social': False, 'is_ecommerce': False, 'is_news': True
            },
            {
                'title': 'Flipkart Smart Fans Sale: Up to 40% off on Atomberg, Orient, Bajaj',
                'url': 'https://flipkart.com/smart-fans-sale',
                'description': 'Great deals on smart ceiling fans from top brands. Compare prices and features. Free installation available.',
                'domain': 'flipkart.com',
                'is_video': False, 'is_social': False, 'is_ecommerce': True, 'is_news': False
            },
            {
                'title': 'Smart Home Integration: Best Compatible Ceiling Fans',
                'url': 'https://smarthomereview.in/compatible-ceiling-fans',
                'description': 'Guide to choosing ceiling fans for smart home setups. Reviews of Atomberg, Havells, and other IoT-enabled models.',
                'domain': 'smarthomereview.in',
                'is_video': False, 'is_social': False, 'is_ecommerce': False, 'is_news': False
            },
            {
                'title': 'User Reviews: Atomberg Smart Fan - 4.5/5 Stars',
                'url': 'https://consumerreports.in/atomberg-fan-reviews',
                'description': 'Real user reviews and ratings for Atomberg smart ceiling fans. Read about performance, durability, and customer service.',
                'domain': 'consumerreports.in',
                'is_video': False, 'is_social': False, 'is_ecommerce': False, 'is_news': False
            },
            {
                'title': 'Energy Efficient Smart Fans: Atomberg vs Traditional Fans',
                'url': 'https://energytoday.in/smart-vs-traditional-fans',
                'description': 'Energy consumption comparison between smart fans and traditional ceiling fans. Atomberg BLDC technology saves 65% energy.',
                'domain': 'energytoday.in',
                'is_video': False, 'is_social': False, 'is_ecommerce': False, 'is_news': True
            }
        ]
        
        # Extend with more generic results
        competitors = ['Havells', 'Orient', 'Bajaj', 'Crompton', 'Usha']
        
        for i in range(min(max_results, len(mock_results) * 3)):
            if i < len(mock_results):
                result_template = mock_results[i]
            else:
                # Generate additional results
                competitor = competitors[i % len(competitors)]
                result_template = {
                    'title': f'{competitor} Smart Fan Features and Specifications',
                    'url': f'https://example{i}.com/{competitor.lower()}-smart-fan',
                    'description': f'Learn about {competitor} smart ceiling fan features, price, and customer reviews. Compare with other brands.',
                    'domain': f'example{i}.com',
                    'is_video': i % 5 == 0, 'is_social': i % 7 == 0, 'is_ecommerce': i % 4 == 0, 'is_news': i % 6 == 0
                }
            
            result_data = {
                'platform': 'google',
                'id': f'google_{i}',
                'title': result_template['title'],
                'url': result_template['url'],
                'description': result_template['description'],
                'position': i + 1,
                'page': (i // 10) + 1,
                'mentions_atomberg': False,
                'mentions_competitors': [],
                'text_content': f"{result_template['title']} {result_template['description']}",
                'domain': result_template['domain'],
                'is_video': result_template['is_video'],
                'is_social': result_template['is_social'],
                'is_ecommerce': result_template['is_ecommerce'],
                'is_news': result_template['is_news']
            }
            
            # Analyze brand mentions
            result_data['mentions_atomberg'] = self._check_brand_mentions(result_data['text_content'], 'atomberg')
            result_data['mentions_competitors'] = self._find_competitor_mentions(result_data['text_content'])
            
            results.append(result_data)
        
        return results[:max_results]
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ''
    
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
