#!/usr/bin/env python3
"""
Demo script for Atomberg Share of Voice Analysis
Runs a simplified version of the analysis with mock data
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import Config
from agents.search_agent import SearchAgent
from analysis.sov_calculator import SoVCalculator
from analysis.sentiment_analyzer import SentimentAnalyzer
from utils.data_processor import DataProcessor
from utils.visualizer import Visualizer

def run_demo():
    """Run a demonstration of the SoV analysis"""
    print("🚀 Starting Atomberg Share of Voice Analysis Demo")
    print("=" * 60)
    
    # Initialize configuration
    config = Config()
    print(f"✅ Configuration loaded")
    print(f"   - Competitors tracked: {len(config.COMPETITORS)}")
    print(f"   - Default keywords: {len(config.DEFAULT_KEYWORDS)}")
    
    # Initialize components
    search_agent = SearchAgent(config)
    sov_calculator = SoVCalculator(config)
    sentiment_analyzer = SentimentAnalyzer()
    data_processor = DataProcessor()
    visualizer = Visualizer()
    
    print(f"✅ All components initialized")
    
    # Demo parameters
    keywords = ["smart fan"]
    platforms = ["youtube", "twitter", "google"]
    max_results = 20  # Smaller number for demo
    
    print(f"\n🔍 Demo Analysis Parameters:")
    print(f"   - Keywords: {keywords}")
    print(f"   - Platforms: {platforms}")
    print(f"   - Max results per platform: {max_results}")
    
    # Step 1: Collect data (using mock data for demo)
    print(f"\n📊 Step 1: Collecting data from platforms...")
    all_results = {}
    
    for keyword in keywords:
        keyword_results = {}
        for platform in platforms:
            print(f"   - Searching {platform} for '{keyword}'...")
            try:
                platform_data = search_agent.search_platform(platform, keyword, max_results)
                keyword_results[platform] = platform_data
                print(f"     ✅ Found {len(platform_data)} results")
            except Exception as e:
                print(f"     ❌ Error: {str(e)}")
                keyword_results[platform] = []
        
        all_results[keyword] = keyword_results
    
    # Step 2: Process data
    print(f"\n🧹 Step 2: Processing and cleaning data...")
    processed_data = data_processor.process_search_results(all_results)
    
    total_posts = sum(len(posts) for keyword_data in processed_data.values() 
                     for posts in keyword_data.values())
    print(f"   ✅ Processed {total_posts} posts total")
    
    # Step 3: Sentiment analysis
    print(f"\n😊 Step 3: Performing sentiment analysis...")
    sentiment_results = sentiment_analyzer.analyze_batch(processed_data)
    print(f"   ✅ Analyzed sentiment for {len(sentiment_results)} posts")
    
    # Step 4: Calculate SoV metrics
    print(f"\n📈 Step 4: Calculating Share of Voice metrics...")
    sov_metrics = sov_calculator.calculate_sov(processed_data, sentiment_results)
    
    overall_sov = sov_metrics.get('overall_sov', 0)
    print(f"   ✅ Overall Atomberg SoV: {overall_sov:.2%}")
    
    # Step 5: Generate insights
    print(f"\n💡 Step 5: Generating insights and recommendations...")
    
    insights = generate_demo_insights(sov_metrics, processed_data)
    print(f"   ✅ Generated {len(insights.get('key_findings', []))} key findings")
    
    # Step 6: Create visualizations
    print(f"\n📊 Step 6: Creating visualizations...")
    try:
        charts = visualizer.create_sov_dashboard(sov_metrics, processed_data)
        print(f"   ✅ Created {len(charts)} charts")
        for chart_name, chart_path in charts.items():
            print(f"     - {chart_name}: {chart_path}")
    except Exception as e:
        print(f"   ⚠️  Visualization error: {e}")
        charts = {}
    
    # Step 7: Save results
    print(f"\n💾 Step 7: Saving results...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save main results
    results = {
        'metadata': {
            'keywords': keywords,
            'platforms': platforms,
            'total_posts_analyzed': total_posts,
            'analysis_timestamp': timestamp
        },
        'sov_metrics': sov_metrics,
        'insights': insights,
        'charts': charts
    }
    
    results_file = f'data/demo_results_{timestamp}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"   ✅ Results saved to {results_file}")
    
    # Create summary report
    try:
        report_path = visualizer.create_summary_report(sov_metrics, insights)
        print(f"   ✅ Summary report: {report_path}")
    except Exception as e:
        print(f"   ⚠️  Report generation error: {e}")
    
    # Display summary
    print(f"\n" + "=" * 60)
    print(f"🎯 ATOMBERG SHARE OF VOICE ANALYSIS COMPLETE")
    print(f"=" * 60)
    print(f"📊 Analysis Summary:")
    print(f"   • Total posts analyzed: {total_posts}")
    print(f"   • Atomberg mentions: {sov_metrics.get('atomberg_mentions', 0)}")
    print(f"   • Competitor mentions: {sov_metrics.get('competitor_mentions', 0)}")
    print(f"   • Overall SoV: {overall_sov:.2%}")
    
    # Platform breakdown
    platform_breakdown = sov_metrics.get('platform_breakdown', {})
    if platform_breakdown:
        print(f"\n📱 Platform Performance:")
        for platform, sov in platform_breakdown.items():
            print(f"   • {platform.title()}: {sov:.2%}")
    
    # Key findings
    key_findings = insights.get('key_findings', [])
    if key_findings:
        print(f"\n🔍 Key Findings:")
        for i, finding in enumerate(key_findings[:3], 1):
            print(f"   {i}. {finding}")
    
    # Recommendations
    recommendations = insights.get('marketing_recommendations', [])
    if recommendations:
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec}")
    
    print(f"\n📂 Output Files:")
    print(f"   • Analysis data: {results_file}")
    if 'report_path' in locals():
        print(f"   • Summary report: {report_path}")
    print(f"   • Detailed report: ATOMBERG_SOV_REPORT.md")
    
    print(f"\n✨ Demo completed successfully!")
    return results

def generate_demo_insights(sov_metrics: dict, processed_data: dict) -> dict:
    """Generate insights for the demo"""
    insights = {
        'key_findings': [],
        'competitive_positioning': {},
        'content_recommendations': [],
        'marketing_recommendations': []
    }
    
    overall_sov = sov_metrics.get('overall_sov', 0)
    
    # Generate findings based on SoV performance
    if overall_sov < 0.15:
        insights['key_findings'].append("Low market visibility: Atomberg needs increased content marketing")
        insights['marketing_recommendations'].extend([
            "Launch comprehensive YouTube content strategy",
            "Increase social media engagement and posting frequency",
            "Develop SEO-optimized blog content around smart fan topics"
        ])
    elif overall_sov > 0.25:
        insights['key_findings'].append("Strong market presence: Atomberg has significant share of voice")
        insights['marketing_recommendations'].append("Maintain momentum and explore new keyword opportunities")
    else:
        insights['key_findings'].append("Moderate market presence: Room for strategic growth")
    
    # Platform-specific insights
    platform_breakdown = sov_metrics.get('platform_breakdown', {})
    best_platform = max(platform_breakdown.items(), key=lambda x: x[1]) if platform_breakdown else None
    
    if best_platform:
        platform_name, platform_sov = best_platform
        insights['key_findings'].append(f"Best performing platform: {platform_name} ({platform_sov:.1%} SoV)")
        insights['marketing_recommendations'].append(f"Double down on {platform_name} content strategy")
    
    # Sentiment insights
    sentiment_share = sov_metrics.get('sentiment_share', {})
    positive_sentiment = sentiment_share.get('positive', 0)
    
    if positive_sentiment > 0.6:
        insights['key_findings'].append("Strong positive sentiment: Brand perception is favorable")
    elif positive_sentiment < 0.4:
        insights['key_findings'].append("Sentiment challenges: Address customer concerns")
        insights['content_recommendations'].append("Create content addressing common pain points")
    
    insights['content_recommendations'].extend([
        "Develop installation tutorial videos",
        "Create energy savings comparison content",
        "Showcase smart home integration use cases"
    ])
    
    return insights

if __name__ == "__main__":
    try:
        results = run_demo()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
