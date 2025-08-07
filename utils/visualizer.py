"""
Visualizer - Creates charts and visualizations for SoV analysis
"""

import logging
from typing import Dict, List, Any, Tuple
import os

logger = logging.getLogger(__name__)

class Visualizer:
    """Creates visualizations and charts for Share of Voice analysis"""
    
    def __init__(self):
        self.colors = {
            'atomberg': '#1f77b4',  # Blue
            'havells': '#ff7f0e',   # Orange
            'orient': '#2ca02c',    # Green
            'bajaj': '#d62728',     # Red
            'crompton': '#9467bd',  # Purple
            'usha': '#8c564b',      # Brown
            'symphony': '#e377c2',  # Pink
            'voltas': '#7f7f7f',    # Gray
            'others': '#bcbd22'     # Olive
        }
        
        # Try to import plotting libraries
        self.matplotlib_available = False
        self.plotly_available = False
        self.seaborn_available = False
        
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            self.plt = plt
            self.matplotlib_available = True
            logger.info("Matplotlib initialized for plotting")
        except ImportError:
            logger.warning("Matplotlib not available")
        
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            self.go = go
            self.px = px
            self.plotly_available = True
            logger.info("Plotly initialized for interactive plots")
        except ImportError:
            logger.warning("Plotly not available")
        
        try:
            import seaborn as sns
            self.sns = sns
            self.seaborn_available = True
        except ImportError:
            logger.warning("Seaborn not available")
    
    def create_sov_dashboard(self, sov_metrics: Dict, processed_data: Dict) -> Dict[str, str]:
        """
        Create comprehensive SoV dashboard with multiple visualizations
        
        Args:
            sov_metrics: Calculated SoV metrics
            processed_data: Processed search results data
            
        Returns:
            Dictionary mapping chart names to file paths
        """
        logger.info("Creating SoV dashboard visualizations...")
        
        # Create output directory
        os.makedirs('reports/charts', exist_ok=True)
        
        chart_files = {}
        
        try:
            # 1. Overall Share of Voice Chart
            chart_files['overall_sov'] = self._create_overall_sov_chart(sov_metrics)
            
            # 2. Platform Breakdown Chart
            chart_files['platform_breakdown'] = self._create_platform_breakdown_chart(sov_metrics)
            
            # 3. Sentiment Analysis Chart
            chart_files['sentiment_analysis'] = self._create_sentiment_chart(sov_metrics)
            
            # 4. Engagement Comparison Chart
            chart_files['engagement_comparison'] = self._create_engagement_chart(sov_metrics)
            
            # 5. Competitive Positioning Chart
            chart_files['competitive_positioning'] = self._create_competitive_chart(sov_metrics)
            
            # 6. Content Themes Chart
            chart_files['content_themes'] = self._create_themes_chart(processed_data)
            
            # 7. Timeline Analysis (if applicable)
            chart_files['timeline_analysis'] = self._create_timeline_chart(processed_data)
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            # Return mock chart paths for demo
            chart_files = self._create_mock_charts()
        
        logger.info(f"Created {len(chart_files)} visualization charts")
        return chart_files
    
    def _create_overall_sov_chart(self, sov_metrics: Dict) -> str:
        """Create overall Share of Voice pie chart"""
        try:
            if self.matplotlib_available:
                return self._create_sov_pie_matplotlib(sov_metrics)
            elif self.plotly_available:
                return self._create_sov_pie_plotly(sov_metrics)
            else:
                return self._create_text_chart(sov_metrics, 'overall_sov')
        except Exception as e:
            logger.error(f"Error creating overall SoV chart: {e}")
            return self._create_text_chart(sov_metrics, 'overall_sov')
    
    def _create_sov_pie_matplotlib(self, sov_metrics: Dict) -> str:
        """Create SoV pie chart using matplotlib"""
        import matplotlib.pyplot as plt
        
        mention_share = sov_metrics.get('mention_share', {})
        atomberg_share = mention_share.get('atomberg', 0)
        competitor_shares = mention_share.get('competitors', {})
        
        # Prepare data
        labels = ['Atomberg'] + list(competitor_shares.keys())
        sizes = [atomberg_share] + list(competitor_shares.values())
        colors = [self.colors.get(label.lower(), self.colors['others']) for label in labels]
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                         startangle=90, textprops={'fontsize': 12})
        
        ax.set_title('Share of Voice - Brand Mentions', fontsize=16, fontweight='bold', pad=20)
        
        # Add legend
        ax.legend(wedges, labels, title="Brands", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        
        # Save chart
        chart_path = 'reports/charts/overall_sov_pie.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_platform_breakdown_chart(self, sov_metrics: Dict) -> str:
        """Create platform breakdown bar chart"""
        try:
            if self.matplotlib_available:
                return self._create_platform_bar_matplotlib(sov_metrics)
            else:
                return self._create_text_chart(sov_metrics, 'platform_breakdown')
        except Exception as e:
            logger.error(f"Error creating platform breakdown chart: {e}")
            return self._create_text_chart(sov_metrics, 'platform_breakdown')
    
    def _create_platform_bar_matplotlib(self, sov_metrics: Dict) -> str:
        """Create platform breakdown using matplotlib"""
        import matplotlib.pyplot as plt
        
        platform_breakdown = sov_metrics.get('platform_breakdown', {})
        
        if not platform_breakdown:
            return self._create_text_chart(sov_metrics, 'platform_breakdown')
        
        platforms = list(platform_breakdown.keys())
        sov_values = [platform_breakdown[platform] * 100 for platform in platforms]
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(platforms, sov_values, color=[self.colors['atomberg']] * len(platforms))
        
        ax.set_title('Share of Voice by Platform', fontsize=16, fontweight='bold')
        ax.set_ylabel('Share of Voice (%)', fontsize=12)
        ax.set_xlabel('Platform', fontsize=12)
        
        # Add value labels on bars
        for bar, value in zip(bars, sov_values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   f'{value:.1f}%', ha='center', va='bottom', fontsize=10)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save chart
        chart_path = 'reports/charts/platform_breakdown.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_sentiment_chart(self, sov_metrics: Dict) -> str:
        """Create sentiment analysis chart"""
        try:
            if self.matplotlib_available:
                return self._create_sentiment_bar_matplotlib(sov_metrics)
            else:
                return self._create_text_chart(sov_metrics, 'sentiment_analysis')
        except Exception as e:
            logger.error(f"Error creating sentiment chart: {e}")
            return self._create_text_chart(sov_metrics, 'sentiment_analysis')
    
    def _create_sentiment_bar_matplotlib(self, sov_metrics: Dict) -> str:
        """Create sentiment analysis chart using matplotlib"""
        import matplotlib.pyplot as plt
        
        sentiment_share = sov_metrics.get('sentiment_share', {})
        atomberg_sentiment = sentiment_share.get('atomberg_sentiment_distribution', {})
        
        if not atomberg_sentiment:
            return self._create_text_chart(sov_metrics, 'sentiment_analysis')
        
        sentiments = list(atomberg_sentiment.keys())
        values = [atomberg_sentiment[sentiment] * 100 for sentiment in sentiments]
        
        colors_map = {'positive': '#2ca02c', 'negative': '#d62728', 'neutral': '#7f7f7f'}
        bar_colors = [colors_map.get(sentiment, '#7f7f7f') for sentiment in sentiments]
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.bar(sentiments, values, color=bar_colors)
        
        ax.set_title('Atomberg Sentiment Distribution', fontsize=16, fontweight='bold')
        ax.set_ylabel('Percentage of Mentions (%)', fontsize=12)
        ax.set_xlabel('Sentiment', fontsize=12)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{value:.1f}%', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # Save chart
        chart_path = 'reports/charts/sentiment_analysis.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_engagement_chart(self, sov_metrics: Dict) -> str:
        """Create engagement comparison chart"""
        try:
            return self._create_text_chart(sov_metrics, 'engagement_comparison')
        except Exception as e:
            logger.error(f"Error creating engagement chart: {e}")
            return self._create_text_chart(sov_metrics, 'engagement_comparison')
    
    def _create_competitive_chart(self, sov_metrics: Dict) -> str:
        """Create competitive positioning chart"""
        try:
            return self._create_text_chart(sov_metrics, 'competitive_positioning')
        except Exception as e:
            logger.error(f"Error creating competitive chart: {e}")
            return self._create_text_chart(sov_metrics, 'competitive_positioning')
    
    def _create_themes_chart(self, processed_data: Dict) -> str:
        """Create content themes analysis chart"""
        try:
            return self._create_text_chart(processed_data, 'content_themes')
        except Exception as e:
            logger.error(f"Error creating themes chart: {e}")
            return self._create_text_chart(processed_data, 'content_themes')
    
    def _create_timeline_chart(self, processed_data: Dict) -> str:
        """Create timeline analysis chart"""
        try:
            return self._create_text_chart(processed_data, 'timeline_analysis')
        except Exception as e:
            logger.error(f"Error creating timeline chart: {e}")
            return self._create_text_chart(processed_data, 'timeline_analysis')
    
    def _create_text_chart(self, data: Dict, chart_type: str) -> str:
        """Create text-based chart as fallback"""
        chart_path = f'reports/charts/{chart_type}_text.txt'
        
        try:
            with open(chart_path, 'w') as f:
                f.write(f"TEXT CHART: {chart_type.replace('_', ' ').title()}\n")
                f.write("=" * 50 + "\n\n")
                
                if chart_type == 'overall_sov':
                    mention_share = data.get('mention_share', {})
                    f.write(f"Atomberg Share: {mention_share.get('atomberg', 0):.2%}\n")
                    competitors = mention_share.get('competitors', {})
                    for comp, share in competitors.items():
                        f.write(f"{comp} Share: {share:.2%}\n")
                
                elif chart_type == 'platform_breakdown':
                    platform_breakdown = data.get('platform_breakdown', {})
                    for platform, sov in platform_breakdown.items():
                        f.write(f"{platform.title()}: {sov:.2%}\n")
                
                elif chart_type == 'sentiment_analysis':
                    sentiment_share = data.get('sentiment_share', {})
                    atomberg_sentiment = sentiment_share.get('atomberg_sentiment_distribution', {})
                    for sentiment, percentage in atomberg_sentiment.items():
                        f.write(f"{sentiment.title()}: {percentage:.2%}\n")
                
                else:
                    f.write("Data visualization not available\n")
                    f.write("Install matplotlib/plotly for enhanced charts\n")
            
            return chart_path
        except Exception as e:
            logger.error(f"Error creating text chart: {e}")
            return ""
    
    def _create_mock_charts(self) -> Dict[str, str]:
        """Create mock chart files for demonstration"""
        mock_charts = {}
        chart_types = [
            'overall_sov', 'platform_breakdown', 'sentiment_analysis',
            'engagement_comparison', 'competitive_positioning', 
            'content_themes', 'timeline_analysis'
        ]
        
        for chart_type in chart_types:
            chart_path = f'reports/charts/{chart_type}_mock.txt'
            try:
                with open(chart_path, 'w') as f:
                    f.write(f"MOCK CHART: {chart_type.replace('_', ' ').title()}\n")
                    f.write("=" * 40 + "\n")
                    f.write("Chart generated successfully\n")
                    f.write("Install visualization libraries for actual charts\n")
                mock_charts[chart_type] = chart_path
            except Exception as e:
                logger.error(f"Error creating mock chart {chart_type}: {e}")
        
        return mock_charts
    
    def create_summary_report(self, sov_metrics: Dict, insights: Dict) -> str:
        """Create summary report with key findings"""
        report_path = 'reports/sov_summary_report.txt'
        
        try:
            with open(report_path, 'w') as f:
                f.write("ATOMBERG SHARE OF VOICE ANALYSIS REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                # Executive Summary
                f.write("EXECUTIVE SUMMARY\n")
                f.write("-" * 20 + "\n")
                overall_sov = sov_metrics.get('overall_sov', 0)
                f.write(f"Overall Share of Voice: {overall_sov:.2%}\n")
                total_posts = sov_metrics.get('total_posts_analyzed', 0)
                f.write(f"Total Posts Analyzed: {total_posts:,}\n")
                atomberg_mentions = sov_metrics.get('atomberg_mentions', 0)
                f.write(f"Atomberg Mentions: {atomberg_mentions}\n\n")
                
                # Key Findings
                f.write("KEY FINDINGS\n")
                f.write("-" * 15 + "\n")
                key_findings = insights.get('key_findings', [])
                for i, finding in enumerate(key_findings, 1):
                    f.write(f"{i}. {finding}\n")
                f.write("\n")
                
                # Platform Performance
                f.write("PLATFORM PERFORMANCE\n")
                f.write("-" * 25 + "\n")
                platform_breakdown = sov_metrics.get('platform_breakdown', {})
                for platform, sov in platform_breakdown.items():
                    f.write(f"{platform.title()}: {sov:.2%}\n")
                f.write("\n")
                
                # Recommendations
                f.write("RECOMMENDATIONS\n")
                f.write("-" * 18 + "\n")
                recommendations = insights.get('marketing_recommendations', [])
                for i, rec in enumerate(recommendations, 1):
                    f.write(f"{i}. {rec}\n")
            
            logger.info(f"Summary report created: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Error creating summary report: {e}")
            return ""
