"""
Sentiment Analyzer - Performs sentiment analysis on social media posts
"""

import logging
from typing import Dict, List, Any, Union
import re

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Sentiment analysis for social media posts and content"""
    
    def __init__(self):
        self.sentiment_lexicon = None
        self.vader_analyzer = None
        self.textblob_available = False
        
        # Try to initialize sentiment analysis tools
        self._initialize_analyzers()
    
    def _initialize_analyzers(self):
        """Initialize available sentiment analysis tools"""
        # Try VADER sentiment analyzer
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self.vader_analyzer = SentimentIntensityAnalyzer()
            logger.info("VADER sentiment analyzer initialized")
        except ImportError:
            logger.warning("VADER sentiment analyzer not available")
        
        # Try TextBlob
        try:
            from textblob import TextBlob
            self.textblob_available = True
            logger.info("TextBlob sentiment analyzer initialized")
        except ImportError:
            logger.warning("TextBlob not available")
        
        # Initialize simple lexicon-based analyzer as fallback
        self._initialize_simple_lexicon()
    
    def _initialize_simple_lexicon(self):
        """Initialize simple sentiment lexicon for fallback"""
        self.positive_words = {
            'excellent', 'amazing', 'great', 'fantastic', 'wonderful', 'awesome', 
            'outstanding', 'superb', 'brilliant', 'perfect', 'best', 'love', 'like',
            'good', 'nice', 'happy', 'satisfied', 'recommend', 'impressed', 'quality',
            'efficient', 'smooth', 'quiet', 'reliable', 'durable', 'value', 'worth',
            'smart', 'innovative', 'advanced', 'modern', 'sleek', 'stylish'
        }
        
        self.negative_words = {
            'terrible', 'awful', 'bad', 'horrible', 'disappointing', 'worst', 'hate',
            'dislike', 'poor', 'cheap', 'broken', 'defective', 'useless', 'waste',
            'problem', 'issue', 'trouble', 'difficult', 'hard', 'complicated', 'noisy',
            'loud', 'slow', 'unreliable', 'fragile', 'expensive', 'overpriced'
        }
        
        self.negation_words = {
            'not', 'no', 'never', 'none', 'nobody', 'nothing', 'neither', 'nowhere',
            'hardly', 'scarcely', 'barely', 'don\'t', 'doesn\'t', 'didn\'t', 'won\'t',
            'wouldn\'t', 'shouldn\'t', 'couldn\'t', 'can\'t', 'cannot'
        }
    
    def analyze_batch(self, processed_data: Dict) -> Dict[str, Dict]:
        """
        Analyze sentiment for all posts in processed data
        
        Args:
            processed_data: Dictionary of processed search results
            
        Returns:
            Dictionary mapping post IDs to sentiment analysis results
        """
        logger.info("Starting batch sentiment analysis...")
        
        sentiment_results = {}
        total_posts = 0
        
        for keyword_data in processed_data.values():
            for platform_data in keyword_data.values():
                for post in platform_data:
                    post_id = post.get('id', f'unknown_{total_posts}')
                    text_content = post.get('text_content', '')
                    
                    sentiment_result = self.analyze_text(text_content)
                    sentiment_results[post_id] = sentiment_result
                    total_posts += 1
        
        logger.info(f"Completed sentiment analysis for {total_posts} posts")
        return sentiment_results
    
    def analyze_text(self, text: str) -> Dict[str, Union[str, float]]:
        """
        Analyze sentiment of a single text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing sentiment classification and scores
        """
        if not text or not text.strip():
            return self._empty_sentiment_result()
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Try different analyzers in order of preference
        if self.vader_analyzer:
            return self._analyze_with_vader(cleaned_text)
        elif self.textblob_available:
            return self._analyze_with_textblob(cleaned_text)
        else:
            return self._analyze_with_lexicon(cleaned_text)
    
    def _analyze_with_vader(self, text: str) -> Dict[str, Union[str, float]]:
        """Analyze sentiment using VADER"""
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            
            # Determine sentiment label
            compound = scores['compound']
            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'confidence': abs(compound),
                'positive_score': scores['pos'],
                'negative_score': scores['neg'],
                'neutral_score': scores['neu'],
                'compound_score': compound,
                'analyzer': 'vader'
            }
        except Exception as e:
            logger.error(f"Error in VADER analysis: {e}")
            return self._analyze_with_lexicon(text)
    
    def _analyze_with_textblob(self, text: str) -> Dict[str, Union[str, float]]:
        """Analyze sentiment using TextBlob"""
        try:
            from textblob import TextBlob
            
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Determine sentiment label
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'confidence': abs(polarity),
                'polarity': polarity,
                'subjectivity': subjectivity,
                'positive_score': max(polarity, 0),
                'negative_score': abs(min(polarity, 0)),
                'neutral_score': 1 - abs(polarity),
                'analyzer': 'textblob'
            }
        except Exception as e:
            logger.error(f"Error in TextBlob analysis: {e}")
            return self._analyze_with_lexicon(text)
    
    def _analyze_with_lexicon(self, text: str) -> Dict[str, Union[str, float]]:
        """Analyze sentiment using simple lexicon-based approach"""
        words = text.lower().split()
        
        positive_score = 0
        negative_score = 0
        negation_context = False
        
        for i, word in enumerate(words):
            # Check for negation
            if word in self.negation_words:
                negation_context = True
                continue
            
            # Reset negation context after 3 words
            if i > 0 and words[i-1] not in self.negation_words and i > 2:
                negation_context = False
            
            # Score words
            if word in self.positive_words:
                if negation_context:
                    negative_score += 1
                else:
                    positive_score += 1
            elif word in self.negative_words:
                if negation_context:
                    positive_score += 1
                else:
                    negative_score += 1
        
        # Calculate final sentiment
        total_sentiment_words = positive_score + negative_score
        
        if total_sentiment_words == 0:
            sentiment = 'neutral'
            confidence = 0.0
        elif positive_score > negative_score:
            sentiment = 'positive'
            confidence = positive_score / total_sentiment_words
        elif negative_score > positive_score:
            sentiment = 'negative'
            confidence = negative_score / total_sentiment_words
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_score': positive_score / max(total_sentiment_words, 1),
            'negative_score': negative_score / max(total_sentiment_words, 1),
            'neutral_score': 1 - (total_sentiment_words / max(len(words), 1)),
            'analyzer': 'lexicon'
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text for sentiment analysis"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove mentions and hashtags (but keep the content)
        text = re.sub(r'[@#]\w+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\;]', '', text)
        
        return text
    
    def _empty_sentiment_result(self) -> Dict[str, Union[str, float]]:
        """Return empty sentiment result"""
        return {
            'sentiment': 'neutral',
            'confidence': 0.0,
            'positive_score': 0.0,
            'negative_score': 0.0,
            'neutral_score': 1.0,
            'analyzer': 'none'
        }
    
    def get_sentiment_summary(self, sentiment_results: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Generate summary statistics from sentiment analysis results
        
        Args:
            sentiment_results: Dictionary of sentiment analysis results
            
        Returns:
            Summary statistics
        """
        if not sentiment_results:
            return {
                'total_analyzed': 0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'average_confidence': 0.0,
                'dominant_sentiment': 'neutral'
            }
        
        sentiments = [result['sentiment'] for result in sentiment_results.values()]
        confidences = [result['confidence'] for result in sentiment_results.values()]
        
        sentiment_counts = {
            'positive': sentiments.count('positive'),
            'negative': sentiments.count('negative'),
            'neutral': sentiments.count('neutral')
        }
        
        total = len(sentiments)
        sentiment_distribution = {
            sentiment: count / total 
            for sentiment, count in sentiment_counts.items()
        }
        
        average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]
        
        return {
            'total_analyzed': total,
            'sentiment_distribution': sentiment_distribution,
            'sentiment_counts': sentiment_counts,
            'average_confidence': average_confidence,
            'dominant_sentiment': dominant_sentiment
        }
