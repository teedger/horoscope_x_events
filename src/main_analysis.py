#!/usr/bin/env python3
"""
Main Analysis Script - Бүх шинжилгээг нэгтгэсэн script

Энэ script нь бүх модулиудыг дарааллаар ажиллуулж,
эхнээс төгсгөл хүртэл автоматаар гүйцэтгэнэ.

Ажиллуулах:
    python src/main_analysis.py

Эсвэл:
    python -m src.main_analysis
"""

import sys
from pathlib import Path
from datetime import datetime
import argparse

# Модулиудыг import хийх
sys.path.append(str(Path(__file__).parent))

from utils.checkpoint_manager import CheckpointManager


class MainAnalysisPipeline:
    """
    Үндсэн шинжилгээний pipeline

    Бүх алхмуудыг дарааллаар гүйцэтгэнэ.
    """

    def __init__(self, skip_existing: bool = True, data_file: str = None):
        """
        Pipeline эхлүүлэх

        Args:
            skip_existing: Checkpoint байвал алгасах эсэх
            data_file: Horoscope JSON файлын зам
        """
        self.skip_existing = skip_existing
        self.data_file = data_file
        self.checkpoint_manager = CheckpointManager()

        self.start_time = datetime.now()

    def print_header(self) -> None:
        """Header хэвлэх"""
        print("\n" + "="*70)
        print("🌙 MONGOLIAN LUNAR CALENDAR vs WORLD DISASTERS")
        print("   Correlation Analysis Pipeline")
        print("="*70)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Skip existing: {self.skip_existing}")
        print("="*70 + "\n")

    def step_1_lunar_converter(self) -> bool:
        """
        Алхам 1: Сарны огноо хөрвүүлэлт

        Returns:
            Амжилттай эсэх
        """
        print("\n" + "─"*70)
        print("📅 STEP 1/5: Lunar Calendar Conversion")
        print("─"*70)

        if self.skip_existing and self.checkpoint_manager.exists('lunar_converted'):
            print("✓ Checkpoint байна, алгасч байна.")
            return True

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("lunar_converter", Path(__file__).parent / "1_lunar_converter.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            LunarCalendarProcessor = module.LunarCalendarProcessor

            # Data file override
            if self.data_file:
                processor = LunarCalendarProcessor(input_file=self.data_file)
            else:
                processor = LunarCalendarProcessor()

            df = processor.process_all()
            processor.save_to_csv(df)
            processor.generate_summary(df)

            print("\n✅ Step 1 амжилттай дууслаа!")
            return True

        except FileNotFoundError as e:
            print(f"\n❌ Файл олдсонгүй: {e}")
            print("\n💡 Зааварчилгаа:")
            print("   horoscope_list_20250112.json файлыг data/raw/ хавтаст хуулна уу")
            print("   Эсвэл --data-file параметр ашиглана уу:")
            print("   python main_analysis.py --data-file /path/to/horoscope.json")
            return False

        except Exception as e:
            print(f"\n❌ Алдаа: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step_2_event_scraper(self) -> bool:
        """
        Алхам 2: Үйл явдал цуглуулах

        Returns:
            Амжилттай эсэх
        """
        print("\n" + "─"*70)
        print("🌍 STEP 2/5: World Events Collection")
        print("─"*70)

        if self.skip_existing and self.checkpoint_manager.exists('events_scraped'):
            print("✓ Checkpoint байна, алгасч байна.")
            return True

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("event_scraper", Path(__file__).parent / "2_event_scraper.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            DisasterEventCollector = module.DisasterEventCollector

            collector = DisasterEventCollector()
            df = collector.process_events()
            collector.save_to_csv(df)
            collector.generate_summary(df)

            print("\n✅ Step 2 амжилттай дууслаа!")
            return True

        except Exception as e:
            print(f"\n❌ Алдаа: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step_3_data_matcher(self) -> bool:
        """
        Алхам 3: Өгөгдөл таарах

        Returns:
            Амжилттай эсэх
        """
        print("\n" + "─"*70)
        print("🔗 STEP 3/5: Data Matching")
        print("─"*70)

        if self.skip_existing and self.checkpoint_manager.exists('matched'):
            print("✓ Checkpoint байна, алгасч байна.")
            return True

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("data_matcher", Path(__file__).parent / "3_data_matcher.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            EventLunarMatcher = module.EventLunarMatcher

            matcher = EventLunarMatcher()
            df = matcher.match_all()
            matcher.save_to_csv(df)
            matcher.generate_summary(df)

            print("\n✅ Step 3 амжилттай дууслаа!")
            return True

        except Exception as e:
            print(f"\n❌ Алдаа: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step_4_statistical_analysis(self) -> bool:
        """
        Алхам 4: Статистик шинжилгээ

        Returns:
            Амжилттай эсэх
        """
        print("\n" + "─"*70)
        print("📊 STEP 4/5: Statistical Analysis")
        print("─"*70)

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("statistical_analysis", Path(__file__).parent / "4_statistical_analysis.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            StatisticalAnalyzer = module.StatisticalAnalyzer

            analyzer = StatisticalAnalyzer()
            results = analyzer.run_all_tests()
            analyzer.save_results()
            analyzer.print_summary()

            print("\n✅ Step 4 амжилттай дууслаа!")
            return True

        except Exception as e:
            print(f"\n❌ Алдаа: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step_5_visualization(self) -> bool:
        """
        Алхам 5: Визуализаци

        Returns:
            Амжилттай эсэх
        """
        print("\n" + "─"*70)
        print("🎨 STEP 5/5: Visualization")
        print("─"*70)

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("visualization", Path(__file__).parent / "5_visualization.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            Visualizer = module.Visualizer

            visualizer = Visualizer()
            visualizer.generate_all()

            print("\n✅ Step 5 амжилттай дууслаа!")
            return True

        except Exception as e:
            print(f"\n❌ Алдаа: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self) -> bool:
        """
        Pipeline ажиллуулах

        Returns:
            Амжилттай эсэх
        """
        self.print_header()

        # Алхам 1: Lunar converter
        if not self.step_1_lunar_converter():
            print("\n❌ Step 1 амжилтгүй боллоо. Зогслоо.")
            return False

        # Алхам 2: Event scraper
        if not self.step_2_event_scraper():
            print("\n❌ Step 2 амжилтгүй боллоо. Зогслоо.")
            return False

        # Алхам 3: Data matcher
        if not self.step_3_data_matcher():
            print("\n❌ Step 3 амжилтгүй боллоо. Зогслоо.")
            return False

        # Алхам 4: Statistical analysis
        if not self.step_4_statistical_analysis():
            print("\n❌ Step 4 амжилтгүй боллоо. Зогслоо.")
            return False

        # Алхам 5: Visualization
        if not self.step_5_visualization():
            print("\n❌ Step 5 амжилтгүй боллоо. Зогслоо.")
            return False

        # Амжилттай дууслаа
        self.print_summary()
        return True

    def print_summary(self) -> None:
        """Эцсийн хураангуй"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        print("\n" + "="*70)
        print("✅ БҮГД АМЖИЛТТАЙ ДУУСЛАА!")
        print("="*70)
        print(f"Started:  {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration}")
        print("\n📂 Үр дүнгүүд:")
        print("   - data/processed/lunar_bad_days_gregorian.csv")
        print("   - data/processed/world_disasters.csv")
        print("   - data/processed/matched_events.csv")
        print("   - results/reports/statistical_results.json")
        print("   - results/visualizations/comprehensive_analysis.png")
        print("   - results/visualizations/*.png")
        print("\n💡 Дараагийн алхам:")
        print("   Visualization-уудыг нээж үзнэ үү:")
        print("   open results/visualizations/comprehensive_analysis.png")
        print("="*70 + "\n")


def main():
    """
    Main функц - CLI interface

    Command-line arguments:
        --no-skip: Checkpoint-уудыг алгасахгүй, бүгдийг дахин ажиллуулах
        --data-file: Horoscope JSON файлын зам
    """
    parser = argparse.ArgumentParser(
        description='Mongolian Lunar Calendar vs World Disasters - Complete Analysis Pipeline'
    )
    parser.add_argument(
        '--no-skip',
        action='store_true',
        help='Do not skip existing checkpoints (re-run everything)'
    )
    parser.add_argument(
        '--data-file',
        type=str,
        help='Path to horoscope JSON file (default: data/raw/horoscope_list_20250112.json)'
    )

    args = parser.parse_args()

    # Pipeline үүсгэх
    pipeline = MainAnalysisPipeline(
        skip_existing=not args.no_skip,
        data_file=args.data_file
    )

    # Ажиллуулах
    success = pipeline.run()

    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
