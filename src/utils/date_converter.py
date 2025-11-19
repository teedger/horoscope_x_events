"""
Lunar Date Converter - Сарны огноог Григорийн огноо руу хөрвүүлэх

Монголын сарны календарь Хятадын сарны календартай ижил боловч
timezone өөр тул анхаарах хэрэгтэй.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import lunarcalendar
from lunarcalendar import Converter, Solar, Lunar
import pytz


class LunarDateConverter:
    """
    Сарны огноо хөрвүүлэгч

    Монголын сарны календарийн огноог Григорийн огноо руу хөрвүүлнэ.

    Examples:
        >>> converter = LunarDateConverter()
        >>> gregorian = converter.lunar_to_gregorian(2000, 1, 15)
        >>> print(gregorian)  # datetime object
    """

    def __init__(self, timezone: str = 'Asia/Ulaanbaatar'):
        """
        Converter эхлүүлэх

        Args:
            timezone: Цагийн бүс (Mongolia: Asia/Ulaanbaatar, UTC+8)
        """
        self.timezone = pytz.timezone(timezone)

    def lunar_to_gregorian(
        self,
        lunar_year: int,
        lunar_month: int,
        lunar_day: int,
        is_leap_month: bool = False
    ) -> Optional[datetime]:
        """
        Сарны огноог Григорийн огноо руу хөрвүүлэх

        Args:
            lunar_year: Сарны он (жишээ: 2000)
            lunar_month: Сарны сар (1-12)
            lunar_day: Сарны өдөр (1-30)
            is_leap_month: Өндөр сар эсэх (leap month)

        Returns:
            datetime объект эсвэл None (алдаа гарсан бол)

        Examples:
            >>> converter = LunarDateConverter()
            >>> date = converter.lunar_to_gregorian(2000, 1, 15)
            >>> print(date.strftime('%Y-%m-%d'))
        """
        try:
            # lunarcalendar library ашиглан хөрвүүлэх
            lunar = Lunar(lunar_year, lunar_month, lunar_day, isleap=is_leap_month)
            solar = Converter.Lunar2Solar(lunar)

            # datetime объект үүсгэх
            gregorian_date = datetime(
                solar.year,
                solar.month,
                solar.day,
                tzinfo=self.timezone
            )

            return gregorian_date

        except Exception as e:
            print(f"⚠ Огноо хөрвүүлэх үед алдаа ({lunar_year}-{lunar_month}-{lunar_day}): {e}")
            return None

    def gregorian_to_lunar(
        self,
        gregorian_date: datetime
    ) -> Optional[Tuple[int, int, int, bool]]:
        """
        Григорийн огноог сарны огноо руу хөрвүүлэх

        Args:
            gregorian_date: Григорийн огноо

        Returns:
            Tuple (year, month, day, is_leap_month) эсвэл None

        Examples:
            >>> date = datetime(2000, 2, 15)
            >>> lunar = converter.gregorian_to_lunar(date)
            >>> print(lunar)  # (2000, 1, 10, False)
        """
        try:
            solar = Solar(
                gregorian_date.year,
                gregorian_date.month,
                gregorian_date.day
            )
            lunar = Converter.Solar2Lunar(solar)

            return (lunar.year, lunar.month, lunar.day, lunar.isleap)

        except Exception as e:
            print(f"⚠ Огноо хөрвүүлэх үед алдаа ({gregorian_date}): {e}")
            return None

    def is_valid_lunar_date(
        self,
        lunar_year: int,
        lunar_month: int,
        lunar_day: int
    ) -> bool:
        """
        Сарны огноо зөв эсэхийг шалгах

        Args:
            lunar_year: Сарны он
            lunar_month: Сарны сар
            lunar_day: Сарны өдөр

        Returns:
            True хэрэв зөв бол
        """
        try:
            result = self.lunar_to_gregorian(lunar_year, lunar_month, lunar_day)
            return result is not None
        except:
            return False

    def get_lunar_month_length(
        self,
        lunar_year: int,
        lunar_month: int
    ) -> int:
        """
        Сарны сарын хэдэн өдөртэй болохыг тогтоох

        Args:
            lunar_year: Сарны он
            lunar_month: Сарны сар

        Returns:
            Өдрийн тоо (29 эсвэл 30)
        """
        # 30-р өдөр байгаа эсэхийг шалгах
        if self.is_valid_lunar_date(lunar_year, lunar_month, 30):
            return 30
        else:
            return 29


# Convenience functions
def convert_lunar_to_gregorian(
    year: int,
    month: int,
    day: int,
    timezone: str = 'Asia/Ulaanbaatar'
) -> Optional[datetime]:
    """
    Хурдан хөрвүүлэлт - функц хэлбэрээр

    Args:
        year: Сарны он
        month: Сарны сар
        day: Сарны өдөр
        timezone: Цагийн бүс

    Returns:
        datetime объект

    Examples:
        >>> date = convert_lunar_to_gregorian(2000, 1, 15)
    """
    converter = LunarDateConverter(timezone)
    return converter.lunar_to_gregorian(year, month, day)


def convert_gregorian_to_lunar(
    date: datetime,
    timezone: str = 'Asia/Ulaanbaatar'
) -> Optional[Tuple[int, int, int, bool]]:
    """
    Хурдан хөрвүүлэлт - Григорийн → Сарны

    Args:
        date: Григорийн огноо
        timezone: Цагийн бүс

    Returns:
        Tuple (year, month, day, is_leap_month)
    """
    converter = LunarDateConverter(timezone)
    return converter.gregorian_to_lunar(date)
