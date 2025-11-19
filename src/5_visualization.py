"""
5. Visualization - Өгөгдлийн визуализаци

Энэ script нь шинжилгээний үр дүнг олон төрлийн график,
зураг ашиглан харуулна.

Визуализацийн төрлүүд:
1. Timeline Chart - Цаг хугацааны дагуу үйл явдал
2. Heatmap - Он/сарын гамшгийн тархалт
3. Box Plot - Муу өдөр vs бусад өдрийн severity
4. Correlation Matrix - Хамаарлын матриц
5. Event Distribution - Үйл явдлын төрөл
6. Statistical Summary - Статистик хураангуй
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Any, Optional
import json
import sys

# Style тохиргоо
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Монгол фонт тохиргоо (хэрэв системд байвал)
try:
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']
except:
    pass
plt.rcParams['axes.unicode_minus'] = False


class Visualizer:
    """
    Visualization класс

    Өгөгдлийн визуализацийг үүсгэх.
    """

    def __init__(
        self,
        matched_file: str = 'data/processed/matched_events.csv',
        lunar_file: str = 'data/processed/lunar_bad_days_gregorian.csv',
        stats_file: str = 'results/reports/statistical_results.json',
        output_dir: str = 'results/visualizations'
    ):
        """
        Visualizer эхлүүлэх

        Args:
            matched_file: Таарсан өгөгдлийн файл
            lunar_file: Сарны өдрүүдийн файл
            stats_file: Статистик үр дүнгийн файл
            output_dir: Зураг хадгалах хавтас
        """
        self.matched_file = Path(matched_file)
        self.lunar_file = Path(lunar_file)
        self.stats_file = Path(stats_file)
        self.output_dir = Path(output_dir)

        # Output folder үүсгэх
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Өгөгдөл
        self.matched_df = None
        self.lunar_df = None
        self.stats = None

    def load_data(self) -> None:
        """Өгөгдөл унших"""
        print("📖 Өгөгдөл уншиж байна...")

        # Таарсан өгөгдөл
        self.matched_df = pd.read_csv(self.matched_file)
        self.matched_df['event_date'] = pd.to_datetime(self.matched_df['event_date'])
        print(f"  ✓ Таарсан үйл явдал: {len(self.matched_df)}")

        # Сарны өдрүүд
        self.lunar_df = pd.read_csv(self.lunar_file)
        self.lunar_df['gregorian_date'] = pd.to_datetime(self.lunar_df['gregorian_date'])
        print(f"  ✓ Сарны өдрүүд: {len(self.lunar_df)}")

        # Статистик үр дүн
        if self.stats_file.exists():
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)
            print(f"  ✓ Статистик үр дүн унших")
        else:
            print(f"  ⚠ Статистик үр дүн олдсонгүй (зарим график үүсгэгдэхгүй)")

    def plot_timeline(self, ax: Optional[plt.Axes] = None) -> plt.Figure:
        """
        1. Timeline Chart - Цаг хугацааны дагуу үйл явдал

        Args:
            ax: Matplotlib axes (эсвэл None)

        Returns:
            Figure объект
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(16, 8))
        else:
            fig = ax.figure

        # Муу өдөр / бусад өдөр ялган өнгөлөх
        bad_day_events = self.matched_df[self.matched_df['start_is_bad_day'] == True]
        other_events = self.matched_df[self.matched_df['start_is_bad_day'] == False]

        # Plot хийх
        ax.scatter(
            other_events['event_date'],
            other_events['severity_score'],
            c='gray',
            alpha=0.5,
            s=100,
            label='Normal/Good Days',
            edgecolors='black',
            linewidth=0.5
        )

        ax.scatter(
            bad_day_events['event_date'],
            bad_day_events['severity_score'],
            c='red',
            alpha=0.8,
            s=150,
            label='Bad Days',
            edgecolors='darkred',
            linewidth=1,
            marker='^'
        )

        # Formatting
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Severity Score', fontsize=12, fontweight='bold')
        ax.set_title('World Disaster Events Timeline\n(Red = Bad Days, Gray = Other Days)',
                     fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)

        # Severity threshold шугам
        ax.axhline(y=70, color='orange', linestyle='--', alpha=0.5, label='High Severity Threshold')

        plt.tight_layout()

        return fig

    def plot_heatmap(self, ax: Optional[plt.Axes] = None) -> plt.Figure:
        """
        2. Heatmap - Он/сарын гамшгийн тархалт

        Args:
            ax: Matplotlib axes

        Returns:
            Figure объект
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(14, 10))
        else:
            fig = ax.figure

        # Он/сарын pivot table үүсгэх
        self.matched_df['month_name'] = self.matched_df['event_date'].dt.month

        # Муу өдөр дээр болсон үйл явдлуудын severity-г нэгтгэх
        pivot_data = self.matched_df.pivot_table(
            values='severity_score',
            index='year',
            columns='month_name',
            aggfunc='sum',
            fill_value=0
        )

        # Heatmap
        sns.heatmap(
            pivot_data,
            cmap='YlOrRd',
            annot=False,
            fmt='.0f',
            cbar_kws={'label': 'Total Severity Score'},
            ax=ax
        )

        ax.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax.set_ylabel('Year', fontsize=12, fontweight='bold')
        ax.set_title('Disaster Severity Heatmap by Year and Month', fontsize=14, fontweight='bold')

        # Month labels
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ax.set_xticklabels(month_labels, rotation=0)

        plt.tight_layout()

        return fig

    def plot_box_comparison(self, ax: Optional[plt.Axes] = None) -> plt.Figure:
        """
        3. Box Plot - Муу өдөр vs бусад өдрийн severity харьцуулалт

        Args:
            ax: Matplotlib axes

        Returns:
            Figure объект
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 8))
        else:
            fig = ax.figure

        # Өгөгдөл бэлдэх
        data_to_plot = []
        labels = []

        # Муу өдөр
        bad_day_scores = self.matched_df[self.matched_df['start_is_bad_day'] == True]['severity_score']
        data_to_plot.append(bad_day_scores)
        labels.append(f'Bad Days\n(n={len(bad_day_scores)})')

        # Сайн өдөр
        good_day_scores = self.matched_df[self.matched_df['start_is_good_day'] == True]['severity_score']
        if len(good_day_scores) > 0:
            data_to_plot.append(good_day_scores)
            labels.append(f'Good Days\n(n={len(good_day_scores)})')

        # Энгийн өдөр
        normal_day_scores = self.matched_df[
            (self.matched_df['start_is_bad_day'] == False) &
            (self.matched_df['start_is_good_day'] == False)
        ]['severity_score']
        data_to_plot.append(normal_day_scores)
        labels.append(f'Normal Days\n(n={len(normal_day_scores)})')

        # Box plot
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                        showmeans=True, meanline=True)

        # Өнгөлөх
        colors = ['#ff6b6b', '#51cf66', '#868e96']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        # Formatting
        ax.set_ylabel('Severity Score', fontsize=12, fontweight='bold')
        ax.set_title('Severity Score Comparison\nby Lunar Calendar Day Type',
                     fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        # Дундаж утгуудыг текстээр харуулах
        for i, scores in enumerate(data_to_plot):
            mean_val = scores.mean()
            median_val = scores.median()
            ax.text(i+1, mean_val, f'μ={mean_val:.1f}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout()

        return fig

    def plot_event_distribution(self, ax: Optional[plt.Axes] = None) -> plt.Figure:
        """
        4. Event Distribution - Үйл явдлын төрлийн тархалт

        Args:
            ax: Matplotlib axes

        Returns:
            Figure объект
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 8))
        else:
            fig = ax.figure

        # Категориор тоолох
        category_counts = self.matched_df.groupby(['category', 'start_is_bad_day']).size().unstack(fill_value=0)

        # Stacked bar chart
        category_counts.plot(kind='bar', stacked=False, ax=ax,
                            color=['#868e96', '#ff6b6b'], alpha=0.8)

        ax.set_xlabel('Event Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Events', fontsize=12, fontweight='bold')
        ax.set_title('Event Distribution by Category and Lunar Day Type',
                     fontsize=14, fontweight='bold')
        ax.legend(['Not Bad Day', 'Bad Day'], loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        return fig

    def plot_statistical_summary(self, ax: Optional[plt.Axes] = None) -> plt.Figure:
        """
        5. Statistical Summary - Статистик хураангуй

        Args:
            ax: Matplotlib axes

        Returns:
            Figure объект
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 8))
        else:
            fig = ax.figure

        ax.axis('off')

        # Статистик мэдээлэл
        if self.stats:
            desc_stats = self.stats.get('descriptive_statistics', {})
            t_test = self.stats.get('t_test', {})
            chi_square = self.stats.get('chi_square_test', {})
            corr = self.stats.get('correlation_analysis', {})

            summary_text = f"""
╔══════════════════════════════════════════════════════════════╗
║         STATISTICAL ANALYSIS SUMMARY                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  📊 DESCRIPTIVE STATISTICS                                    ║
║  ─────────────────────────────────────────────────────────   ║
║  Total Events: {desc_stats.get('total_events', 'N/A'):>45}  ║
║  Events on Bad Days: {desc_stats.get('events_on_bad_days', 'N/A'):>39} ({desc_stats.get('percentage_on_bad_days', 0):.1f}%)  ║
║  Events on Good Days: {desc_stats.get('events_on_good_days', 'N/A'):>38}  ║
║  Events on Normal Days: {desc_stats.get('events_on_normal_days', 'N/A'):>36}  ║
║                                                               ║
║  Overall Severity Mean: {desc_stats.get('severity_overall_mean', 0):>34.2f}  ║
║  Overall Severity Median: {desc_stats.get('severity_overall_median', 0):>32.2f}  ║
║                                                               ║
║  🧪 T-TEST RESULTS (Severity Comparison)                      ║
║  ─────────────────────────────────────────────────────────   ║
║  Bad Days Mean: {t_test.get('bad_day_mean', 0):>44.2f}  ║
║  Not Bad Days Mean: {t_test.get('not_bad_day_mean', 0):>40.2f}  ║
║  Mean Difference: {t_test.get('mean_difference', 0):>42.2f}  ║
║  P-value: {t_test.get('p_value', 1):>52.4f}  ║
║  Significant: {('YES' if t_test.get('is_significant') else 'NO'):>48}  ║
║                                                               ║
║  🧪 CHI-SQUARE TEST                                           ║
║  ─────────────────────────────────────────────────────────   ║
║  Chi-square: {chi_square.get('chi_square_statistic', 0):>47.4f}  ║
║  P-value: {chi_square.get('p_value', 1):>52.4f}  ║
║  Significant: {('YES' if chi_square.get('is_significant') else 'NO'):>48}  ║
║                                                               ║
║  📈 OVERALL CONCLUSION                                        ║
║  ─────────────────────────────────────────────────────────   ║
"""

            # Conclusion
            if self.stats.get('overall_conclusion'):
                for line in self.stats['overall_conclusion'].split('\n'):
                    summary_text += f"║  {line:<60} ║\n"

            summary_text += "╚══════════════════════════════════════════════════════════════╝"

        else:
            summary_text = "Statistical results not available.\nPlease run 4_statistical_analysis.py first."

        ax.text(0.5, 0.5, summary_text,
                ha='center', va='center',
                fontsize=9, fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        ax.set_title('Statistical Analysis Summary', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        return fig

    def create_comprehensive_visualization(self) -> None:
        """
        Бүх визуализацийг нэг зурган дээр үүсгэх

        6 subplot бүхий comprehensive figure
        """
        print("\n🎨 Comprehensive visualization үүсгэж байна...")

        fig = plt.figure(figsize=(24, 16))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # 1. Timeline (top row, full width)
        ax1 = fig.add_subplot(gs[0, :])
        self.plot_timeline(ax1)

        # 2. Heatmap
        ax2 = fig.add_subplot(gs[1, 0])
        self.plot_heatmap(ax2)

        # 3. Box Plot
        ax3 = fig.add_subplot(gs[1, 1])
        self.plot_box_comparison(ax3)

        # 4. Event Distribution
        ax4 = fig.add_subplot(gs[2, 0])
        self.plot_event_distribution(ax4)

        # 5. Statistical Summary
        ax5 = fig.add_subplot(gs[2, 1])
        self.plot_statistical_summary(ax5)

        # Main title
        fig.suptitle('Mongolian Lunar Calendar "Bad Days" vs World Disaster Events\nComprehensive Analysis (1942-2005)',
                     fontsize=18, fontweight='bold', y=0.995)

        # Хадгалах
        output_file = self.output_dir / 'comprehensive_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"  ✓ Хадгалагдлаа: {output_file}")

        plt.close()

    def create_individual_plots(self) -> None:
        """
        График бүрийг тус тусад нь үүсгэх
        """
        print("\n🎨 Тус тусын график үүсгэж байна...")

        plots = [
            ('timeline', self.plot_timeline),
            ('heatmap', self.plot_heatmap),
            ('box_comparison', self.plot_box_comparison),
            ('event_distribution', self.plot_event_distribution),
            ('statistical_summary', self.plot_statistical_summary)
        ]

        for name, plot_func in plots:
            fig = plot_func()
            output_file = self.output_dir / f'{name}.png'
            fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"  ✓ {name}.png хадгалагдлаа")
            plt.close(fig)

    def generate_all(self) -> None:
        """
        Бүх визуализацийг үүсгэх
        """
        print("="*60)
        print("🎨 VISUALIZATION ҮҮСГЭЛТ")
        print("="*60)

        # Өгөгдөл унших
        self.load_data()

        # Comprehensive visualization
        self.create_comprehensive_visualization()

        # Individual plots
        self.create_individual_plots()

        print("\n✅ Бүх график амжилттай үүсгэгдлээ!")
        print(f"📂 Хавтас: {self.output_dir}")


def main():
    """
    Main функц - script ажиллуулах
    """
    print("="*60)
    print("🎨 VISUALIZATION")
    print("="*60)

    try:
        # Visualizer үүсгэх
        visualizer = Visualizer()

        # Бүх график үүсгэх
        visualizer.generate_all()

        print("\n✅ Амжилттай дууслаа!")

    except FileNotFoundError as e:
        print(f"\n❌ Файл олдсонгүй: {e}")
        print("Эхлээд өмнөх script-үүдийг ажиллуулна уу.")
        return None

    except Exception as e:
        print(f"\n❌ Алдаа гарлаа: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
