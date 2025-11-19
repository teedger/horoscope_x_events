"""
4. Statistical Analysis - Статистик шинжилгээ

Энэ script нь сарны муу өдөр ба гамшигт үйл явдлын хоорондох
корреляцийг статистик аргаар шинжилнэ.

Тестүүд:
- Chi-Square Test (Independence)
- T-Test (Severity харьцуулалт)
- Pearson Correlation
- Additional analyses
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple
from scipy import stats
from scipy.stats import chi2_contingency, ttest_ind, pearsonr
import sys

# Utility модулиудыг import хийх
sys.path.append(str(Path(__file__).parent))
from utils.checkpoint_manager import CheckpointManager


class StatisticalAnalyzer:
    """
    Статистик шинжилгээний класс

    Сарны муу өдөр ба гамшигт үйл явдлын хоорондох
    статистик хамаарлыг тогтооно.
    """

    def __init__(
        self,
        matched_file: str = 'data/processed/matched_events.csv',
        lunar_file: str = 'data/processed/lunar_bad_days_gregorian.csv',
        output_file: str = 'results/reports/statistical_results.json'
    ):
        """
        Analyzer эхлүүлэх

        Args:
            matched_file: Таарсан өгөгдлийн файл
            lunar_file: Сарны өдрүүдийн файл
            output_file: Үр дүн хадгалах JSON файл
        """
        self.matched_file = Path(matched_file)
        self.lunar_file = Path(lunar_file)
        self.output_file = Path(output_file)

        # Output folder үүсгэх
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        self.results = {}

    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Өгөгдөл унших

        Returns:
            Tuple (matched_df, lunar_df)
        """
        if not self.matched_file.exists():
            raise FileNotFoundError(
                f"❌ Таарсан өгөгдлийн файл олдсонгүй: {self.matched_file}\n"
                f"Эхлээд '3_data_matcher.py' ажиллуулна уу."
            )

        if not self.lunar_file.exists():
            raise FileNotFoundError(
                f"❌ Сарны календарийн файл олдсонгүй: {self.lunar_file}\n"
                f"Эхлээд '1_lunar_converter.py' ажиллуулна уу."
            )

        print("📖 Өгөгдөл уншиж байна...")

        matched_df = pd.read_csv(self.matched_file)
        lunar_df = pd.read_csv(self.lunar_file)

        print(f"  ✓ Таарсан үйл явдал: {len(matched_df)}")
        print(f"  ✓ Сарны өдрүүд: {len(lunar_df)}")

        return matched_df, lunar_df

    def test_chi_square(self, matched_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Chi-Square Test - Independence тест

        H0: Муу өдөр ба гамшигт үйл явдал хамааралгүй
        H1: Хамааралтай

        Args:
            matched_df: Таарсан өгөгдлийн DataFrame

        Returns:
            Тестийн үр дүн
        """
        print("\n🧪 Chi-Square Test of Independence...")

        # Contingency table үүсгэх
        # Rows: Bad Day vs Not Bad Day
        # Cols: Disaster Event vs No Disaster
        #
        # Асуудал: Бидэнд зөвхөн үйл явдлууд байна, "үйл явдалгүй" өдрүүд байхгүй
        # Тиймээс бид сарны муу өдөр ба энгийн өдрүүдийн тооноос
        # үйл явдал гарсан өдрүүдийг харьцуулна

        # Муу өдрүүдийн тоо
        bad_days_total = (matched_df['start_is_bad_day'] == True).sum()
        not_bad_days_total = (matched_df['start_is_bad_day'] == False).sum()

        # Contingency table
        # Энэ тохиолдолд: Chi-square-ийг үйл явдлын категори дээр хийе
        # Өөр хувилбар: Severity-ийн түвшингээр ангилах

        # Хувилбар 1: Өндөр severity (>= 70) vs Бага severity
        high_severity_threshold = 70

        high_severity_bad_day = len(matched_df[
            (matched_df['start_is_bad_day'] == True) &
            (matched_df['severity_score'] >= high_severity_threshold)
        ])
        high_severity_not_bad_day = len(matched_df[
            (matched_df['start_is_bad_day'] == False) &
            (matched_df['severity_score'] >= high_severity_threshold)
        ])
        low_severity_bad_day = len(matched_df[
            (matched_df['start_is_bad_day'] == True) &
            (matched_df['severity_score'] < high_severity_threshold)
        ])
        low_severity_not_bad_day = len(matched_df[
            (matched_df['start_is_bad_day'] == False) &
            (matched_df['severity_score'] < high_severity_threshold)
        ])

        contingency_table = np.array([
            [high_severity_bad_day, high_severity_not_bad_day],
            [low_severity_bad_day, low_severity_not_bad_day]
        ])

        # Chi-square тест
        chi2, p_value, dof, expected = chi2_contingency(contingency_table)

        result = {
            'test_name': 'Chi-Square Test of Independence',
            'contingency_table': contingency_table.tolist(),
            'chi_square_statistic': float(chi2),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'expected_frequencies': expected.tolist(),
            'significance_level': 0.05,
            'is_significant': p_value < 0.05,
            'interpretation': self._interpret_chi_square(p_value)
        }

        print(f"  Chi-square статистик: {chi2:.4f}")
        print(f"  P-value: {p_value:.4f}")
        print(f"  Үр дүн: {result['interpretation']}")

        return result

    def test_t_test(self, matched_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Independent T-Test - Severity score харьцуулалт

        H0: Муу өдрүүд ба бусад өдрүүдийн severity score адилхан
        H1: Өөр

        Args:
            matched_df: Таарсан өгөгдлийн DataFrame

        Returns:
            Тестийн үр дүн
        """
        print("\n🧪 Independent T-Test (Severity Comparison)...")

        # Хоёр бүлэг ангилах
        bad_day_severities = matched_df[matched_df['start_is_bad_day'] == True]['severity_score']
        not_bad_day_severities = matched_df[matched_df['start_is_bad_day'] == False]['severity_score']

        # T-test
        t_statistic, p_value = ttest_ind(bad_day_severities, not_bad_day_severities)

        result = {
            'test_name': 'Independent T-Test (Severity Scores)',
            'bad_day_mean': float(bad_day_severities.mean()),
            'bad_day_std': float(bad_day_severities.std()),
            'bad_day_n': int(len(bad_day_severities)),
            'not_bad_day_mean': float(not_bad_day_severities.mean()),
            'not_bad_day_std': float(not_bad_day_severities.std()),
            'not_bad_day_n': int(len(not_bad_day_severities)),
            't_statistic': float(t_statistic),
            'p_value': float(p_value),
            'significance_level': 0.05,
            'is_significant': p_value < 0.05,
            'mean_difference': float(bad_day_severities.mean() - not_bad_day_severities.mean()),
            'interpretation': self._interpret_t_test(p_value, bad_day_severities.mean(), not_bad_day_severities.mean())
        }

        print(f"  Муу өдөр дундаж: {result['bad_day_mean']:.2f} (n={result['bad_day_n']})")
        print(f"  Бусад өдөр дундаж: {result['not_bad_day_mean']:.2f} (n={result['not_bad_day_n']})")
        print(f"  T-статистик: {t_statistic:.4f}")
        print(f"  P-value: {p_value:.4f}")
        print(f"  Үр дүн: {result['interpretation']}")

        return result

    def test_correlation(self, matched_df: pd.DataFrame, lunar_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Pearson Correlation - Сар бүрийн корреляц

        Сар бүрийн:
        - Муу өдрийн тоо
        - Гамшигт үйл явдлын тоо
        - Нийт severity score

        Args:
            matched_df: Таарсан өгөгдлийн DataFrame
            lunar_df: Сарны өдрүүдийн DataFrame

        Returns:
            Тестийн үр дүн
        """
        print("\n🧪 Pearson Correlation Analysis...")

        # Gregorian он/сар-аар group хийх
        lunar_df['gregorian_date'] = pd.to_datetime(lunar_df['gregorian_date'])
        lunar_df['year_month'] = lunar_df['gregorian_date'].dt.to_period('M')

        matched_df['event_date'] = pd.to_datetime(matched_df['event_date'])
        matched_df['year_month'] = matched_df['event_date'].dt.to_period('M')

        # Сар бүрийн муу өдрийн тоо
        bad_days_per_month = lunar_df[lunar_df['is_bad_day'] == True].groupby('year_month').size()

        # Сар бүрийн үйл явдлын тоо
        events_per_month = matched_df.groupby('year_month').size()

        # Сар бүрийн severity
        severity_per_month = matched_df.groupby('year_month')['severity_score'].sum()

        # Common months (зөвхөн өгөгдөл байгаа саруудыг авах)
        common_months = bad_days_per_month.index.intersection(events_per_month.index)

        if len(common_months) < 3:
            print("  ⚠ Хангалттай өгөгдөл байхгүй (< 3 сар)")
            return {
                'test_name': 'Pearson Correlation',
                'error': 'Insufficient data',
                'interpretation': 'Хангалттай өгөгдөл байхгүй корреляц тооцоолох'
            }

        # Корреляц тооцоолох
        bad_days_values = bad_days_per_month[common_months].values
        events_values = events_per_month[common_months].values
        severity_values = severity_per_month[common_months].values

        # Корреляц 1: Муу өдөр vs Үйл явдлын тоо
        corr1, p_value1 = pearsonr(bad_days_values, events_values)

        # Корреляц 2: Муу өдөр vs Severity
        corr2, p_value2 = pearsonr(bad_days_values, severity_values)

        result = {
            'test_name': 'Pearson Correlation (Monthly)',
            'months_analyzed': int(len(common_months)),
            'correlation_bad_days_vs_event_count': {
                'r': float(corr1),
                'p_value': float(p_value1),
                'is_significant': p_value1 < 0.05,
                'interpretation': self._interpret_correlation(corr1, p_value1)
            },
            'correlation_bad_days_vs_severity': {
                'r': float(corr2),
                'p_value': float(p_value2),
                'is_significant': p_value2 < 0.05,
                'interpretation': self._interpret_correlation(corr2, p_value2)
            }
        }

        print(f"  Шинжилсэн сарын тоо: {len(common_months)}")
        print(f"\n  Корреляц 1 (Муу өдөр vs Үйл явдлын тоо):")
        print(f"    r = {corr1:.4f}, p = {p_value1:.4f}")
        print(f"    {result['correlation_bad_days_vs_event_count']['interpretation']}")
        print(f"\n  Корреляц 2 (Муу өдөр vs Severity):")
        print(f"    r = {corr2:.4f}, p = {p_value2:.4f}")
        print(f"    {result['correlation_bad_days_vs_severity']['interpretation']}")

        return result

    def descriptive_statistics(self, matched_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Тодорхойлогч статистик

        Args:
            matched_df: Таарсан өгөгдлийн DataFrame

        Returns:
            Хураангуй статистик
        """
        print("\n📊 Тодорхойлогч статистик...")

        result = {
            'total_events': int(len(matched_df)),
            'events_on_bad_days': int((matched_df['start_is_bad_day'] == True).sum()),
            'events_on_good_days': int((matched_df['start_is_good_day'] == True).sum()),
            'events_on_normal_days': int((matched_df['start_is_bad_day'] == False).sum() - (matched_df['start_is_good_day'] == True).sum()),
            'percentage_on_bad_days': float((matched_df['start_is_bad_day'] == True).sum() / len(matched_df) * 100),
            'severity_overall_mean': float(matched_df['severity_score'].mean()),
            'severity_overall_median': float(matched_df['severity_score'].median()),
            'severity_overall_std': float(matched_df['severity_score'].std()),
            'date_range': {
                'start': matched_df['year'].min(),
                'end': matched_df['year'].max()
            }
        }

        print(f"  Нийт үйл явдал: {result['total_events']}")
        print(f"  Муу өдрүүд дээр: {result['events_on_bad_days']} ({result['percentage_on_bad_days']:.1f}%)")
        print(f"  Дундаж severity: {result['severity_overall_mean']:.2f}")

        return result

    def run_all_tests(self) -> Dict[str, Any]:
        """
        Бүх статистик тест ажиллуулах

        Returns:
            Бүх тестийн үр дүн
        """
        print("="*60)
        print("📈 СТАТИСТИК ШИНЖИЛГЭЭ")
        print("="*60)

        # Өгөгдөл унших
        matched_df, lunar_df = self.load_data()

        # Тестүүд ажиллуулах
        self.results['descriptive_statistics'] = self.descriptive_statistics(matched_df)
        self.results['chi_square_test'] = self.test_chi_square(matched_df)
        self.results['t_test'] = self.test_t_test(matched_df)
        self.results['correlation_analysis'] = self.test_correlation(matched_df, lunar_df)

        # Overall interpretation
        self.results['overall_conclusion'] = self._generate_conclusion()

        return self.results

    def _interpret_chi_square(self, p_value: float) -> str:
        """Chi-square тестийн тайлбар"""
        if p_value < 0.001:
            return "Маш хүчтэй нотолгоо (p < 0.001): Муу өдөр ба үйл явдлын хүндрэл ХАМААРАЛТАЙ"
        elif p_value < 0.01:
            return "Хүчтэй нотолгоо (p < 0.01): Муу өдөр ба үйл явдлын хүндрэл хамааралтай"
        elif p_value < 0.05:
            return "Статистик ач холбогдолтой (p < 0.05): Муу өдөр ба үйл явдлын хүндрэл хамааралтай"
        else:
            return "Статистик ач холбогдол БАЙХГҮЙ (p >= 0.05): Муу өдөр ба үйл явдал хамааралгүй"

    def _interpret_t_test(self, p_value: float, mean1: float, mean2: float) -> str:
        """T-test тайлбар"""
        diff = mean1 - mean2
        if p_value < 0.05:
            if diff > 0:
                return f"Статистик ач холбогдолтой (p < 0.05): Муу өдрүүд дээр severity ӨНДӨР (+{diff:.2f})"
            else:
                return f"Статистик ач холбогдолтой (p < 0.05): Муу өдрүүд дээр severity БАГА ({diff:.2f})"
        else:
            return "Статистик ач холбогдол БАЙХГҮЙ: Муу өдөр ба бусад өдрийн severity адилхан"

    def _interpret_correlation(self, r: float, p_value: float) -> str:
        """Correlation тайлбар"""
        if p_value >= 0.05:
            return f"Корреляц байхгүй (p >= 0.05, r={r:.3f})"

        # Statistically significant
        if abs(r) < 0.3:
            strength = "сул"
        elif abs(r) < 0.7:
            strength = "дунд"
        else:
            strength = "хүчтэй"

        direction = "эерэг" if r > 0 else "сөрөг"

        return f"{strength.capitalize()} {direction} корреляц (r={r:.3f}, p={p_value:.4f})"

    def _generate_conclusion(self) -> str:
        """Ерөнхий дүгнэлт"""
        conclusions = []

        # Chi-square
        if 'chi_square_test' in self.results:
            if self.results['chi_square_test'].get('is_significant'):
                conclusions.append("✓ Chi-square тест хамаарал илрүүлсэн")
            else:
                conclusions.append("✗ Chi-square тест хамаарал илрүүлээгүй")

        # T-test
        if 't_test' in self.results:
            if self.results['t_test'].get('is_significant'):
                diff = self.results['t_test']['mean_difference']
                if diff > 0:
                    conclusions.append(f"✓ Муу өдрүүд дээр severity өндөр (+{diff:.1f})")
                else:
                    conclusions.append(f"✗ Муу өдрүүд дээр severity бага ({diff:.1f})")
            else:
                conclusions.append("○ Severity-д ялгаа байхгүй")

        # Correlation
        if 'correlation_analysis' in self.results:
            corr1 = self.results['correlation_analysis'].get('correlation_bad_days_vs_event_count', {})
            if corr1.get('is_significant'):
                conclusions.append(f"✓ Муу өдөр ба үйл явдлын тоо хамааралтай (r={corr1['r']:.3f})")
            else:
                conclusions.append("✗ Муу өдөр ба үйл явдлын тоо хамааралгүй")

        if len(conclusions) == 0:
            return "Статистик шинжилгээ дутуу"

        return "\n".join(conclusions)

    def save_results(self) -> None:
        """Үр дүнг JSON файлд хадгалах"""
        import json

        print(f"\n💾 Үр дүн хадгалж байна: {self.output_file}")

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print("✓ Амжилттай хадгалагдлаа!")

    def print_summary(self) -> None:
        """Хураангуй хэвлэх"""
        print("\n" + "="*60)
        print("📊 СТАТИСТИК ШИНЖИЛГЭЭНИЙ ҮР ДҮН")
        print("="*60)

        if 'overall_conclusion' in self.results:
            print("\n" + self.results['overall_conclusion'])

        print("\n" + "="*60)


def main():
    """
    Main функц - script ажиллуулах
    """
    print("="*60)
    print("📈 СТАТИСТИК ШИНЖИЛГЭЭ")
    print("="*60)

    try:
        # Analyzer үүсгэх
        analyzer = StatisticalAnalyzer()

        # Бүх тест ажиллуулах
        results = analyzer.run_all_tests()

        # Үр дүн хадгалах
        analyzer.save_results()

        # Хураангуй харуулах
        analyzer.print_summary()

        print("\n✅ Амжилттай дууслаа!")
        return results

    except FileNotFoundError as e:
        print(f"\n{e}")
        return None

    except Exception as e:
        print(f"\n❌ Алдаа гарлаа: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()
