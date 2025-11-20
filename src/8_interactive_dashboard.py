"""
Interactive Dashboard - Plotly ашиглан интерактив дашборд

Энэ модуль нь интерактив веб-дашборд үүсгэнэ.
HTML файл хэлбэрээр хадгалж browser дээр үзэж болно.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).parent))


class InteractiveDashboard:
    """
    Интерактив дашборд үүсгэгч

    Plotly ашиглан интерактив график үүсгэж HTML хэлбэрээр хадгална.
    """

    def __init__(
        self,
        matched_file: str = 'data/processed/matched_events.csv',
        stats_file: str = 'results/reports/statistical_results.json',
        output_file: str = 'results/visualizations/interactive_dashboard.html'
    ):
        """
        Dashboard эхлүүлэх

        Args:
            matched_file: Таарсан өгөгдлийн файл
            stats_file: Статистик үр дүнгийн файл
            output_file: Output HTML файл
        """
        self.matched_file = Path(matched_file)
        self.stats_file = Path(stats_file)
        self.output_file = Path(output_file)

        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> pd.DataFrame:
        """Өгөгдөл унших"""
        print("📖 Dashboard өгөгдөл уншиж байна...")

        df = pd.read_csv(self.matched_file)
        df['event_date'] = pd.to_datetime(df['event_date'])

        # Day type column нэмэх
        df['day_type'] = 'Normal'
        df.loc[df['start_is_bad_day'] == True, 'day_type'] = 'Bad Day'
        df.loc[df['start_is_good_day'] == True, 'day_type'] = 'Good Day'

        print(f"  ✓ {len(df)} үйл явдал уншигдлаа")

        return df

    def create_timeline_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Интерактив timeline chart

        Args:
            df: DataFrame

        Returns:
            Plotly Figure
        """
        fig = px.scatter(
            df,
            x='event_date',
            y='severity_score',
            color='day_type',
            size='severity_score',
            hover_name='event_name',
            hover_data=['category', 'deaths', 'affected_population'],
            color_discrete_map={
                'Bad Day': '#ff6b6b',
                'Good Day': '#51cf66',
                'Normal': '#868e96'
            },
            title='World Disaster Events Timeline (Interactive)',
            labels={
                'event_date': 'Date',
                'severity_score': 'Severity Score',
                'day_type': 'Lunar Day Type'
            }
        )

        fig.update_layout(
            hovermode='closest',
            height=500
        )

        # Add threshold line
        fig.add_hline(y=70, line_dash="dash", line_color="orange",
                     annotation_text="High Severity Threshold")

        return fig

    def create_category_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Категориор ангилал (sunburst)

        Args:
            df: DataFrame

        Returns:
            Plotly Figure
        """
        # Aggregate by category and day type
        agg_df = df.groupby(['category', 'day_type']).agg({
            'severity_score': 'sum',
            'event_name': 'count'
        }).reset_index()

        agg_df.columns = ['category', 'day_type', 'total_severity', 'count']

        fig = px.sunburst(
            agg_df,
            path=['category', 'day_type'],
            values='count',
            color='total_severity',
            color_continuous_scale='RdYlGn_r',
            title='Event Distribution by Category and Lunar Day Type'
        )

        fig.update_layout(height=500)

        return fig

    def create_severity_distribution(self, df: pd.DataFrame) -> go.Figure:
        """
        Severity distribution (box + violin)

        Args:
            df: DataFrame

        Returns:
            Plotly Figure
        """
        fig = px.violin(
            df,
            x='day_type',
            y='severity_score',
            color='day_type',
            box=True,
            points='all',
            color_discrete_map={
                'Bad Day': '#ff6b6b',
                'Good Day': '#51cf66',
                'Normal': '#868e96'
            },
            title='Severity Score Distribution by Lunar Day Type',
            labels={
                'day_type': 'Lunar Day Type',
                'severity_score': 'Severity Score'
            }
        )

        fig.update_layout(
            showlegend=False,
            height=500
        )

        return fig

    def create_yearly_trend(self, df: pd.DataFrame) -> go.Figure:
        """
        Жилийн trend шугаман график

        Args:
            df: DataFrame

        Returns:
            Plotly Figure
        """
        # Aggregate by year
        yearly = df.groupby('year').agg({
            'severity_score': ['sum', 'mean', 'count'],
            'start_is_bad_day': 'sum'
        }).reset_index()

        yearly.columns = ['year', 'total_severity', 'avg_severity', 'event_count', 'bad_day_count']

        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Total severity (bar)
        fig.add_trace(
            go.Bar(
                x=yearly['year'],
                y=yearly['total_severity'],
                name='Total Severity',
                marker_color='#868e96',
                opacity=0.6
            ),
            secondary_y=False
        )

        # Event count (line)
        fig.add_trace(
            go.Scatter(
                x=yearly['year'],
                y=yearly['event_count'],
                name='Event Count',
                mode='lines+markers',
                line=dict(color='#ff6b6b', width=2)
            ),
            secondary_y=True
        )

        # Bad day events (line)
        fig.add_trace(
            go.Scatter(
                x=yearly['year'],
                y=yearly['bad_day_count'],
                name='Bad Day Events',
                mode='lines+markers',
                line=dict(color='#ffd43b', width=2, dash='dash')
            ),
            secondary_y=True
        )

        fig.update_layout(
            title='Yearly Trend: Severity and Event Count',
            height=500
        )

        fig.update_yaxes(title_text="Total Severity", secondary_y=False)
        fig.update_yaxes(title_text="Event Count", secondary_y=True)

        return fig

    def create_correlation_heatmap(self, df: pd.DataFrame) -> go.Figure:
        """
        Корреляцийн heatmap

        Args:
            df: DataFrame

        Returns:
            Plotly Figure
        """
        # Select numeric columns
        numeric_cols = ['severity_score', 'deaths', 'affected_population',
                       'start_is_bad_day', 'start_is_good_day', 'month', 'year']

        available_cols = [col for col in numeric_cols if col in df.columns]
        corr_matrix = df[available_cols].corr()

        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            title='Correlation Matrix',
            labels=dict(color="Correlation")
        )

        fig.update_layout(height=500)

        return fig

    def create_dashboard(self) -> None:
        """
        Бүрэн дашборд үүсгэх
        """
        print("\n🎨 Interactive dashboard үүсгэж байна...")

        # Load data
        df = self.load_data()

        # Create all charts
        timeline_fig = self.create_timeline_chart(df)
        category_fig = self.create_category_chart(df)
        severity_fig = self.create_severity_distribution(df)
        yearly_fig = self.create_yearly_trend(df)
        corr_fig = self.create_correlation_heatmap(df)

        # Combine into single HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mongolian Lunar Calendar vs World Disasters - Interactive Dashboard</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f8f9fa;
        }}
        .header {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .full-width {{
            grid-column: 1 / -1;
        }}
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .summary-box {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .stat {{
            display: inline-block;
            padding: 15px;
            margin: 5px;
            background: #f1f3f5;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #495057;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #868e96;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #868e96;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌙 Mongolian Lunar Calendar vs World Disasters</h1>
        <p>Interactive Analysis Dashboard (1942-2005)</p>
    </div>

    <div class="summary-box" style="margin-bottom: 20px;">
        <h2>📊 Summary Statistics</h2>
        <div class="stat">
            <div class="stat-value">{len(df)}</div>
            <div class="stat-label">Total Events</div>
        </div>
        <div class="stat">
            <div class="stat-value">{(df['start_is_bad_day'] == True).sum()}</div>
            <div class="stat-label">On Bad Days</div>
        </div>
        <div class="stat">
            <div class="stat-value">{df['severity_score'].mean():.1f}</div>
            <div class="stat-label">Avg Severity</div>
        </div>
        <div class="stat">
            <div class="stat-value">{df['year'].min()}-{df['year'].max()}</div>
            <div class="stat-label">Date Range</div>
        </div>
    </div>

    <div class="dashboard-grid">
        <div class="chart-container full-width">
            {timeline_fig.to_html(full_html=False, include_plotlyjs='cdn')}
        </div>

        <div class="chart-container">
            {severity_fig.to_html(full_html=False, include_plotlyjs=False)}
        </div>

        <div class="chart-container">
            {category_fig.to_html(full_html=False, include_plotlyjs=False)}
        </div>

        <div class="chart-container full-width">
            {yearly_fig.to_html(full_html=False, include_plotlyjs=False)}
        </div>

        <div class="chart-container full-width">
            {corr_fig.to_html(full_html=False, include_plotlyjs=False)}
        </div>
    </div>

    <div class="footer">
        <p>Generated by Mongolian Lunar Calendar Analysis Pipeline</p>
        <p>🔬 This is academic research. Correlation does not imply causation.</p>
    </div>
</body>
</html>
        """

        # Save HTML
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"  ✅ Dashboard хадгалагдлаа: {self.output_file}")
        print(f"  💡 Browser дээр нээхдээ: open {self.output_file}")


def main():
    """Main функц"""
    print("="*60)
    print("🎨 INTERACTIVE DASHBOARD")
    print("="*60)

    try:
        dashboard = InteractiveDashboard()
        dashboard.create_dashboard()

        print("\n✅ Dashboard амжилттай үүсгэгдлээ!")

    except FileNotFoundError as e:
        print(f"\n❌ Файл олдсонгүй: {e}")

    except Exception as e:
        print(f"\n❌ Алдаа: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
