#!/usr/bin/env python3
"""
Standalone Demo for Atomberg Share of Voice Analysis
This version works without external dependencies for demonstration
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict
import random

class MockDataGenerator:
    """Generates realistic mock data for demonstration"""
    
    def __init__(self):
        self.competitors = ['Havells', 'Orient', 'Bajaj', 'Crompton', 'Usha']
        
        self.youtube_titles = [
            "Best Smart Ceiling Fans 2024 - Atomberg vs Havells Comparison",
            "Smart Fan Review: Energy Efficient BLDC Motors Explained",
            "Installing IoT Ceiling Fan with App Control - Step by Step",
            "Atomberg Smart Fan Unboxing and First Impressions",
            "Smart Home Setup: Integrating Ceiling Fans with Alexa",
            "Energy Bill Reduced by 65% - Smart Fan vs Regular Fan Test",
            "Top 5 Smart Ceiling Fans Under ₹15000 in India",
            "Havells vs Orient vs Bajaj Smart Fan Speed Test",
            "Why I Switched to Atomberg BLDC Fan - 6 Month Review",
            "Smart Fan App Features Comparison - Which is Best?"
        ]
        
        self.twitter_texts = [
            "Just installed @atomberg smart fan and the energy savings are incredible! #SmartHome #EnergyEfficient",
            "Comparing smart ceiling fans - @havells vs @orient vs @atomberg. Which should I buy? #Help",
            "My Atomberg fan has been running silently for 2 years. Best investment ever! #SmartFan",
            "Smart home setup complete! Atomberg fan integrated with Alexa perfectly 🏠✨ #IoT",
            "Looking for recommendations: Best BLDC ceiling fan under ₹10k? Considering Atomberg and Havells",
            "Atomberg customer service is outstanding! Fan issue resolved in 24 hours 👍 #CustomerService",
            "Energy bill down 40% after switching to smart fans throughout the house #EnergyEfficient #SmartHome",
            "Installation was trickier than expected but the Atomberg app makes control so easy #SmartFan",
            "Comparing Orient and Atomberg smart fans - both have great features but Atomberg wins on efficiency",
            "Smart fan deals this festive season? Looking at Atomberg and Bajaj models #Shopping"
        ]
        
        self.google_results = [
            ("Best Smart Ceiling Fans in India 2024 - Complete Buying Guide", 
             "Compare top smart ceiling fans from Atomberg, Havells, Orient. Energy efficient BLDC motors with app control."),
            ("Atomberg Smart Fan Review: IoT Ceiling Fan with Remote Control",
             "Detailed review of Atomberg smart ceiling fan features, installation, energy efficiency, and smart home integration."),
            ("Smart Ceiling Fans - Buy Online at Best Prices | Amazon.in",
             "Shop smart ceiling fans from top brands. Atomberg, Havells, Orient, Bajaj with free delivery and installation."),
            ("Havells vs Atomberg Smart Fan Comparison 2024",
             "Which smart ceiling fan is better? Compare features, price, energy efficiency between Havells and Atomberg."),
            ("Top 10 Energy Efficient Ceiling Fans | BLDC Motor Technology",
             "Energy efficient ceiling fans with BLDC motors. Atomberg leads in energy savings with 28W power consumption."),
            ("Smart Home Ceiling Fan Integration Guide | IoT Setup",
             "How to integrate smart ceiling fans with Alexa, Google Home. Atomberg and Orient compatibility guide."),
            ("Ceiling Fan Installation Services Near Me | Smart Fan Setup",
             "Professional installation for smart ceiling fans. Atomberg certified installers available across India."),
            ("Smart Fan App Review: Atomberg vs Havells vs Orient",
             "Compare smart fan mobile apps. Atomberg app rated highest for user experience and features."),
            ("Energy Savings Calculator: Smart Fan vs Regular Fan",
             "Calculate energy savings with smart BLDC fans. Atomberg users save average ₹2400 annually on electricity."),
            ("Smart Ceiling Fan Troubleshooting Guide | Common Issues",
             "Fix common smart fan problems. Atomberg, Havells, Orient troubleshooting tips and customer support contacts.")
        ]
    
    def generate_youtube_data(self, query: str, max_results: int) -> List[Dict]:
        """Generate mock YouTube data"""
        results = []
        for i in range(min(max_results, len(self.youtube_titles))):
            title = self.youtube_titles[i]
            
            # Determine brand mentions
            mentions_atomberg = 'atomberg' in title.lower()
            competitor_mentions = [comp for comp in self.competitors if comp.lower() in title.lower()]
            
            result = {
                'platform': 'youtube',
                'id': f'yt_mock_{i}',
                'title': title,
                'description': f'Detailed analysis and review of {title.split()[0]} with technical specifications and user experience.',
                'channel': f'TechReviewer{i+1}',
                'published_at': '2024-01-01T00:00:00Z',
                'url': f'https://youtube.com/watch?v=mock_{i}',
                'views': random.randint(5000, 50000),
                'likes': random.randint(100, 1000),
                'comments': random.randint(20, 200),
                'mentions_atomberg': mentions_atomberg,
                'mentions_competitors': competitor_mentions,
                'text_content': title
            }
            results.append(result)
        
        return results
    
    def generate_twitter_data(self, query: str, max_results: int) -> List[Dict]:
        """Generate mock Twitter data"""
        results = []
        for i in range(min(max_results, len(self.twitter_texts))):
            text = self.twitter_texts[i]
            
            # Determine brand mentions
            mentions_atomberg = 'atomberg' in text.lower() or '@atomberg' in text.lower()
            competitor_mentions = []
            for comp in self.competitors:
                if comp.lower() in text.lower() or f'@{comp.lower()}' in text.lower():
                    competitor_mentions.append(comp)
            
            result = {
                'platform': 'twitter',
                'id': f'tw_mock_{i}',
                'text': text,
                'author': f'user_{i+1}',
                'author_followers': random.randint(500, 5000),
                'retweets': random.randint(1, 50),
                'likes': random.randint(5, 200),
                'replies': random.randint(0, 30),
                'mentions_atomberg': mentions_atomberg,
                'mentions_competitors': competitor_mentions,
                'text_content': text
            }
            results.append(result)
        
        return results
    
    def generate_google_data(self, query: str, max_results: int) -> List[Dict]:
        """Generate mock Google search data"""
        results = []
        for i, (title, description) in enumerate(self.google_results[:max_results]):
            
            # Determine brand mentions
            full_text = f"{title} {description}"
            mentions_atomberg = 'atomberg' in full_text.lower()
            competitor_mentions = [comp for comp in self.competitors if comp.lower() in full_text.lower()]
            
            result = {
                'platform': 'google',
                'id': f'google_mock_{i}',
                'title': title,
                'description': description,
                'url': f'https://example{i}.com/smart-fans',
                'position': i + 1,
                'page': (i // 10) + 1,
                'mentions_atomberg': mentions_atomberg,
                'mentions_competitors': competitor_mentions,
                'text_content': full_text,
                'domain': f'example{i}.com'
            }
            results.append(result)
        
        return results

class SimpleSentimentAnalyzer:
    """Simple sentiment analyzer using word lists"""
    
    def __init__(self):
        self.positive_words = {
            'amazing', 'excellent', 'great', 'fantastic', 'wonderful', 'awesome',
            'best', 'love', 'perfect', 'outstanding', 'brilliant', 'good',
            'efficient', 'quiet', 'smooth', 'reliable', 'durable', 'recommend'
        }
        
        self.negative_words = {
            'terrible', 'awful', 'bad', 'horrible', 'worst', 'hate',
            'broken', 'problem', 'issue', 'disappointing', 'noisy', 'expensive'
        }
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        if not text:
            return {'sentiment': 'neutral', 'confidence': 0.0}
        
        words = text.lower().split()
        positive_score = sum(1 for word in words if word in self.positive_words)
        negative_score = sum(1 for word in words if word in self.negative_words)
        
        if positive_score > negative_score:
            sentiment = 'positive'
            confidence = positive_score / len(words)
        elif negative_score > positive_score:
            sentiment = 'negative'
            confidence = negative_score / len(words)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': min(confidence, 1.0),
            'positive_score': positive_score,
            'negative_score': negative_score
        }

class SimpleSoVCalculator:
    """Simple Share of Voice calculator"""
    
    def calculate_sov(self, processed_data: Dict, sentiment_data: Dict) -> Dict:
        """Calculate SoV metrics"""
        # Flatten all posts
        all_posts = []
        for keyword_data in processed_data.values():
            for platform_data in keyword_data.values():
                all_posts.extend(platform_data)
        
        if not all_posts:
            return self._empty_metrics()
        
        # Calculate mention share
        atomberg_mentions = sum(1 for post in all_posts if post.get('mentions_atomberg', False))
        competitor_mentions = sum(len(post.get('mentions_competitors', [])) for post in all_posts)
        total_brand_mentions = atomberg_mentions + competitor_mentions
        
        mention_share = atomberg_mentions / max(total_brand_mentions, 1)
        
        # Calculate sentiment metrics
        atomberg_posts = [post for post in all_posts if post.get('mentions_atomberg', False)]
        positive_atomberg = 0
        total_atomberg_sentiment = 0
        
        for post in atomberg_posts:
            post_sentiment = sentiment_data.get(post['id'], {})
            if post_sentiment.get('sentiment') == 'positive':
                positive_atomberg += 1
            total_atomberg_sentiment += 1
        
        sentiment_ratio = positive_atomberg / max(total_atomberg_sentiment, 1)
        
        # Platform breakdown
        platform_breakdown = {}
        for keyword_data in processed_data.values():
            for platform, posts in keyword_data.items():
                if posts:
                    platform_atomberg = sum(1 for post in posts if post.get('mentions_atomberg', False))
                    platform_total = sum(len(post.get('mentions_competitors', [])) for post in posts) + platform_atomberg
                    platform_breakdown[platform] = platform_atomberg / max(platform_total, 1)
        
        # Overall SoV (weighted average)
        overall_sov = (mention_share * 0.6) + (sentiment_ratio * 0.4)
        
        return {
            'overall_sov': overall_sov,
            'mention_share': {
                'atomberg': mention_share,
                'total_mentions': total_brand_mentions,
                'atomberg_mentions': atomberg_mentions
            },
            'sentiment_share': {
                'positive': sentiment_ratio,
                'atomberg_positive_mentions': positive_atomberg,
                'atomberg_sentiment_distribution': {
                    'positive': sentiment_ratio,
                    'negative': 1 - sentiment_ratio if sentiment_ratio < 1 else 0,
                    'neutral': 0
                }
            },
            'platform_breakdown': platform_breakdown,
            'total_posts_analyzed': len(all_posts),
            'atomberg_mentions': atomberg_mentions,
            'competitor_mentions': competitor_mentions
        }
    
    def _empty_metrics(self):
        return {
            'overall_sov': 0.0,
            'mention_share': {'atomberg': 0.0, 'total_mentions': 0},
            'sentiment_share': {'positive': 0.0},
            'platform_breakdown': {},
            'total_posts_analyzed': 0,
            'atomberg_mentions': 0,
            'competitor_mentions': 0
        }

def run_standalone_demo():
    """Run standalone demo without external dependencies"""
    print("🚀 Atomberg Share of Voice Analysis - Standalone Demo")
    print("=" * 60)
    
    # Initialize components
    data_generator = MockDataGenerator()
    sentiment_analyzer = SimpleSentimentAnalyzer()
    sov_calculator = SimpleSoVCalculator()
    
    # Demo parameters
    keywords = ["smart fan"]
    platforms = ["youtube", "twitter", "google"]
    max_results = 10
    
    print(f"📊 Demo Parameters:")
    print(f"   - Keywords: {keywords}")
    print(f"   - Platforms: {platforms}")
    print(f"   - Max results per platform: {max_results}")
    
    # Step 1: Generate mock data
    print(f"\n🔍 Step 1: Generating mock data...")
    all_results = {}
    
    for keyword in keywords:
        keyword_results = {}
        for platform in platforms:
            print(f"   - Generating {platform} data for '{keyword}'...")
            
            if platform == 'youtube':
                platform_data = data_generator.generate_youtube_data(keyword, max_results)
            elif platform == 'twitter':
                platform_data = data_generator.generate_twitter_data(keyword, max_results)
            elif platform == 'google':
                platform_data = data_generator.generate_google_data(keyword, max_results)
            else:
                platform_data = []
            
            keyword_results[platform] = platform_data
            print(f"     ✅ Generated {len(platform_data)} posts")
        
        all_results[keyword] = keyword_results
    
    # Step 2: Sentiment analysis
    print(f"\n😊 Step 2: Performing sentiment analysis...")
    sentiment_results = {}
    total_posts = 0
    
    for keyword_data in all_results.values():
        for platform_data in keyword_data.values():
            for post in platform_data:
                post_id = post['id']
                text_content = post.get('text_content', '')
                sentiment_result = sentiment_analyzer.analyze_text(text_content)
                sentiment_results[post_id] = sentiment_result
                total_posts += 1
    
    print(f"   ✅ Analyzed sentiment for {total_posts} posts")
    
    # Step 3: Calculate SoV
    print(f"\n📈 Step 3: Calculating Share of Voice metrics...")
    sov_metrics = sov_calculator.calculate_sov(all_results, sentiment_results)
    overall_sov = sov_metrics.get('overall_sov', 0)
    print(f"   ✅ Overall Atomberg SoV: {overall_sov:.2%}")
    
    # Step 4: Generate insights
    print(f"\n💡 Step 4: Generating insights...")
    insights = generate_insights(sov_metrics)
    print(f"   ✅ Generated insights and recommendations")
    
    # Step 5: Save results
    print(f"\n💾 Step 5: Saving results...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # Save detailed results
    results = {
        'metadata': {
            'analysis_type': 'standalone_demo',
            'keywords': keywords,
            'platforms': platforms,
            'timestamp': timestamp,
            'total_posts_analyzed': total_posts
        },
        'sov_metrics': sov_metrics,
        'insights': insights,
        'sample_data': {
            platform: data[:3] for platform, data in all_results['smart fan'].items()
        }
    }
    
    results_file = f'data/standalone_demo_{timestamp}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Create text report
    report_file = f'reports/demo_report_{timestamp}.txt'
    with open(report_file, 'w') as f:
        f.write("ATOMBERG SHARE OF VOICE ANALYSIS - DEMO REPORT\n")
        f.write("=" * 55 + "\n\n")
        
        f.write("EXECUTIVE SUMMARY\n")
        f.write("-" * 20 + "\n")
        f.write(f"Overall Share of Voice: {overall_sov:.2%}\n")
        f.write(f"Total Posts Analyzed: {total_posts}\n")
        f.write(f"Atomberg Mentions: {sov_metrics.get('atomberg_mentions', 0)}\n")
        f.write(f"Competitor Mentions: {sov_metrics.get('competitor_mentions', 0)}\n\n")
        
        f.write("PLATFORM BREAKDOWN\n")
        f.write("-" * 20 + "\n")
        platform_breakdown = sov_metrics.get('platform_breakdown', {})
        for platform, sov in platform_breakdown.items():
            f.write(f"{platform.title()}: {sov:.2%}\n")
        f.write("\n")
        
        f.write("KEY INSIGHTS\n")
        f.write("-" * 15 + "\n")
        for i, insight in enumerate(insights.get('key_findings', []), 1):
            f.write(f"{i}. {insight}\n")
        f.write("\n")
        
        f.write("RECOMMENDATIONS\n")
        f.write("-" * 18 + "\n")
        for i, rec in enumerate(insights.get('recommendations', []), 1):
            f.write(f"{i}. {rec}\n")
    
    print(f"   ✅ Results saved to {results_file}")
    print(f"   ✅ Report saved to {report_file}")
    
    # Display summary
    print(f"\n" + "=" * 60)
    print(f"🎯 DEMO ANALYSIS COMPLETE")
    print(f"=" * 60)
    print(f"📊 Results Summary:")
    print(f"   • Overall SoV: {overall_sov:.2%}")
    print(f"   • Posts analyzed: {total_posts}")
    print(f"   • Atomberg mentions: {sov_metrics.get('atomberg_mentions', 0)}")
    
    platform_breakdown = sov_metrics.get('platform_breakdown', {})
    if platform_breakdown:
        print(f"\n📱 Platform Performance:")
        for platform, sov in platform_breakdown.items():
            print(f"   • {platform.title()}: {sov:.2%}")
    
    print(f"\n🔍 Key Insights:")
    for i, insight in enumerate(insights.get('key_findings', [])[:3], 1):
        print(f"   {i}. {insight}")
    
    print(f"\n📂 Generated Files:")
    print(f"   • {results_file}")
    print(f"   • {report_file}")
    print(f"   • ATOMBERG_SOV_REPORT.md (comprehensive report)")
    
    print(f"\n✨ Demo completed successfully!")

def generate_insights(sov_metrics: Dict) -> Dict:
    """Generate insights from SoV metrics"""
    insights = {
        'key_findings': [],
        'recommendations': []
    }
    
    overall_sov = sov_metrics.get('overall_sov', 0)
    
    # SoV performance insights
    if overall_sov < 0.2:
        insights['key_findings'].append("Low Share of Voice: Atomberg needs increased digital presence")
        insights['recommendations'].extend([
            "Launch comprehensive content marketing strategy",
            "Increase social media engagement frequency",
            "Develop SEO-optimized content around smart fan keywords"
        ])
    elif overall_sov > 0.4:
        insights['key_findings'].append("Strong Share of Voice: Atomberg has commanding market presence")
        insights['recommendations'].append("Maintain current strategy and explore adjacent product categories")
    else:
        insights['key_findings'].append("Moderate Share of Voice: Solid foundation with growth opportunities")
        insights['recommendations'].append("Focus on high-performing platforms for amplified growth")
    
    # Platform insights
    platform_breakdown = sov_metrics.get('platform_breakdown', {})
    if platform_breakdown:
        best_platform = max(platform_breakdown.items(), key=lambda x: x[1])
        platform_name, platform_sov = best_platform
        insights['key_findings'].append(f"Top performing platform: {platform_name} ({platform_sov:.1%} SoV)")
        insights['recommendations'].append(f"Increase investment in {platform_name} content and advertising")
    
    # Sentiment insights
    sentiment_data = sov_metrics.get('sentiment_share', {})
    positive_ratio = sentiment_data.get('positive', 0)
    
    if positive_ratio > 0.7:
        insights['key_findings'].append("Excellent brand sentiment: Strong positive perception in market")
    elif positive_ratio < 0.4:
        insights['key_findings'].append("Sentiment concerns: Address customer pain points and feedback")
        insights['recommendations'].append("Develop customer support content and address common issues")
    
    insights['recommendations'].extend([
        "Create comparison content highlighting Atomberg's unique value propositions",
        "Develop user-generated content campaigns featuring customer success stories",
        "Optimize for smart home and IoT-related keyword clusters"
    ])
    
    return insights

if __name__ == "__main__":
    try:
        run_standalone_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
