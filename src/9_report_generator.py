"""
HTML Report Generator - Бүрэн тайлан үүсгэх

Энэ модуль нь бүх шинжилгээний үр дүнг нэгтгэж
HTML тайлан үүсгэнэ.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import base64
import sys

sys.path.append(str(Path(__file__).parent))


class ReportGenerator:
    """
    HTML тайлан үүсгэгч

    Бүх үр дүнг нэгтгэж publication-ready тайлан бэлдэнэ.
    """

    def __init__(
        self,
        matched_file: str = 'data/processed/matched_events.csv',
        stats_file: str = 'results/reports/statistical_results.json',
        ml_file: str = 'results/reports/ml_results.json',
        viz_dir: str = 'results/visualizations',
        output_file: str = 'results/reports/final_report.html'
    ):
        """
        Generator эхлүүлэх
        """
        self.matched_file = Path(matched_file)
        self.stats_file = Path(stats_file)
        self.ml_file = Path(ml_file)
        self.viz_dir = Path(viz_dir)
        self.output_file = Path(output_file)

        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> dict:
        """Бүх өгөгдөл унших"""
        data = {}

        # Matched events
        if self.matched_file.exists():
            data['matched'] = pd.read_csv(self.matched_file)

        # Statistical results
        if self.stats_file.exists():
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                data['stats'] = json.load(f)

        # ML results
        if self.ml_file.exists():
            with open(self.ml_file, 'r', encoding='utf-8') as f:
                data['ml'] = json.load(f)

        return data

    def image_to_base64(self, image_path: Path) -> str:
        """Зургийг base64 руу хөрвүүлэх"""
        if not image_path.exists():
            return ""

        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def generate_report(self) -> None:
        """HTML тайлан үүсгэх"""
        print("📝 HTML тайлан үүсгэж байна...")

        data = self.load_data()

        # Get statistics
        matched_df = data.get('matched', pd.DataFrame())
        stats = data.get('stats', {})
        ml = data.get('ml', {})

        # Descriptive stats
        desc = stats.get('descriptive_statistics', {})
        t_test = stats.get('t_test', {})
        chi_square = stats.get('chi_square_test', {})

        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mongolian Lunar Calendar vs World Disasters - Final Report</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Georgia', serif;
            line-height: 1.8;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #fafafa;
            color: #333;
        }}
        .cover {{
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white;
            border-radius: 15px;
            margin-bottom: 40px;
        }}
        .cover h1 {{
            font-size: 2.5em;
            margin: 0 0 20px 0;
        }}
        .cover .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .cover .date {{
            margin-top: 30px;
            opacity: 0.7;
        }}
        h2 {{
            color: #0f3460;
            border-bottom: 3px solid #e94560;
            padding-bottom: 10px;
            margin-top: 50px;
        }}
        h3 {{
            color: #16213e;
            margin-top: 30px;
        }}
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #e94560;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #0f3460;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #0f3460;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .highlight {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }}
        .success {{
            background: #d4edda;
            border-left-color: #28a745;
        }}
        .danger {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}
        .info {{
            background: #d1ecf1;
            border-left-color: #17a2b8;
        }}
        .image-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .image-container img {{
            max-width: 100%;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        .conclusion {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-top: 40px;
        }}
        .conclusion h2 {{
            color: white;
            border-bottom-color: rgba(255,255,255,0.3);
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
        }}
        @media print {{
            body {{
                background: white;
            }}
            .section {{
                box-shadow: none;
                border: 1px solid #ddd;
            }}
        }}
    </style>
</head>
<body>
    <div class="cover">
        <h1>🌙 Mongolian Lunar Calendar</h1>
        <h1>vs World Disasters</h1>
        <p class="subtitle">Statistical Correlation Analysis Report</p>
        <p class="date">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>

    <div class="section">
        <h2>1. Executive Summary</h2>

        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-value">{desc.get('total_events', 'N/A')}</div>
                <div class="stat-label">Total Events Analyzed</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{desc.get('events_on_bad_days', 'N/A')}</div>
                <div class="stat-label">Events on Bad Days</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{desc.get('percentage_on_bad_days', 0):.1f}%</div>
                <div class="stat-label">Bad Day Percentage</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{desc.get('severity_overall_mean', 0):.1f}</div>
                <div class="stat-label">Average Severity</div>
            </div>
        </div>

        <div class="highlight info">
            <strong>Research Question:</strong> Is there a statistically significant correlation
            between Mongolian lunar calendar "bad days" and world disaster events?
        </div>
    </div>

    <div class="section">
        <h2>2. Data Overview</h2>

        <h3>2.1 Lunar Calendar Data</h3>
        <p>The Mongolian lunar calendar classifies days into several types:</p>
        <ul>
            <li><strong>Bad Days (modon, ters):</strong> Days considered inauspicious</li>
            <li><strong>Good Days (baljin, dash):</strong> Days considered auspicious</li>
            <li><strong>Haircut Days:</strong> Days suitable for haircuts</li>
        </ul>

        <h3>2.2 World Disaster Events</h3>
        <p>Events analyzed include:</p>
        <ul>
            <li>Wars and armed conflicts</li>
            <li>Natural disasters (earthquakes, tsunamis, cyclones)</li>
            <li>Terrorist attacks</li>
            <li>Industrial disasters</li>
            <li>Assassinations of political figures</li>
            <li>Economic crises</li>
        </ul>

        <h3>2.3 Severity Scoring System</h3>
        <p>Each event was scored on a 0-100 scale based on:</p>
        <table>
            <tr>
                <th>Factor</th>
                <th>Max Points</th>
                <th>Description</th>
            </tr>
            <tr>
                <td>Death Toll</td>
                <td>40</td>
                <td>Number of fatalities</td>
            </tr>
            <tr>
                <td>Affected Population</td>
                <td>30</td>
                <td>People impacted</td>
            </tr>
            <tr>
                <td>Geopolitical Impact</td>
                <td>30</td>
                <td>Category-based impact score</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>3. Statistical Analysis Results</h2>

        <h3>3.1 T-Test Results (Severity Comparison)</h3>
        <div class="stat-grid">
            <div class="stat-box">
                <div class="stat-value">{t_test.get('bad_day_mean', 0):.2f}</div>
                <div class="stat-label">Bad Days Mean Severity</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{t_test.get('not_bad_day_mean', 0):.2f}</div>
                <div class="stat-label">Other Days Mean Severity</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{t_test.get('p_value', 1):.4f}</div>
                <div class="stat-label">P-value</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{'YES' if t_test.get('is_significant') else 'NO'}</div>
                <div class="stat-label">Statistically Significant</div>
            </div>
        </div>

        <div class="highlight {'success' if t_test.get('is_significant') else 'danger'}">
            <strong>Interpretation:</strong> {t_test.get('interpretation', 'N/A')}
        </div>

        <h3>3.2 Chi-Square Test Results</h3>
        <p>
            Chi-square statistic: <strong>{chi_square.get('chi_square_statistic', 0):.4f}</strong><br>
            Degrees of freedom: <strong>{chi_square.get('degrees_of_freedom', 0)}</strong><br>
            P-value: <strong>{chi_square.get('p_value', 1):.4f}</strong><br>
            Significant at α=0.05: <strong>{'YES' if chi_square.get('is_significant') else 'NO'}</strong>
        </p>

        <div class="highlight {'success' if chi_square.get('is_significant') else 'danger'}">
            <strong>Interpretation:</strong> {chi_square.get('interpretation', 'N/A')}
        </div>
    </div>

    <div class="section">
        <h2>4. Visualizations</h2>

        <h3>4.1 Comprehensive Analysis</h3>
        <div class="image-container">
            <p><em>See: results/visualizations/comprehensive_analysis.png</em></p>
        </div>

        <h3>4.2 Interactive Dashboard</h3>
        <p>An interactive dashboard is available at: <code>results/visualizations/interactive_dashboard.html</code></p>
    </div>

    {'<div class="section"><h2>5. Machine Learning Results</h2>' + self._generate_ml_section(ml) + '</div>' if ml and 'error' not in ml else ''}

    <div class="conclusion">
        <h2>6. Conclusion</h2>

        <h3>Key Findings</h3>
        <p>{stats.get('overall_conclusion', 'Analysis results pending.')}</p>

        <h3>Limitations</h3>
        <ul>
            <li>Date conversion accuracy between lunar and Gregorian calendars</li>
            <li>Limited sample size (63 years of data)</li>
            <li>Subjective severity scoring methodology</li>
            <li>Potential selection bias in event collection</li>
        </ul>

        <h3>Future Work</h3>
        <ul>
            <li>Expand date range with more historical data</li>
            <li>Include regional analysis (Mongolia-specific events)</li>
            <li>Develop more sophisticated ML models</li>
            <li>Cross-reference with other traditional calendars</li>
        </ul>
    </div>

    <div class="footer">
        <p><strong>Disclaimer:</strong> This is academic research. Correlation does not imply causation.
        The findings should not be interpreted as validation of traditional beliefs.</p>
        <p>Generated by Mongolian Lunar Calendar Analysis Pipeline</p>
        <p>&copy; {datetime.now().year}</p>
    </div>
</body>
</html>
        """

        # Save HTML
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"  ✅ Тайлан хадгалагдлаа: {self.output_file}")

    def _generate_ml_section(self, ml: dict) -> str:
        """ML section үүсгэх"""
        if not ml or 'models' not in ml:
            return "<p>ML results not available.</p>"

        models = ml.get('models', {})
        best = ml.get('best_model', 'N/A')

        html = f"""
        <p><strong>Best Model:</strong> {best}</p>
        <table>
            <tr>
                <th>Model</th>
                <th>Accuracy</th>
                <th>F1 Score</th>
                <th>ROC-AUC</th>
            </tr>
        """

        for name, metrics in models.items():
            html += f"""
            <tr>
                <td>{name}</td>
                <td>{metrics.get('accuracy', 0):.2%}</td>
                <td>{metrics.get('f1_score', 0):.2%}</td>
                <td>{metrics.get('roc_auc', 0):.2%}</td>
            </tr>
            """

        html += "</table>"

        if 'interpretation' in ml:
            html += f"""
            <div class="highlight info">
                <strong>ML Interpretation:</strong><br>
                {ml['interpretation'].replace(chr(10), '<br>')}
            </div>
            """

        return html


def main():
    """Main функц"""
    print("="*60)
    print("📝 HTML REPORT GENERATOR")
    print("="*60)

    try:
        generator = ReportGenerator()
        generator.generate_report()

        print("\n✅ HTML тайлан амжилттай үүсгэгдлээ!")

    except Exception as e:
        print(f"\n❌ Алдаа: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
