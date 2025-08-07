"""
Data Processor - Cleans and processes raw search results
"""

import logging
from typing import Dict, List, Any
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class DataProcessor:
    """Processes and cleans raw search result data"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        self.brand_variations = {
            'atomberg': ['atomberg', 'atom berg', 'atomburg', 'atombergs'],
            'havells': ['havells', 'havell', 'havels'],
            'orient': ['orient', 'oriental'],
            'bajaj': ['bajaj', 'bajaj electricals'],
            'crompton': ['crompton', 'crompton greaves'],
            'usha': ['usha', 'usha international'],
            'symphony': ['symphony', 'symphony air'],
            'voltas': ['voltas', 'voltas air']
        }
    
    def process_search_results(self, raw_results: Dict) -> Dict[str, Dict[str, List[Dict]]]:
        """
        Process raw search results from all platforms
        
        Args:
            raw_results: Raw search results organized by keyword and platform
            
        Returns:
            Processed and cleaned search results
        """
        logger.info("Processing search results...")
        
        processed_results = {}
        total_processed = 0
        
        for keyword, keyword_data in raw_results.items():
            processed_keyword_data = {}
            
            for platform, posts in keyword_data.items():
                processed_posts = []
                
                for post in posts:
                    processed_post = self._process_single_post(post)
                    if processed_post:  # Only include valid posts
                        processed_posts.append(processed_post)
                        total_processed += 1
                
                processed_keyword_data[platform] = processed_posts
                logger.info(f"Processed {len(processed_posts)} posts from {platform} for '{keyword}'")
            
            processed_results[keyword] = processed_keyword_data
        
        logger.info(f"Total processed posts: {total_processed}")
        return processed_results
    
    def _process_single_post(self, post: Dict) -> Dict[str, Any]:
        """Process a single post/result"""
        try:
            # Create a copy to avoid modifying original
            processed_post = post.copy()
            
            # Clean and standardize text content
            text_content = post.get('text_content', '')
            if not text_content:
                # Construct text content from available fields
                title = post.get('title', '')
                description = post.get('description', '')
                text = post.get('text', '')
                text_content = f"{title} {description} {text}".strip()
            
            processed_post['text_content'] = self._clean_text(text_content)
            
            # Standardize timestamps
            processed_post['processed_at'] = datetime.now().isoformat()
            
            # Enhanced brand mention detection
            processed_post['mentions_atomberg'] = self._detect_brand_mentions(
                processed_post['text_content'], 'atomberg'
            )
            processed_post['mentions_competitors'] = self._detect_competitor_mentions(
                processed_post['text_content']
            )
            
            # Extract keywords and themes
            processed_post['keywords'] = self._extract_keywords(processed_post['text_content'])
            processed_post['themes'] = self._identify_themes(processed_post['text_content'])
            
            # Standardize engagement metrics
            processed_post = self._standardize_engagement_metrics(processed_post)
            
            # Add derived metrics
            processed_post['content_length'] = len(processed_post['text_content'])
            processed_post['word_count'] = len(processed_post['text_content'].split())
            
            # Quality score based on content and engagement
            processed_post['quality_score'] = self._calculate_quality_score(processed_post)
            
            return processed_post
            
        except Exception as e:
            logger.error(f"Error processing post {post.get('id', 'unknown')}: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Convert to lowercase for processing
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Clean mentions and hashtags but preserve the text
        text = re.sub(r'[@#](\w+)', r'\1', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{3,}', '...', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\;:\-]', ' ', text)
        
        # Remove excessive whitespace again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _detect_brand_mentions(self, text: str, brand: str) -> bool:
        """Enhanced brand mention detection with variations"""
        if not text:
            return False
        
        brand_variations = self.brand_variations.get(brand.lower(), [brand.lower()])
        
        text_lower = text.lower()
        for variation in brand_variations:
            if variation in text_lower:
                return True
        
        return False
    
    def _detect_competitor_mentions(self, text: str) -> List[str]:
        """Detect all competitor brand mentions"""
        mentioned_competitors = []
        
        if not text:
            return mentioned_competitors
        
        text_lower = text.lower()
        
        for brand, variations in self.brand_variations.items():
            if brand == 'atomberg':  # Skip Atomberg as it's not a competitor
                continue
                
            for variation in variations:
                if variation in text_lower:
                    mentioned_competitors.append(brand.title())
                    break  # Avoid duplicates for same brand
        
        return mentioned_competitors
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        if not text:
            return []
        
        # Define relevant keywords for smart fan domain
        relevant_keywords = {
            'smart', 'intelligent', 'iot', 'wifi', 'bluetooth', 'app', 'remote', 'control',
            'energy', 'efficient', 'bldc', 'motor', 'speed', 'timer', 'alexa', 'google',
            'home', 'automation', 'ceiling', 'fan', 'quiet', 'silent', 'noise', 'review',
            'rating', 'price', 'cost', 'buy', 'purchase', 'install', 'setup', 'quality',
            'durable', 'warranty', 'service', 'support', 'compare', 'vs', 'versus',
            'best', 'top', 'recommended'
        }
        
        words = text.lower().split()
        found_keywords = []
        
        for word in words:
            # Remove punctuation from word
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in relevant_keywords and clean_word not in self.stop_words:
                if clean_word not in found_keywords:
                    found_keywords.append(clean_word)
        
        return found_keywords
    
    def _identify_themes(self, text: str) -> List[str]:
        """Identify content themes"""
        if not text:
            return []
        
        themes = []
        text_lower = text.lower()
        
        # Define theme patterns
        theme_patterns = {
            'review': ['review', 'rating', 'stars', 'feedback', 'opinion', 'experience'],
            'comparison': ['vs', 'versus', 'compare', 'comparison', 'better', 'best'],
            'technical': ['bldc', 'motor', 'rpm', 'watts', 'energy', 'efficiency', 'iot'],
            'installation': ['install', 'setup', 'mounting', 'wiring', 'assembly'],
            'purchase': ['buy', 'price', 'cost', 'deal', 'discount', 'sale', 'offer'],
            'support': ['service', 'support', 'warranty', 'customer', 'help'],
            'smart_features': ['smart', 'app', 'wifi', 'bluetooth', 'alexa', 'google', 'remote'],
            'performance': ['speed', 'quiet', 'silent', 'air', 'flow', 'cooling', 'noise']
        }
        
        for theme, keywords in theme_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _standardize_engagement_metrics(self, post: Dict) -> Dict:
        """Standardize engagement metrics across platforms"""
        platform = post.get('platform', '')
        
        # Initialize standard engagement fields
        engagement_fields = {
            'total_engagement': 0,
            'engagement_rate': 0.0,
            'reach_estimate': 0
        }
        
        if platform == 'youtube':
            views = post.get('views', 0)
            likes = post.get('likes', 0)
            comments = post.get('comments', 0)
            
            engagement_fields['total_engagement'] = likes + comments
            engagement_fields['reach_estimate'] = views
            if views > 0:
                engagement_fields['engagement_rate'] = (likes + comments) / views
        
        elif platform == 'twitter':
            retweets = post.get('retweets', 0)
            likes = post.get('likes', 0)
            replies = post.get('replies', 0)
            quotes = post.get('quotes', 0)
            followers = post.get('author_followers', 0)
            
            engagement_fields['total_engagement'] = retweets + likes + replies + quotes
            engagement_fields['reach_estimate'] = max(followers, engagement_fields['total_engagement'] * 10)
            if followers > 0:
                engagement_fields['engagement_rate'] = engagement_fields['total_engagement'] / followers
        
        elif platform == 'google':
            position = post.get('position', 10)
            page = post.get('page', 1)
            
            # Estimate engagement based on search position
            # Higher positions (lower numbers) get more estimated engagement
            estimated_clicks = max(100 - (position * 5) - (page * 20), 1)
            engagement_fields['total_engagement'] = estimated_clicks
            engagement_fields['reach_estimate'] = estimated_clicks * 10
            engagement_fields['engagement_rate'] = min(0.1, estimated_clicks / 1000)
        
        # Update post with standardized metrics
        post.update(engagement_fields)
        return post
    
    def _calculate_quality_score(self, post: Dict) -> float:
        """Calculate content quality score (0-1)"""
        score = 0.0
        factors = 0
        
        # Content length factor
        word_count = post.get('word_count', 0)
        if word_count > 0:
            # Optimal length is 50-200 words
            if 50 <= word_count <= 200:
                score += 1.0
            elif 20 <= word_count < 50 or 200 < word_count <= 300:
                score += 0.7
            elif word_count > 10:
                score += 0.3
            factors += 1
        
        # Engagement factor
        engagement_rate = post.get('engagement_rate', 0)
        if engagement_rate > 0:
            # Normalize engagement rate (cap at 0.1 for scoring)
            normalized_engagement = min(engagement_rate, 0.1) / 0.1
            score += normalized_engagement
            factors += 1
        
        # Theme relevance factor
        themes = post.get('themes', [])
        relevant_themes = ['review', 'comparison', 'technical', 'smart_features', 'performance']
        theme_score = len([t for t in themes if t in relevant_themes]) / len(relevant_themes)
        score += theme_score
        factors += 1
        
        # Keyword relevance factor
        keywords = post.get('keywords', [])
        if len(keywords) > 0:
            # More relevant keywords indicate higher quality
            keyword_score = min(len(keywords) / 10, 1.0)  # Cap at 10 keywords
            score += keyword_score
            factors += 1
        
        # Platform-specific quality factors
        platform = post.get('platform', '')
        if platform == 'google':
            position = post.get('position', 10)
            if position <= 3:
                score += 1.0
            elif position <= 10:
                score += 0.7
            else:
                score += 0.3
            factors += 1
        
        # Return average score
        return score / max(factors, 1)
