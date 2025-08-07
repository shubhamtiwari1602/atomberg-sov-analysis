#!/usr/bin/env python3
"""
Atomberg Share of Voice Analysis Agent
Main application entry point
"""

import argparse
import logging
import os
from datetime import datetime
from typing import List, Dict

from agents.search_agent import SearchAgent
from analysis.sov_calculator import SoVCalculator
from analysis.sentiment_analyzer import SentimentAnalyzer
from utils.data_processor import DataProcessor
from utils.visualizer import Visualizer
from config.settings import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('atomberg_sov_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AtombergSoVAgent:
    """Main agent class for Atomberg Share of Voice analysis"""
    
    def __init__(self, config: Config):
        self.config = config
        self.search_agent = SearchAgent(config)
        self.sov_calculator = SoVCalculator(config)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.data_processor = DataProcessor()
        self.visualizer = Visualizer()
        
    def analyze_sov(self, keywords: List[str], platforms: List[str], num_results: int = 50) -> Dict:
        """
        Main analysis function that orchestrates the entire SoV analysis
        
        Args:
            keywords: List of search keywords (e.g., ['smart fan', 'ceiling fan'])
            platforms: List of platforms to search (e.g., ['youtube', 'twitter', 'google'])
            num_results: Number of top results to analyze per platform
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Starting SoV analysis for keywords: {keywords}")
        logger.info(f"Platforms: {platforms}, Results per platform: {num_results}")
        
        all_results = {}
        
        # Step 1: Search and collect data from all platforms
        for keyword in keywords:
            logger.info(f"Analyzing keyword: '{keyword}'")
            keyword_results = {}
            
            for platform in platforms:
                logger.info(f"Searching {platform} for '{keyword}'")
                try:
                    platform_data = self.search_agent.search_platform(
                        platform=platform,
                        query=keyword,
                        max_results=num_results
                    )
                    keyword_results[platform] = platform_data
                    logger.info(f"Collected {len(platform_data)} results from {platform}")
                except Exception as e:
                    logger.error(f"Error searching {platform}: {str(e)}")
                    keyword_results[platform] = []
            
            all_results[keyword] = keyword_results
        
        # Step 2: Process and clean the collected data
        logger.info("Processing collected data...")
        processed_data = self.data_processor.process_search_results(all_results)
        
        # Step 3: Perform sentiment analysis
        logger.info("Performing sentiment analysis...")
        sentiment_results = self.sentiment_analyzer.analyze_batch(processed_data)
        
        # Step 4: Calculate Share of Voice metrics
        logger.info("Calculating Share of Voice metrics...")
        sov_metrics = self.sov_calculator.calculate_sov(processed_data, sentiment_results)
        
        # Step 5: Generate insights and recommendations
        logger.info("Generating insights and recommendations...")
        insights = self._generate_insights(sov_metrics, processed_data)
        
        # Step 6: Create visualizations
        logger.info("Creating visualizations...")
        charts = self.visualizer.create_sov_dashboard(sov_metrics, processed_data)
        
        # Compile final results
        final_results = {
            'metadata': {
                'keywords': keywords,
                'platforms': platforms,
                'num_results': num_results,
                'analysis_date': datetime.now().isoformat(),
                'total_posts_analyzed': sum(len(data) for keyword_data in processed_data.values() 
                                          for data in keyword_data.values())
            },
            'raw_data': processed_data,
            'sentiment_analysis': sentiment_results,
            'sov_metrics': sov_metrics,
            'insights': insights,
            'visualizations': charts
        }
        
        # Step 7: Save results
        self._save_results(final_results)
        
        logger.info("Analysis completed successfully!")
        return final_results
    
    def _generate_insights(self, sov_metrics: Dict, processed_data: Dict) -> Dict:
        """Generate actionable insights from the analysis"""
        insights = {
            'key_findings': [],
            'competitive_positioning': {},
            'content_recommendations': [],
            'marketing_recommendations': []
        }
        
        # Analyze overall SoV performance
        overall_sov = sov_metrics.get('overall_sov', 0)
        if overall_sov < 0.1:  # Less than 10%
            insights['key_findings'].append(
                "Low Share of Voice: Atomberg has limited visibility in smart fan conversations"
            )
            insights['marketing_recommendations'].extend([
                "Increase content marketing efforts focused on smart fan features",
                "Engage with smart home and IoT communities",
                "Collaborate with tech influencers and reviewers"
            ])
        elif overall_sov > 0.3:  # More than 30%
            insights['key_findings'].append(
                "Strong Share of Voice: Atomberg has significant presence in smart fan discussions"
            )
            insights['marketing_recommendations'].append(
                "Maintain current content strategy and expand to related keywords"
            )
        
        # Sentiment analysis insights
        sentiment_score = sov_metrics.get('sentiment_share', {}).get('positive', 0)
        if sentiment_score > 0.7:
            insights['key_findings'].append(
                "Positive brand sentiment: Most Atomberg mentions are positive"
            )
        elif sentiment_score < 0.4:
            insights['key_findings'].append(
                "Negative sentiment concerns: Address customer pain points"
            )
            insights['content_recommendations'].extend([
                "Create content addressing common customer concerns",
                "Showcase customer success stories and testimonials"
            ])
        
        # Platform-specific insights
        platform_performance = sov_metrics.get('platform_breakdown', {})
        best_platform = max(platform_performance.items(), key=lambda x: x[1]) if platform_performance else None
        if best_platform:
            insights['key_findings'].append(
                f"Best performing platform: {best_platform[0]} ({best_platform[1]:.2%} SoV)"
            )
            insights['marketing_recommendations'].append(
                f"Invest more resources in {best_platform[0]} content and engagement"
            )
        
        return insights
    
    def _save_results(self, results: Dict):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        
        # Save raw data as JSON
        import json
        with open(f'data/sov_analysis_{timestamp}.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save metrics as CSV
        import pandas as pd
        metrics_df = pd.DataFrame([results['sov_metrics']])
        metrics_df.to_csv(f'data/sov_metrics_{timestamp}.csv', index=False)
        
        logger.info(f"Results saved to data/sov_analysis_{timestamp}.json")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Atomberg Share of Voice Analysis Agent')
    parser.add_argument('--keywords', type=str, default='smart fan', 
                       help='Comma-separated keywords to analyze')
    parser.add_argument('--platforms', type=str, default='youtube,twitter', 
                       help='Comma-separated platforms to search')
    parser.add_argument('--results', type=int, default=50, 
                       help='Number of results to analyze per platform')
    parser.add_argument('--config', type=str, default='config/settings.py',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Parse arguments
    keywords = [k.strip() for k in args.keywords.split(',')]
    platforms = [p.strip() for p in args.platforms.split(',')]
    
    # Load configuration
    config = Config()
    
    # Initialize and run agent
    agent = AtombergSoVAgent(config)
    
    try:
        results = agent.analyze_sov(
            keywords=keywords,
            platforms=platforms,
            num_results=args.results
        )
        
        print("\n" + "="*60)
        print("ATOMBERG SHARE OF VOICE ANALYSIS COMPLETE")
        print("="*60)
        print(f"Keywords analyzed: {', '.join(keywords)}")
        print(f"Platforms searched: {', '.join(platforms)}")
        print(f"Total posts analyzed: {results['metadata']['total_posts_analyzed']}")
        print(f"Overall SoV: {results['sov_metrics'].get('overall_sov', 0):.2%}")
        print("\nKey Findings:")
        for finding in results['insights']['key_findings']:
            print(f"• {finding}")
        print("\nDetailed results saved to data/ directory")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
