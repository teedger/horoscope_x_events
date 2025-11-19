"""
2. World Events Scraper - Дэлхийн гамшигт үйл явдлуудыг цуглуулах

Энэ script нь 1942-2005 оны хооронд болсон дэлхийн томоохон
гамшигт үйл явдлуудыг цуглуулна.

Эх сурвалжууд:
- Wikipedia болон бусад нээлттэй эх сурвалжууд
- Гар аргаар бэлдсэн dataset (major events)
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys

# Utility модулиудыг import хийх
sys.path.append(str(Path(__file__).parent))
from utils.checkpoint_manager import CheckpointManager
from utils.progress_tracker import create_progress_bar


class DisasterEventCollector:
    """
    Гамшигт үйл явдлын цуглуулагч

    Дэлхийн томоохон гамшигт үйл явдлуудын өгөгдлийг цуглуулна.
    """

    def __init__(
        self,
        output_file: str = 'data/processed/world_disasters.csv',
        checkpoint_name: str = 'events_scraped'
    ):
        """
        Collector эхлүүлэх

        Args:
            output_file: Output CSV файлын зам
            checkpoint_name: Checkpoint нэр
        """
        self.output_file = Path(output_file)
        self.checkpoint_name = checkpoint_name
        self.checkpoint_manager = CheckpointManager()

        # Output folder үүсгэх
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def get_predefined_events(self) -> List[Dict[str, Any]]:
        """
        Урьдчилан бэлдсэн томоохон үйл явдлуудын жагсаалт

        Энэ нь 1942-2005 оны хоорондох томоохон гамшигт үйл явдлууд.
        Бодит scraping-ийн оронд эхлээд энэ dataset ашиглана.

        Returns:
            Үйл явдлуудын жагсаалт
        """
        events = [
            # ===========================================
            # 1940s - World War II ба дараах үе
            # ===========================================
            {
                'name': 'World War II - European Theater End',
                'date': '1945-05-08',
                'end_date': '1945-05-08',
                'category': 'war',
                'description': 'End of World War II in Europe (V-E Day)',
                'deaths': 40000000,  # Total WWII deaths (approximate)
                'affected_population': 100000000,
                'countries': ['Global'],
                'severity_score': None  # Will be calculated
            },
            {
                'name': 'Atomic Bombing of Hiroshima',
                'date': '1945-08-06',
                'end_date': '1945-08-06',
                'category': 'military_attack',
                'description': 'First atomic bomb dropped on Hiroshima, Japan',
                'deaths': 140000,
                'affected_population': 350000,
                'countries': ['Japan'],
                'severity_score': None
            },
            {
                'name': 'Atomic Bombing of Nagasaki',
                'date': '1945-08-09',
                'end_date': '1945-08-09',
                'category': 'military_attack',
                'description': 'Second atomic bomb dropped on Nagasaki, Japan',
                'deaths': 74000,
                'affected_population': 270000,
                'countries': ['Japan'],
                'severity_score': None
            },

            # ===========================================
            # 1950s - Korean War, Natural Disasters
            # ===========================================
            {
                'name': 'Korean War',
                'date': '1950-06-25',
                'end_date': '1953-07-27',
                'category': 'war',
                'description': 'War between North and South Korea',
                'deaths': 2500000,
                'affected_population': 10000000,
                'countries': ['North Korea', 'South Korea', 'USA', 'China'],
                'severity_score': None
            },
            {
                'name': 'Great Smog of London',
                'date': '1952-12-05',
                'end_date': '1952-12-09',
                'category': 'environmental_disaster',
                'description': 'Severe air pollution event in London',
                'deaths': 12000,
                'affected_population': 100000,
                'countries': ['UK'],
                'severity_score': None
            },
            {
                'name': '1953 North Sea Flood',
                'date': '1953-01-31',
                'end_date': '1953-02-01',
                'category': 'natural_disaster',
                'description': 'Major flood affecting Netherlands, UK, and Belgium',
                'deaths': 2551,
                'affected_population': 100000,
                'countries': ['Netherlands', 'UK', 'Belgium'],
                'severity_score': None
            },

            # ===========================================
            # 1960s - Vietnam War, Earthquakes
            # ===========================================
            {
                'name': 'Vietnam War Escalation',
                'date': '1964-08-02',
                'end_date': '1975-04-30',
                'category': 'war',
                'description': 'Vietnam War (Gulf of Tonkin to Fall of Saigon)',
                'deaths': 3000000,
                'affected_population': 20000000,
                'countries': ['Vietnam', 'USA', 'Cambodia', 'Laos'],
                'severity_score': None
            },
            {
                'name': 'Great Chilean Earthquake',
                'date': '1960-05-22',
                'end_date': '1960-05-22',
                'category': 'natural_disaster',
                'description': 'Most powerful earthquake ever recorded (9.5 magnitude)',
                'deaths': 5700,
                'affected_population': 2000000,
                'countries': ['Chile'],
                'severity_score': None
            },
            {
                'name': 'Cuban Missile Crisis',
                'date': '1962-10-16',
                'end_date': '1962-10-28',
                'category': 'political_crisis',
                'description': 'Closest Cold War came to nuclear war',
                'deaths': 0,
                'affected_population': 3000000000,  # Global population at risk
                'countries': ['USA', 'USSR', 'Cuba'],
                'severity_score': None
            },
            {
                'name': 'Assassination of John F. Kennedy',
                'date': '1963-11-22',
                'end_date': '1963-11-22',
                'category': 'assassination',
                'description': 'Assassination of US President Kennedy',
                'deaths': 1,
                'affected_population': 190000000,
                'countries': ['USA'],
                'severity_score': None
            },
            {
                'name': 'Assassination of Martin Luther King Jr.',
                'date': '1968-04-04',
                'end_date': '1968-04-04',
                'category': 'assassination',
                'description': 'Assassination of civil rights leader MLK',
                'deaths': 1,
                'affected_population': 200000000,
                'countries': ['USA'],
                'severity_score': None
            },

            # ===========================================
            # 1970s - Disasters, Oil Crisis
            # ===========================================
            {
                'name': 'Bhola Cyclone',
                'date': '1970-11-12',
                'end_date': '1970-11-13',
                'category': 'natural_disaster',
                'description': 'Deadliest tropical cyclone on record',
                'deaths': 500000,
                'affected_population': 3500000,
                'countries': ['Bangladesh', 'India'],
                'severity_score': None
            },
            {
                'name': '1973 Oil Crisis',
                'date': '1973-10-17',
                'end_date': '1974-03-17',
                'category': 'economic_crisis',
                'description': 'Oil embargo causing global economic crisis',
                'deaths': 0,
                'affected_population': 1000000000,
                'countries': ['Global'],
                'severity_score': None
            },
            {
                'name': 'Tangshan Earthquake',
                'date': '1976-07-28',
                'end_date': '1976-07-28',
                'category': 'natural_disaster',
                'description': 'Deadliest earthquake of 20th century',
                'deaths': 242000,
                'affected_population': 1600000,
                'countries': ['China'],
                'severity_score': None
            },

            # ===========================================
            # 1980s - Cold War events, Disasters
            # ===========================================
            {
                'name': 'Iran-Iraq War',
                'date': '1980-09-22',
                'end_date': '1988-08-20',
                'category': 'war',
                'description': 'War between Iran and Iraq',
                'deaths': 1000000,
                'affected_population': 5000000,
                'countries': ['Iran', 'Iraq'],
                'severity_score': None
            },
            {
                'name': 'Assassination of Indira Gandhi',
                'date': '1984-10-31',
                'end_date': '1984-10-31',
                'category': 'assassination',
                'description': 'Assassination of Indian Prime Minister',
                'deaths': 1,
                'affected_population': 750000000,
                'countries': ['India'],
                'severity_score': None
            },
            {
                'name': 'Bhopal Gas Disaster',
                'date': '1984-12-02',
                'end_date': '1984-12-03',
                'category': 'industrial_disaster',
                'description': 'Worst industrial disaster in history',
                'deaths': 15000,
                'affected_population': 600000,
                'countries': ['India'],
                'severity_score': None
            },
            {
                'name': 'Chernobyl Nuclear Disaster',
                'date': '1986-04-26',
                'end_date': '1986-04-26',
                'category': 'industrial_disaster',
                'description': 'Worst nuclear disaster in history',
                'deaths': 4000,  # Direct and indirect deaths
                'affected_population': 5000000,
                'countries': ['USSR', 'Ukraine', 'Belarus'],
                'severity_score': None
            },
            {
                'name': 'Armenian Earthquake',
                'date': '1988-12-07',
                'end_date': '1988-12-07',
                'category': 'natural_disaster',
                'description': 'Devastating earthquake in Armenia',
                'deaths': 25000,
                'affected_population': 1000000,
                'countries': ['Armenia', 'USSR'],
                'severity_score': None
            },
            {
                'name': 'Tiananmen Square Massacre',
                'date': '1989-06-04',
                'end_date': '1989-06-04',
                'category': 'political_violence',
                'description': 'Military crackdown on pro-democracy protests',
                'deaths': 3000,  # Estimates vary widely
                'affected_population': 1000000,
                'countries': ['China'],
                'severity_score': None
            },

            # ===========================================
            # 1990s - Gulf War, Genocides, Conflicts
            # ===========================================
            {
                'name': 'Gulf War',
                'date': '1991-01-17',
                'end_date': '1991-02-28',
                'category': 'war',
                'description': 'War to liberate Kuwait from Iraq',
                'deaths': 25000,
                'affected_population': 2000000,
                'countries': ['Iraq', 'Kuwait', 'USA', 'Coalition'],
                'severity_score': None
            },
            {
                'name': 'Rwandan Genocide',
                'date': '1994-04-07',
                'end_date': '1994-07-15',
                'category': 'genocide',
                'description': 'Genocide of Tutsi people in Rwanda',
                'deaths': 800000,
                'affected_population': 2000000,
                'countries': ['Rwanda'],
                'severity_score': None
            },
            {
                'name': 'Kobe Earthquake',
                'date': '1995-01-17',
                'end_date': '1995-01-17',
                'category': 'natural_disaster',
                'description': 'Great Hanshin earthquake in Japan',
                'deaths': 6434,
                'affected_population': 1500000,
                'countries': ['Japan'],
                'severity_score': None
            },
            {
                'name': 'Oklahoma City Bombing',
                'date': '1995-04-19',
                'end_date': '1995-04-19',
                'category': 'terrorist_attack',
                'description': 'Domestic terrorist attack in USA',
                'deaths': 168,
                'affected_population': 500000,
                'countries': ['USA'],
                'severity_score': None
            },

            # ===========================================
            # 2000-2005 - 9/11, Wars, Natural Disasters
            # ===========================================
            {
                'name': 'September 11 Attacks',
                'date': '2001-09-11',
                'end_date': '2001-09-11',
                'category': 'terrorist_attack',
                'description': 'Terrorist attacks on World Trade Center and Pentagon',
                'deaths': 2977,
                'affected_population': 300000000,
                'countries': ['USA'],
                'severity_score': None
            },
            {
                'name': 'Afghanistan War',
                'date': '2001-10-07',
                'end_date': '2005-12-31',  # Ongoing but we cap at 2005
                'category': 'war',
                'description': 'War in Afghanistan following 9/11',
                'deaths': 50000,  # Up to 2005
                'affected_population': 25000000,
                'countries': ['Afghanistan', 'USA', 'NATO'],
                'severity_score': None
            },
            {
                'name': 'Iraq War',
                'date': '2003-03-20',
                'end_date': '2005-12-31',  # Ongoing but we cap at 2005
                'category': 'war',
                'description': 'Invasion of Iraq and subsequent conflict',
                'deaths': 150000,  # Up to 2005
                'affected_population': 26000000,
                'countries': ['Iraq', 'USA', 'Coalition'],
                'severity_score': None
            },
            {
                'name': 'Bam Earthquake',
                'date': '2003-12-26',
                'end_date': '2003-12-26',
                'category': 'natural_disaster',
                'description': 'Earthquake in Bam, Iran',
                'deaths': 26271,
                'affected_population': 200000,
                'countries': ['Iran'],
                'severity_score': None
            },
            {
                'name': 'Indian Ocean Tsunami',
                'date': '2004-12-26',
                'end_date': '2004-12-26',
                'category': 'natural_disaster',
                'description': 'One of deadliest natural disasters in history',
                'deaths': 230000,
                'affected_population': 5000000,
                'countries': ['Indonesia', 'Sri Lanka', 'India', 'Thailand', '14 countries'],
                'severity_score': None
            },
            {
                'name': 'Hurricane Katrina',
                'date': '2005-08-29',
                'end_date': '2005-08-30',
                'category': 'natural_disaster',
                'description': 'Devastating hurricane in USA',
                'deaths': 1833,
                'affected_population': 1000000,
                'countries': ['USA'],
                'severity_score': None
            },
            {
                'name': 'Kashmir Earthquake',
                'date': '2005-10-08',
                'end_date': '2005-10-08',
                'category': 'natural_disaster',
                'description': 'Earthquake in Pakistan and India',
                'deaths': 86000,
                'affected_population': 3000000,
                'countries': ['Pakistan', 'India'],
                'severity_score': None
            },
        ]

        return events

    def calculate_severity_score(self, event: Dict[str, Any]) -> int:
        """
        Үйл явдлын хүндрэлийн оноог тооцоолох

        Scoring system:
        - Deaths: 0-40 оноо
        - Affected population: 0-30 оноо
        - Geopolitical impact: 0-30 оноо (category-д тулгуурлан)

        Args:
            event: Үйл явдлын мэдээлэл

        Returns:
            Severity score (0-100)
        """
        score = 0
        deaths = event.get('deaths', 0)
        affected = event.get('affected_population', 0)
        category = event.get('category', 'other')

        # 1. Deaths scoring (0-40 оноо)
        if deaths >= 1000000:
            score += 40
        elif deaths >= 100000:
            score += 35
        elif deaths >= 10000:
            score += 25
        elif deaths >= 1000:
            score += 15
        elif deaths >= 100:
            score += 8
        elif deaths >= 10:
            score += 4
        elif deaths >= 1:
            score += 2

        # 2. Affected population (0-30 оноо)
        if affected >= 100000000:
            score += 30
        elif affected >= 10000000:
            score += 25
        elif affected >= 1000000:
            score += 20
        elif affected >= 100000:
            score += 15
        elif affected >= 10000:
            score += 10
        elif affected >= 1000:
            score += 5

        # 3. Geopolitical impact by category (0-30 оноо)
        category_scores = {
            'war': 30,
            'genocide': 30,
            'terrorist_attack': 25,
            'assassination': 20,
            'political_crisis': 25,
            'natural_disaster': 15,
            'industrial_disaster': 20,
            'economic_crisis': 20,
            'environmental_disaster': 15,
            'political_violence': 20,
            'military_attack': 25,
            'other': 10
        }

        score += category_scores.get(category, 10)

        return min(score, 100)  # Cap at 100

    def process_events(self) -> pd.DataFrame:
        """
        Бүх үйл явдлуудыг боловсруулж, severity score тооцоолох

        Returns:
            Боловсруулсан үйл явдлуудын DataFrame
        """
        # Checkpoint шалгах
        if self.checkpoint_manager.exists(self.checkpoint_name):
            print("📂 Checkpoint олдсон! Өмнө нь цуглуулсан өгөгдлийг ашиглана.")
            df = self.checkpoint_manager.load(self.checkpoint_name)
            return df

        print("📖 Үйл явдлуудыг цуглуулж байна...")

        # Predefined events авах
        events = self.get_predefined_events()

        print(f"\n🔄 Severity score тооцоолж байна...")

        # Severity score тооцоолох
        for event in create_progress_bar(events, desc="Боловсруулж байна"):
            event['severity_score'] = self.calculate_severity_score(event)

        # DataFrame үүсгэх
        df = pd.DataFrame(events)

        # Date parsing
        df['date'] = pd.to_datetime(df['date'])
        df['end_date'] = pd.to_datetime(df['end_date'])

        # Extract year, month, day
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day

        # Duration in days
        df['duration_days'] = (df['end_date'] - df['date']).dt.days + 1

        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)

        print(f"\n✓ Нийт {len(df)} үйл явдал боловсруулагдлаа")
        print(f"  - Огтлолцоо: {df['year'].min()}-{df['year'].max()}")
        print(f"  - Дундаж severity: {df['severity_score'].mean():.1f}")

        # Checkpoint хадгалах
        self.checkpoint_manager.save(self.checkpoint_name, df, {
            'total_events': len(df),
            'date_range': f"{df['year'].min()}-{df['year'].max()}"
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
        print("📊 ДЭЛХИЙН ГАМШИГТ ҮЙЛЯВДЛЫН ХУРААНГУЙ")
        print("="*60)

        print(f"\n📅 Огтлолцоо: {df['year'].min()}-{df['year'].max()}")
        print(f"📈 Нийт үйл явдал: {len(df)}")

        print(f"\n💀 Нийт нас барагсад: {df['deaths'].sum():,}")
        print(f"👥 Нийт өртсөн хүн ам: {df['affected_population'].sum():,}")

        print(f"\n🎯 Severity оноо:")
        print(f"   Дундаж: {df['severity_score'].mean():.1f}")
        print(f"   Медиан: {df['severity_score'].median():.1f}")
        print(f"   Min-Max: {df['severity_score'].min():.0f} - {df['severity_score'].max():.0f}")

        print(f"\n📂 Категориор:")
        category_counts = df['category'].value_counts()
        for cat, count in category_counts.items():
            avg_severity = df[df['category'] == cat]['severity_score'].mean()
            print(f"   {cat}: {count} ({avg_severity:.1f} avg severity)")

        print(f"\n🏆 Хамгийн их severity бүхий үйл явдлууд:")
        top_events = df.nlargest(5, 'severity_score')[['name', 'date', 'severity_score', 'deaths']]
        for idx, row in top_events.iterrows():
            print(f"   {row['severity_score']:.0f} - {row['name']} ({row['date'].strftime('%Y-%m-%d')})")

        print(f"\n📂 Хадгалсан файл:")
        print(f"   {self.output_file}")

        print("\n" + "="*60)


def main():
    """
    Main функц - script ажиллуулах
    """
    print("="*60)
    print("🌍 ДЭЛХИЙН ГАМШИГТ ҮЙЛЯВДЛЫН ЦУГЛУУЛГА")
    print("="*60)

    try:
        # Collector үүсгэх
        collector = DisasterEventCollector()

        # Үйл явдлуудыг боловсруулах
        df = collector.process_events()

        # CSV хадгалах
        collector.save_to_csv(df)

        # Хураангуй харуулах
        collector.generate_summary(df)

        print("\n✅ Амжилттай дууслаа!")
        return df

    except Exception as e:
        print(f"\n❌ Алдаа гарлаа: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    df = main()
