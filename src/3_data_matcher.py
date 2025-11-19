"""
3. Data Matcher - Үйл явдлыг сарны өдрүүдтэй таарах

Энэ script нь дэлхийн гамшигт үйл явдлуудыг сарны календарийн
"муу өдрүүд"-тэй таарч, шинжилгээнд бэлэн өгөгдөл үүсгэнэ.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sys

# Utility модулиудыг import хийх
sys.path.append(str(Path(__file__).parent))
from utils.checkpoint_manager import CheckpointManager


class EventLunarMatcher:
    """
    Үйл явдлыг сарны өдрүүдтэй таарах класс

    Гамшигт үйл явдлуудыг сарны календарийн муу/сайн өдрүүдтэй
    тааруулж, корреляц шинжилгээнд бэлдэнэ.
    """

    def __init__(
        self,
        lunar_file: str = 'data/processed/lunar_bad_days_gregorian.csv',
        events_file: str = 'data/processed/world_disasters.csv',
        output_file: str = 'data/processed/matched_events.csv'
    ):
        """
        Matcher эхлүүлэх

        Args:
            lunar_file: Сарны өдрүүдийн CSV файл
            events_file: Үйл явдлуудын CSV файл
            output_file: Output CSV файл
        """
        self.lunar_file = Path(lunar_file)
        self.events_file = Path(events_file)
        self.output_file = Path(output_file)
        self.checkpoint_manager = CheckpointManager()

        # Output folder үүсгэх
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> tuple:
        """
        Хоёр өгөгдлийг унших

        Returns:
            Tuple (lunar_df, events_df)

        Raises:
            FileNotFoundError: Файл олдоогүй бол
        """
        if not self.lunar_file.exists():
            raise FileNotFoundError(
                f"❌ Сарны календарийн файл олдсонгүй: {self.lunar_file}\n"
                f"Эхлээд '1_lunar_converter.py' ажиллуулна уу."
            )

        if not self.events_file.exists():
            raise FileNotFoundError(
                f"❌ Үйл явдлын файл олдсонгүй: {self.events_file}\n"
                f"Эхлээд '2_event_scraper.py' ажиллуулна уу."
            )

        print("📖 Өгөгдөл уншиж байна...")

        # Сарны календар
        lunar_df = pd.read_csv(self.lunar_file)
        lunar_df['gregorian_date'] = pd.to_datetime(lunar_df['gregorian_date'])
        print(f"  ✓ Сарны өдрүүд: {len(lunar_df)}")

        # Үйл явдлууд
        events_df = pd.read_csv(self.events_file)
        events_df['date'] = pd.to_datetime(events_df['date'])
        events_df['end_date'] = pd.to_datetime(events_df['end_date'])
        print(f"  ✓ Үйл явдлууд: {len(events_df)}")

        return lunar_df, events_df

    def create_date_lookup(self, lunar_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Огноогоор хурдан хайлт хийх dict үүсгэх

        Args:
            lunar_df: Сарны өдрүүдийн DataFrame

        Returns:
            {date_string: {is_bad_day, is_good_day, day_type, ...}}
        """
        print("🔧 Огноо lookup бүтэц үүсгэж байна...")

        lookup = {}

        for _, row in lunar_df.iterrows():
            date_str = row['gregorian_date'].strftime('%Y-%m-%d')

            if date_str not in lookup:
                lookup[date_str] = {
                    'is_bad_day': False,
                    'is_good_day': False,
                    'is_haircut_day': False,
                    'day_types': []
                }

            # Өдрийн төрлүүдийг нэмэх
            lookup[date_str]['day_types'].append(row['day_type'])

            if row['is_bad_day']:
                lookup[date_str]['is_bad_day'] = True
            if row['is_good_day']:
                lookup[date_str]['is_good_day'] = True
            if row['is_haircut_day']:
                lookup[date_str]['is_haircut_day'] = True

        print(f"  ✓ {len(lookup)} өдөр бүртгэгдлээ")

        return lookup

    def match_event_to_lunar(
        self,
        event: pd.Series,
        date_lookup: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Нэг үйл явдлыг сарны өдөртэй таарах

        Стратеги:
        - Богино үйл явдал (1 өдөр): Эхлэх өдрөөр нь
        - Урт үйл явдал (>1 өдөр): Эхлэх өдрөөр нь (мөн дараах өдрүүд дээр ч шалгана)

        Args:
            event: Үйл явдлын Series
            date_lookup: Огноо lookup dict

        Returns:
            Таарсан мэдээлэл
        """
        start_date = event['date']
        end_date = event['end_date']
        duration = (end_date - start_date).days + 1

        # Үндсэн мэдээлэл
        result = {
            'event_name': event['name'],
            'event_date': start_date.strftime('%Y-%m-%d'),
            'event_end_date': end_date.strftime('%Y-%m-%d'),
            'event_duration_days': duration,
            'category': event['category'],
            'deaths': event['deaths'],
            'affected_population': event['affected_population'],
            'severity_score': event['severity_score'],
            'year': event['year'],
            'month': event['month'],
        }

        # Эхлэх өдрийн мэдээлэл
        start_date_str = start_date.strftime('%Y-%m-%d')
        if start_date_str in date_lookup:
            result['start_is_bad_day'] = date_lookup[start_date_str]['is_bad_day']
            result['start_is_good_day'] = date_lookup[start_date_str]['is_good_day']
            result['start_day_types'] = ','.join(date_lookup[start_date_str]['day_types'])
        else:
            result['start_is_bad_day'] = False
            result['start_is_good_day'] = False
            result['start_day_types'] = 'normal'

        # Урт үйл явдлын хувьд: Аль нэг өдөр нь муу өдөр мөн эсэхийг шалгах
        if duration > 1:
            bad_days_count = 0
            good_days_count = 0

            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                if date_str in date_lookup:
                    if date_lookup[date_str]['is_bad_day']:
                        bad_days_count += 1
                    if date_lookup[date_str]['is_good_day']:
                        good_days_count += 1
                current_date += timedelta(days=1)

            result['any_bad_day_in_duration'] = bad_days_count > 0
            result['bad_days_count_in_duration'] = bad_days_count
            result['good_days_count_in_duration'] = good_days_count
        else:
            result['any_bad_day_in_duration'] = result['start_is_bad_day']
            result['bad_days_count_in_duration'] = 1 if result['start_is_bad_day'] else 0
            result['good_days_count_in_duration'] = 1 if result['start_is_good_day'] else 0

        return result

    def match_all(self) -> pd.DataFrame:
        """
        Бүх үйл явдлыг таарах

        Returns:
            Таарсан өгөгдлийн DataFrame
        """
        # Checkpoint шалгах
        if self.checkpoint_manager.exists('matched'):
            print("📂 Checkpoint олдсон! Өмнө нь таарсан өгөгдлийг ашиглана.")
            df = self.checkpoint_manager.load('matched')
            return df

        # Өгөгдөл унших
        lunar_df, events_df = self.load_data()

        # Date lookup үүсгэх
        date_lookup = self.create_date_lookup(lunar_df)

        # Таарах
        print("\n🔄 Үйл явдлуудыг сарны өдрүүдтэй таарж байна...")

        matched_data = []
        for idx, event in events_df.iterrows():
            matched = self.match_event_to_lunar(event, date_lookup)
            matched_data.append(matched)

        # DataFrame үүсгэх
        df = pd.DataFrame(matched_data)

        print(f"\n✓ {len(df)} үйл явдал таарсан")

        # Статистик
        bad_day_events = df['start_is_bad_day'].sum()
        good_day_events = df['start_is_good_day'].sum()
        normal_day_events = len(df) - bad_day_events - good_day_events

        print(f"\n📊 Эхлэх өдрөөр нь:")
        print(f"   Муу өдрүүд дээр эхэлсэн: {bad_day_events} ({bad_day_events/len(df)*100:.1f}%)")
        print(f"   Сайн өдрүүд дээр эхэлсэн: {good_day_events} ({good_day_events/len(df)*100:.1f}%)")
        print(f"   Энгийн өдрүүд дээр эхэлсэн: {normal_day_events} ({normal_day_events/len(df)*100:.1f}%)")

        # Checkpoint хадгалах
        self.checkpoint_manager.save('matched', df, {
            'total_events': len(df),
            'bad_day_events': int(bad_day_events),
            'good_day_events': int(good_day_events)
        })

        return df

    def save_to_csv(self, df: pd.DataFrame) -> None:
        """
        DataFrame-г CSV файлд хадгалах

        Args:
            df: Хадгалах DataFrame
        """
        print(f"\n💾 CSV файл хадгалж байна: {self.output_file}")
        df.to_csv(self.output_file, index=False, encoding='utf-8')
        print(f"✓ Амжилттай хадгалагдлаа!")

    def generate_summary(self, df: pd.DataFrame) -> None:
        """
        Дэлгэрэнгүй хураангуй мэдээлэл

        Args:
            df: Мэдээлэл агуулсан DataFrame
        """
        print("\n" + "="*60)
        print("📊 ТААРСАН ӨГӨГДЛИЙН ХУРААНГУЙ")
        print("="*60)

        print(f"\n📅 Нийт үйл явдал: {len(df)}")
        print(f"📅 Огтлолцоо: {df['year'].min()}-{df['year'].max()}")

        # Муу өдөр vs Энгийн өдөр
        print(f"\n🌙 Сарны өдрийн ангилал (эхлэх өдрөөр):")
        bad_count = df['start_is_bad_day'].sum()
        good_count = df['start_is_good_day'].sum()
        normal_count = len(df) - bad_count - good_count

        print(f"   Муу өдөр: {bad_count} ({bad_count/len(df)*100:.1f}%)")
        print(f"   Сайн өдөр: {good_count} ({good_count/len(df)*100:.1f}%)")
        print(f"   Энгийн өдөр: {normal_count} ({normal_count/len(df)*100:.1f}%)")

        # Severity харьцуулалт
        print(f"\n🎯 Severity оноо харьцуулалт:")
        bad_day_severity = df[df['start_is_bad_day'] == True]['severity_score'].mean()
        normal_day_severity = df[df['start_is_bad_day'] == False]['severity_score'].mean()

        print(f"   Муу өдрүүд: {bad_day_severity:.1f} (дундаж)")
        print(f"   Бусад өдрүүд: {normal_day_severity:.1f} (дундаж)")
        print(f"   Ялгаа: {bad_day_severity - normal_day_severity:+.1f}")

        # Категориор
        print(f"\n📂 Категориор (эхлэх өдөр муу өдөр мөн үү):")
        for category in df['category'].unique():
            cat_df = df[df['category'] == category]
            bad_in_cat = cat_df['start_is_bad_day'].sum()
            print(f"   {category}: {bad_in_cat}/{len(cat_df)} ({bad_in_cat/len(cat_df)*100:.0f}%)")

        print("\n" + "="*60)


def main():
    """
    Main функц - script ажиллуулах
    """
    print("="*60)
    print("🔗 ҮЙЛЯВДЛЫГ САРНЫ ӨДРҮҮДТЭЙ ТААРАХ")
    print("="*60)

    try:
        # Matcher үүсгэх
        matcher = EventLunarMatcher()

        # Таарах
        df = matcher.match_all()

        # CSV хадгалах
        matcher.save_to_csv(df)

        # Хураангуй харуулах
        matcher.generate_summary(df)

        print("\n✅ Амжилттай дууслаа!")
        return df

    except FileNotFoundError as e:
        print(f"\n{e}")
        return None

    except Exception as e:
        print(f"\n❌ Алдаа гарлаа: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    df = main()
