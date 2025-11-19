"""
Progress Tracker - Явцыг харуулах, хянах

Энэ модуль нь tqdm ашиглан явцыг харуулж, мөн файлд явцыг бичиж хадгална.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from tqdm import tqdm
from datetime import datetime


class ProgressTracker:
    """
    Явц хянагч класс

    tqdm-ийн wrapper бөгөөд явцыг файлд хадгалах нэмэлт функцтэй.

    Examples:
        >>> tracker = ProgressTracker(total=100, desc="Processing")
        >>> for i in range(100):
        ...     tracker.update(1, extra_info={'item': i})
    """

    def __init__(
        self,
        total: Optional[int] = None,
        desc: str = "Progress",
        save_file: Optional[str] = None,
        unit: str = "it"
    ):
        """
        ProgressTracker эхлүүлэх

        Args:
            total: Нийт тоо хэмжээ
            desc: Тайлбар текст
            save_file: Явцыг хадгалах файл (JSON)
            unit: Нэгжийн нэр
        """
        self.total = total
        self.desc = desc
        self.unit = unit
        self.save_file = Path(save_file) if save_file else None

        # tqdm progress bar үүсгэх
        self.pbar = tqdm(total=total, desc=desc, unit=unit)

        # Progress мэдээлэл
        self.progress_data = {
            'total': total,
            'current': 0,
            'desc': desc,
            'start_time': datetime.now().isoformat(),
            'last_update': None,
            'extra_info': {}
        }

        # Хэрэв өмнөх явц байвал унших
        if self.save_file and self.save_file.exists():
            self._load_progress()

    def _load_progress(self) -> None:
        """Өмнөх явцыг файлаас унших"""
        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                self.progress_data.update(saved_data)

                # Progress bar-ыг өмнөх байдалд оруулах
                if self.progress_data['current'] > 0:
                    self.pbar.update(self.progress_data['current'])

            print(f"✓ Өмнөх явц уншигдлаа: {self.progress_data['current']}/{self.total}")
        except Exception as e:
            print(f"⚠ Явц унших үед алдаа: {e}")

    def _save_progress(self) -> None:
        """Явцыг файлд хадгалах"""
        if not self.save_file:
            return

        try:
            # Хавтас үүсгэх
            self.save_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠ Явц хадгалах үед алдаа: {e}")

    def update(self, n: int = 1, extra_info: Optional[Dict[str, Any]] = None) -> None:
        """
        Явцыг шинэчлэх

        Args:
            n: Нэмэх утга
            extra_info: Нэмэлт мэдээлэл

        Examples:
            >>> tracker.update(1, {'processed': 'file.txt'})
        """
        self.pbar.update(n)
        self.progress_data['current'] += n
        self.progress_data['last_update'] = datetime.now().isoformat()

        if extra_info:
            self.progress_data['extra_info'].update(extra_info)

        # Файлд хадгалах (өөрчлөлт бүрд биш, 10 дахь бүр)
        if self.progress_data['current'] % 10 == 0:
            self._save_progress()

    def set_postfix(self, **kwargs) -> None:
        """
        Нэмэлт мэдээлэл харуулах

        Args:
            **kwargs: Key-value pairs

        Examples:
            >>> tracker.set_postfix(year=2000, events=150)
        """
        self.pbar.set_postfix(**kwargs)
        self.progress_data['extra_info'].update(kwargs)

    def write(self, message: str) -> None:
        """
        Progress bar-г саадлахгүйгээр текст хэвлэх

        Args:
            message: Хэвлэх текст
        """
        tqdm.write(message)

    def close(self) -> None:
        """Progress bar хаах ба явцыг хадгалах"""
        self._save_progress()
        self.pbar.close()

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - гарахдаа хаах"""
        self.close()


def create_progress_bar(
    iterable,
    desc: str = "Processing",
    save_file: Optional[str] = None,
    **kwargs
) -> tqdm:
    """
    Энгийн progress bar үүсгэх (tqdm wrapper)

    Args:
        iterable: Iterate хийх объект
        desc: Тайлбар
        save_file: Явцыг хадгалах файл (одоогоор ашиглагдахгүй)
        **kwargs: tqdm-д дамжуулах бусад параметрүүд

    Returns:
        tqdm объект

    Examples:
        >>> for item in create_progress_bar(items, desc="Processing items"):
        ...     process(item)
    """
    return tqdm(iterable, desc=desc, **kwargs)
