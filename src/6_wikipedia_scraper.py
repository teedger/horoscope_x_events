"""
Wikipedia Event Scraper - Wikipedia-с үйл явдал цуглуулах

Энэ модуль нь Wikipedia-с нэмэлт түүхэн үйл явдлуудыг
автоматаар цуглуулна.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import json
import sys

sys.path.append(str(Path(__file__).parent))
from utils.checkpoint_manager import CheckpointManager
from utils.progress_tracker import create_progress_bar


class WikipediaEventScraper:
    """
    Wikipedia-с үйл явдал цуглуулах

    Дараах хуудсуудаас үйл явдал цуглуулна:
    - List of wars
    - List of natural disasters
    - List of terrorist incidents
    - List of assassinations
    """

    def __init__(self, checkpoint_name: str = 'wiki_events'):
        """
        Scraper эхлүүлэх

        Args:
            checkpoint_name: Checkpoint нэр
        """
        self.checkpoint_manager = CheckpointManager()
        self.checkpoint_name = checkpoint_name
        self.base_url = "https://en.wikipedia.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Research Bot for Academic Project)'
        })

        # Rate limiting
        self.request_delay = 1.0  # seconds between requests

    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """
        URL-д хүсэлт илгээх (rate limiting-тэй)

        Args:
            url: URL хаяг

        Returns:
            BeautifulSoup объект эсвэл None
        """
        try:
            time.sleep(self.request_delay)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"⚠ Request error ({url}): {e}")
            return None

    def scrape_disasters_by_year(self, start_year: int = 1942, end_year: int = 2005) -> List[Dict]:
        """
        Жил тус бүрийн гамшгийн мэдээлэл цуглуулах

        Args:
            start_year: Эхлэх он
            end_year: Дуусах он

        Returns:
            Үйл явдлуудын жагсаалт
        """
        events = []

        print(f"📥 Wikipedia-с {start_year}-{end_year} оны үйл явдал цуглуулж байна...")

        for year in create_progress_bar(range(start_year, end_year + 1), desc="Scraping"):
            year_events = self._scrape_year_page(year)
            events.extend(year_events)

            # Checkpoint хадгалах (10 жил тутамд)
            if year % 10 == 0:
                self.checkpoint_manager.save(
                    f'{self.checkpoint_name}_partial',
                    events,
                    {'last_year': year, 'count': len(events)}
                )

        return events

    def _scrape_year_page(self, year: int) -> List[Dict]:
        """
        Нэг жилийн хуудас цуглуулах

        Args:
            year: Он

        Returns:
            Тухайн жилийн үйл явдлууд
        """
        url = f"{self.base_url}/wiki/{year}"
        soup = self._make_request(url)

        if not soup:
            return []

        events = []

        # "Events" section олох
        events_section = None
        for heading in soup.find_all(['h2', 'h3']):
            if 'Events' in heading.get_text() or 'Disasters' in heading.get_text():
                events_section = heading
                break

        if not events_section:
            return []

        # Дараагийн section хүртэл бүх list items авах
        current = events_section.find_next_sibling()
        while current and current.name not in ['h2']:
            if current.name == 'ul':
                for li in current.find_all('li', recursive=False):
                    event = self._parse_event_item(li, year)
                    if event:
                        events.append(event)
            current = current.find_next_sibling() if current else None

        return events

    def _parse_event_item(self, li_element, year: int) -> Optional[Dict]:
        """
        List item-аас үйл явдлын мэдээлэл задлах

        Args:
            li_element: BeautifulSoup li element
            year: Он

        Returns:
            Үйл явдлын dict эсвэл None
        """
        text = li_element.get_text(strip=True)

        # Огноо олох pattern
        date_patterns = [
            r'(\w+ \d{1,2})',  # "January 15"
            r'(\d{1,2} \w+)',  # "15 January"
        ]

        date_str = None
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                break

        if not date_str:
            return None

        # Огноог parse хийх
        try:
            # Try different formats
            for fmt in ['%B %d', '%d %B']:
                try:
                    parsed = datetime.strptime(f"{date_str} {year}", f"{fmt} %Y")
                    break
                except:
                    continue
            else:
                return None
        except:
            return None

        # Category таамаглах
        category = self._guess_category(text)

        # Гамшиг эсэхийг шалгах
        disaster_keywords = [
            'earthquake', 'flood', 'hurricane', 'typhoon', 'cyclone',
            'tsunami', 'volcano', 'eruption', 'fire', 'explosion',
            'crash', 'accident', 'disaster', 'attack', 'bombing',
            'war', 'battle', 'assassination', 'death', 'killed',
            'massacre', 'genocide', 'crisis', 'collapse'
        ]

        is_disaster = any(kw in text.lower() for kw in disaster_keywords)

        if not is_disaster:
            return None

        return {
            'name': text[:200],  # First 200 chars
            'date': parsed.strftime('%Y-%m-%d'),
            'year': year,
            'month': parsed.month,
            'day': parsed.day,
            'category': category,
            'source': 'wikipedia',
            'raw_text': text
        }

    def _guess_category(self, text: str) -> str:
        """
        Текстээс категори таамаглах

        Args:
            text: Үйл явдлын текст

        Returns:
            Категори нэр
        """
        text_lower = text.lower()

        category_keywords = {
            'natural_disaster': ['earthquake', 'flood', 'hurricane', 'typhoon', 'cyclone',
                                'tsunami', 'volcano', 'eruption', 'tornado', 'avalanche'],
            'terrorist_attack': ['terrorist', 'bombing', 'attack', 'hijack'],
            'war': ['war', 'battle', 'invasion', 'military', 'army'],
            'assassination': ['assassination', 'assassinated', 'murdered'],
            'industrial_disaster': ['explosion', 'fire', 'collapse', 'accident', 'crash'],
            'political_crisis': ['coup', 'revolution', 'uprising', 'protest'],
        }

        for category, keywords in category_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return category

        return 'other'

    def scrape_specific_lists(self) -> List[Dict]:
        """
        Тодорхой Wikipedia жагсаалтуудаас цуглуулах

        Returns:
            Үйл явдлуудын жагсаалт
        """
        events = []

        lists_to_scrape = [
            '/wiki/List_of_natural_disasters_by_death_toll',
            '/wiki/List_of_wars_by_death_toll',
            '/wiki/List_of_assassinated_American_politicians',
        ]

        for list_url in lists_to_scrape:
            print(f"📥 Scraping: {list_url}")
            url = self.base_url + list_url
            soup = self._make_request(url)

            if soup:
                # Table-уудаас өгөгдөл авах
                for table in soup.find_all('table', {'class': 'wikitable'}):
                    table_events = self._parse_wikitable(table)
                    events.extend(table_events)

        return events

    def _parse_wikitable(self, table) -> List[Dict]:
        """
        Wikipedia table-аас өгөгдөл задлах

        Args:
            table: BeautifulSoup table element

        Returns:
            Үйл явдлуудын жагсаалт
        """
        events = []

        # Header row олох
        headers = []
        header_row = table.find('tr')
        if header_row:
            headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]

        # Data rows
        for row in table.find_all('tr')[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue

            row_data = [cell.get_text(strip=True) for cell in cells]

            # Try to extract event info
            event = {
                'name': row_data[0] if len(row_data) > 0 else '',
                'source': 'wikipedia_table',
                'raw_data': row_data
            }

            # Date олох
            for i, header in enumerate(headers):
                if 'date' in header or 'year' in header:
                    if i < len(row_data):
                        event['date_str'] = row_data[i]
                        break

            if event['name']:
                events.append(event)

        return events


def main():
    """Wikipedia scraper тест"""
    print("="*60)
    print("🌐 WIKIPEDIA EVENT SCRAPER")
    print("="*60)

    scraper = WikipediaEventScraper()

    # Жилийн хуудсуудаас цуглуулах
    events = scraper.scrape_disasters_by_year(1990, 2000)  # Test with small range

    print(f"\n✅ Нийт {len(events)} үйл явдал олдлоо!")

    # Sample events харуулах
    if events:
        print("\n📋 Жишээ үйл явдлууд:")
        for event in events[:5]:
            print(f"  - {event['date']}: {event['name'][:80]}...")

    return events


if __name__ == "__main__":
    events = main()
