"""
1. Lunar Calendar Converter - Сарны календарийг Григорийн огноо руу хөрвүүлэх

Энэ script нь horoscope_list.json файлыг унших, сарны огноонуудыг
Григорийн огноо руу хөрвүүлж, CSV файл үүсгэнэ.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import sys

# Utility модулиудыг import хийх
sys.path.append(str(Path(__file__).parent))
from utils.checkpoint_manager import CheckpointManager
from utils.progress_tracker import create_progress_bar
from utils.date_converter import LunarDateConverter


class LunarCalendarProcessor:
    """
    Сарны календарийн өгөгдлийг боловсруулагч

    horoscope_list.json файлыг уншиж, бүх сарны огноонуудыг
    Григорийн огноо руу хөрвүүлнэ.
    """

    def __init__(
        self,
        input_file: str = 'data/raw/horoscope_list_20250112.json',
        output_file: str = 'data/processed/lunar_bad_days_gregorian.csv'
    ):
        """
        Processor эхлүүлэх

        Args:
            input_file: Input JSON файлын зам
            output_file: Output CSV файлын зам
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.converter = LunarDateConverter()
        self.checkpoint_manager = CheckpointManager()

        # Output folder үүсгэх
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def load_horoscope_data(self) -> List[Dict[str, Any]]:
        """
        Horoscope JSON файл унших

        Returns:
            Сарын мэдээллийн жагсаалт

        Raises:
            FileNotFoundError: Файл олдоогүй бол
        """
        if not self.input_file.exists():
            raise FileNotFoundError(
                f"❌ Horoscope файл олдсонгүй: {self.input_file}\n"
                f"Файлыг {self.input_file} руу хуулна уу."
            )

        print(f"📖 Horoscope өгөгдөл уншиж байна: {self.input_file}")

        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"✓ {len(data)} сарын мэдээлэл уншигдлаа")
        return data

    def convert_month_data(
        self,
        month_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Нэг сарын өгөгдлийг боловсруулах

        Args:
            month_data: Сарын мэдээлэл
                {
                    "year": "2000",
                    "month": "1",
                    "haircut_days": [...],
                    "baljin_days": [...],
                    "dash_days": [...],
                    "modon_days": [...],
                    "ters_days": [...]
                }

        Returns:
            Хөрвүүлсэн өдрүүдийн жагсаалт
        """
        lunar_year = int(month_data['year'])
        lunar_month = int(month_data['month'].strip())

        results = []

        # Өдрийн төрөл бүрийг боловсруулах
        day_types = {
            'haircut': month_data.get('haircut_days', []),
            'baljin': month_data.get('baljin_days', []),  # Сайн өдөр
            'dash': month_data.get('dash_days', []),      # Сайн өдөр
            'modon': month_data.get('modon_days', []),    # МУУ ӨДӨР
            'ters': month_data.get('ters_days', [])       # МУУ ӨДӨР
        }

        for day_type, days in day_types.items():
            for day_str in days:
                lunar_day = int(day_str.strip())

                # Сарны огноог Григорийн огноо руу хөрвүүлэх
                gregorian_date = self.converter.lunar_to_gregorian(
                    lunar_year,
                    lunar_month,
                    lunar_day
                )

                if gregorian_date:
                    # Өдрийн категори тодорхойлох
                    is_bad_day = day_type in ['modon', 'ters']
                    is_good_day = day_type in ['baljin', 'dash']

                    results.append({
                        'lunar_year': lunar_year,
                        'lunar_month': lunar_month,
                        'lunar_day': lunar_day,
                        'gregorian_date': gregorian_date.strftime('%Y-%m-%d'),
                        'gregorian_year': gregorian_date.year,
                        'gregorian_month': gregorian_date.month,
                        'gregorian_day': gregorian_date.day,
                        'day_type': day_type,
                        'is_bad_day': is_bad_day,
                        'is_good_day': is_good_day,
                        'is_haircut_day': day_type == 'haircut'
                    })

        return results

    def process_all(self) -> pd.DataFrame:
        """
        Бүх сарын мэдээллийг боловсруулах

        Returns:
            Бүх өдрүүдийг агуулсан DataFrame

        Examples:
            >>> processor = LunarCalendarProcessor()
            >>> df = processor.process_all()
            >>> print(df.head())
        """
        # Checkpoint шалгах
        if self.checkpoint_manager.exists('lunar_converted'):
            print("📂 Checkpoint олдсон! Өмнө нь хөрвүүлсэн өгөгдлийг ашиглана.")
            df = self.checkpoint_manager.load('lunar_converted')
            return df

        # Horoscope өгөгдөл унших
        horoscope_data = self.load_horoscope_data()

        # Бүх сарын мэдээллийг боловсруулах
        all_days = []

        print(f"\n🔄 Сарны огноонуудыг Григорийн огноо руу хөрвүүлж байна...")

        for month_data in create_progress_bar(
            horoscope_data,
            desc="Хөрвүүлж байна"
        ):
            converted_days = self.convert_month_data(month_data)
            all_days.extend(converted_days)

        # DataFrame үүсгэх
        df = pd.DataFrame(all_days)

        # Огноогоор эрэмбэлэх
        df = df.sort_values('gregorian_date').reset_index(drop=True)

        print(f"\n✓ Нийт {len(df)} өдөр хөрвүүлэгдлээ")
        print(f"  - Муу өдөр: {df['is_bad_day'].sum()}")
        print(f"  - Сайн өдөр: {df['is_good_day'].sum()}")
        print(f"  - Үс засах өдөр: {df['is_haircut_day'].sum()}")
        print(f"  - Огтлолцоо: {df['gregorian_year'].min()}-{df['gregorian_year'].max()}")

        # Checkpoint хадгалах
        self.checkpoint_manager.save('lunar_converted', df, {
            'total_days': len(df),
            'date_range': f"{df['gregorian_year'].min()}-{df['gregorian_year'].max()}"
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
        Хураангуй мэдээлэл үүсгэх

        Args:
            df: Мэдээлэл агуулсан DataFrame
        """
        print("\n" + "="*60)
        print("📊 ХУРААНГУЙ МЭДЭЭЛЭЛ")
        print("="*60)

        print(f"\n📅 Огтлолцоо:")
        print(f"   Сарны календар: {df['lunar_year'].min()}-{df['lunar_year'].max()}")
        print(f"   Григорийн календар: {df['gregorian_year'].min()}-{df['gregorian_year'].max()}")

        print(f"\n📈 Өдрийн статистик:")
        print(f"   Нийт өдөр: {len(df)}")
        print(f"   Муу өдөр (modon + ters): {df['is_bad_day'].sum()}")
        print(f"   Сайн өдөр (baljin + dash): {df['is_good_day'].sum()}")
        print(f"   Үс засах өдөр: {df['is_haircut_day'].sum()}")

        print(f"\n🗓️ Өдрийн төрлөөр:")
        type_counts = df['day_type'].value_counts()
        for day_type, count in type_counts.items():
            print(f"   {day_type}: {count}")

        print(f"\n📂 Хадгалсан файл:")
        print(f"   {self.output_file}")
        print(f"   Хэмжээ: {self.output_file.stat().st_size / 1024:.2f} KB")

        print("\n" + "="*60)


def main():
    """
    Main функц - script ажиллуулах
    """
    print("="*60)
    print("🌙 МОНГОЛЫН САРНЫ КАЛЕНДАР → ГРИГОРИЙН ОГНОО")
    print("="*60)

    try:
        # Processor үүсгэх
        processor = LunarCalendarProcessor()

        # Боловсруулах
        df = processor.process_all()

        # CSV хадгалах
        processor.save_to_csv(df)

        # Хураангуй харуулах
        processor.generate_summary(df)

        print("\n✅ Амжилттай дууслаа!")
        return df

    except FileNotFoundError as e:
        print(f"\n{e}")
        print("\n💡 Зааварчилгаа:")
        print("   1. horoscope_list_20250112.json файлаа бэлдэнэ үү")
        print("   2. Файлыг data/raw/ хавтаст хуулна уу")
        print("   3. Script-ийг дахин ажиллуулна уу")
        return None

    except Exception as e:
        print(f"\n❌ Алдаа гарлаа: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    df = main()
