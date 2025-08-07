"""
Share of Voice Calculator - Computes various SoV metrics
"""

import logging
from typing import Dict, List, Any
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)

class SoVCalculator:
    """Calculator for Share of Voice metrics"""
    
    def __init__(self, config):
        self.config = config
        self.competitors = getattr(config, 'COMPETITORS', [
            'Havells', 'Orient', 'Bajaj', 'Crompton', 'Usha', 'Symphony', 'Voltas'
        ])
    
    def calculate_sov(self, processed_data: Dict, sentiment_data: Dict) -> Dict[str, Any]:
        """
        Calculate comprehensive Share of Voice metrics
        
        Args:
            processed_data: Processed search results by keyword and platform
            sentiment_data: Sentiment analysis results
            
        Returns:
            Dictionary containing various SoV metrics
        """
        logger.info("Calculating Share of Voice metrics...")
        
        # Flatten all posts for analysis
        all_posts = []
        for keyword_data in processed_data.values():
            for platform_data in keyword_data.values():
                all_posts.extend(platform_data)
        
        if not all_posts:
            logger.warning("No posts found for SoV calculation")
            return self._empty_sov_metrics()
        
        # Calculate basic mention metrics
        mention_metrics = self._calculate_mention_share(all_posts)
        
        # Calculate engagement-weighted metrics
        engagement_metrics = self._calculate_engagement_share(all_posts)
        
        # Calculate sentiment-based metrics
        sentiment_metrics = self._calculate_sentiment_share(all_posts, sentiment_data)
        
        # Calculate platform-specific metrics
        platform_metrics = self._calculate_platform_breakdown(processed_data)
        
        # Calculate visibility score
        visibility_score = self._calculate_visibility_score(all_posts)
        
        # Calculate competitive positioning
        competitive_metrics = self._calculate_competitive_positioning(all_posts)
        
        # Overall SoV (weighted average of different metrics)
        overall_sov = self._calculate_overall_sov(
            mention_metrics, engagement_metrics, sentiment_metrics
        )
        
        sov_metrics = {
            'overall_sov': overall_sov,
            'mention_share': mention_metrics,
            'engagement_share': engagement_metrics,
            'sentiment_share': sentiment_metrics,
            'platform_breakdown': platform_metrics,
            'visibility_score': visibility_score,
            'competitive_positioning': competitive_metrics,
            'total_posts_analyzed': len(all_posts),
            'atomberg_mentions': sum(1 for post in all_posts if post.get('mentions_atomberg', False)),
            'competitor_mentions': sum(len(post.get('mentions_competitors', [])) for post in all_posts)
        }
        
        logger.info(f"SoV calculation complete. Overall SoV: {overall_sov:.2%}")
        return sov_metrics
    
    def _calculate_mention_share(self, posts: List[Dict]) -> Dict[str, float]:
        """Calculate share based on pure mention counts"""
        atomberg_mentions = sum(1 for post in posts if post.get('mentions_atomberg', False))
        
        competitor_counts = defaultdict(int)
        for post in posts:
            for competitor in post.get('mentions_competitors', []):
                competitor_counts[competitor] += 1
        
        total_brand_mentions = atomberg_mentions + sum(competitor_counts.values())
        
        if total_brand_mentions == 0:
            return {'atomberg': 0.0, 'competitors': {}, 'total_mentions': 0}
        
        atomberg_share = atomberg_mentions / total_brand_mentions
        competitor_shares = {
            comp: count / total_brand_mentions 
            for comp, count in competitor_counts.items()
        }
        
        return {
            'atomberg': atomberg_share,
            'competitors': competitor_shares,
            'total_mentions': total_brand_mentions,
            'atomberg_mentions': atomberg_mentions
        }
    
    def _calculate_engagement_share(self, posts: List[Dict]) -> Dict[str, float]:
        """Calculate share weighted by engagement metrics"""
        atomberg_engagement = 0
        competitor_engagement = defaultdict(float)
        
        for post in posts:
            # Calculate total engagement for this post
            engagement = self._get_post_engagement(post)
            
            if post.get('mentions_atomberg', False):
                atomberg_engagement += engagement
            
            for competitor in post.get('mentions_competitors', []):
                competitor_engagement[competitor] += engagement
        
        total_engagement = atomberg_engagement + sum(competitor_engagement.values())
        
        if total_engagement == 0:
            return {'atomberg': 0.0, 'competitors': {}, 'total_engagement': 0}
        
        atomberg_share = atomberg_engagement / total_engagement
        competitor_shares = {
            comp: eng / total_engagement 
            for comp, eng in competitor_engagement.items()
        }
        
        return {
            'atomberg': atomberg_share,
            'competitors': competitor_shares,
            'total_engagement': total_engagement,
            'atomberg_engagement': atomberg_engagement
        }
    
    def _calculate_sentiment_share(self, posts: List[Dict], sentiment_data: Dict) -> Dict[str, Any]:
        """Calculate sentiment-based share metrics"""
        atomberg_sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        competitor_sentiments = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0})
        
        for post in posts:
            post_id = post.get('id', '')
            sentiment = sentiment_data.get(post_id, {}).get('sentiment', 'neutral')
            
            if post.get('mentions_atomberg', False):
                atomberg_sentiments[sentiment] += 1
            
            for competitor in post.get('mentions_competitors', []):
                competitor_sentiments[competitor][sentiment] += 1
        
        # Calculate positive sentiment share
        total_positive = atomberg_sentiments['positive'] + sum(
            comp_sent['positive'] for comp_sent in competitor_sentiments.values()
        )
        
        if total_positive == 0:
            positive_share = 0.0
        else:
            positive_share = atomberg_sentiments['positive'] / total_positive
        
        # Calculate sentiment distribution for Atomberg
        total_atomberg = sum(atomberg_sentiments.values())
        atomberg_sentiment_dist = {}
        if total_atomberg > 0:
            atomberg_sentiment_dist = {
                sentiment: count / total_atomberg 
                for sentiment, count in atomberg_sentiments.items()
            }
        
        return {
            'positive': positive_share,
            'atomberg_sentiment_distribution': atomberg_sentiment_dist,
            'competitor_sentiment_distribution': dict(competitor_sentiments),
            'total_positive_mentions': total_positive,
            'atomberg_positive_mentions': atomberg_sentiments['positive']
        }
    
    def _calculate_platform_breakdown(self, processed_data: Dict) -> Dict[str, float]:
        """Calculate SoV breakdown by platform"""
        platform_sov = {}
        
        for keyword, keyword_data in processed_data.items():
            for platform, posts in keyword_data.items():
                if not posts:
                    platform_sov[platform] = 0.0
                    continue
                
                atomberg_mentions = sum(1 for post in posts if post.get('mentions_atomberg', False))
                total_brand_mentions = atomberg_mentions + sum(
                    len(post.get('mentions_competitors', [])) for post in posts
                )
                
                if total_brand_mentions > 0:
                    platform_sov[platform] = atomberg_mentions / total_brand_mentions
                else:
                    platform_sov[platform] = 0.0
        
        return platform_sov
    
    def _calculate_visibility_score(self, posts: List[Dict]) -> float:
        """Calculate a composite visibility score"""
        if not posts:
            return 0.0
        
        atomberg_visibility = 0
        total_visibility = 0
        
        for post in posts:
            # Calculate visibility based on platform, position, engagement
            post_visibility = self._get_post_visibility(post)
            total_visibility += post_visibility
            
            if post.get('mentions_atomberg', False):
                atomberg_visibility += post_visibility
        
        if total_visibility == 0:
            return 0.0
        
        return atomberg_visibility / total_visibility
    
    def _calculate_competitive_positioning(self, posts: List[Dict]) -> Dict[str, Any]:
        """Analyze competitive positioning"""
        # Direct comparisons (posts mentioning multiple brands)
        direct_comparisons = []
        for post in posts:
            mentions_atomberg = post.get('mentions_atomberg', False)
            competitor_mentions = post.get('mentions_competitors', [])
            
            if mentions_atomberg and competitor_mentions:
                direct_comparisons.append({
                    'post_id': post.get('id'),
                    'competitors': competitor_mentions,
                    'engagement': self._get_post_engagement(post)
                })
        
        # Market positioning score
        positioning_scores = {}
        for competitor in self.competitors:
            competitor_posts = [
                post for post in posts 
                if competitor in post.get('mentions_competitors', [])
            ]
            if competitor_posts:
                avg_engagement = statistics.mean(
                    self._get_post_engagement(post) for post in competitor_posts
                )
                positioning_scores[competitor] = avg_engagement
        
        # Atomberg positioning
        atomberg_posts = [post for post in posts if post.get('mentions_atomberg', False)]
        atomberg_avg_engagement = 0
        if atomberg_posts:
            atomberg_avg_engagement = statistics.mean(
                self._get_post_engagement(post) for post in atomberg_posts
            )
        
        return {
            'direct_comparisons': len(direct_comparisons),
            'atomberg_avg_engagement': atomberg_avg_engagement,
            'competitor_avg_engagement': positioning_scores,
            'market_position_rank': self._calculate_market_rank(
                atomberg_avg_engagement, positioning_scores
            )
        }
    
    def _calculate_overall_sov(self, mention_metrics: Dict, engagement_metrics: Dict, 
                             sentiment_metrics: Dict) -> float:
        """Calculate weighted overall SoV"""
        # Weights for different metrics
        mention_weight = 0.4
        engagement_weight = 0.4
        sentiment_weight = 0.2
        
        mention_sov = mention_metrics.get('atomberg', 0)
        engagement_sov = engagement_metrics.get('atomberg', 0)
        sentiment_sov = sentiment_metrics.get('positive', 0)
        
        overall_sov = (
            mention_sov * mention_weight +
            engagement_sov * engagement_weight +
            sentiment_sov * sentiment_weight
        )
        
        return overall_sov
    
    def _get_post_engagement(self, post: Dict) -> float:
        """Calculate engagement score for a post"""
        platform = post.get('platform', '')
        
        if platform == 'youtube':
            views = post.get('views', 0)
            likes = post.get('likes', 0)
            comments = post.get('comments', 0)
            return views * 0.1 + likes * 1.0 + comments * 2.0
        
        elif platform == 'twitter':
            retweets = post.get('retweets', 0)
            likes = post.get('likes', 0)
            replies = post.get('replies', 0)
            quotes = post.get('quotes', 0)
            return retweets * 3.0 + likes * 1.0 + replies * 2.0 + quotes * 2.5
        
        elif platform == 'google':
            position = post.get('position', 10)
            # Higher positions (lower numbers) get more weight
            return max(11 - position, 1) * 10
        
        return 1.0  # Default engagement score
    
    def _get_post_visibility(self, post: Dict) -> float:
        """Calculate visibility score for a post"""
        platform = post.get('platform', '')
        engagement = self._get_post_engagement(post)
        
        # Platform-specific visibility multipliers
        if platform == 'youtube':
            views = post.get('views', 0)
            return views * 0.01 + engagement * 0.1
        
        elif platform == 'twitter':
            followers = post.get('author_followers', 0)
            return followers * 0.001 + engagement * 0.1
        
        elif platform == 'google':
            position = post.get('position', 10)
            page = post.get('page', 1)
            # Top positions get exponentially higher visibility
            return (11 - position) ** 2 * (1 / page)
        
        return engagement
    
    def _calculate_market_rank(self, atomberg_engagement: float, 
                             competitor_engagements: Dict[str, float]) -> int:
        """Calculate Atomberg's market position rank"""
        all_engagements = list(competitor_engagements.values()) + [atomberg_engagement]
        all_engagements.sort(reverse=True)
        
        try:
            return all_engagements.index(atomberg_engagement) + 1
        except ValueError:
            return len(all_engagements)
    
    def _empty_sov_metrics(self) -> Dict[str, Any]:
        """Return empty SoV metrics structure"""
        return {
            'overall_sov': 0.0,
            'mention_share': {'atomberg': 0.0, 'competitors': {}, 'total_mentions': 0},
            'engagement_share': {'atomberg': 0.0, 'competitors': {}, 'total_engagement': 0},
            'sentiment_share': {'positive': 0.0, 'atomberg_sentiment_distribution': {}},
            'platform_breakdown': {},
            'visibility_score': 0.0,
            'competitive_positioning': {},
            'total_posts_analyzed': 0,
            'atomberg_mentions': 0,
            'competitor_mentions': 0
        }
