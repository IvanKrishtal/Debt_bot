import re
from datetime import datetime
from .base import BaseParser
from config import ADMIN_NAME

MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


class SberParser(BaseParser):
    def _find_debt(self, text: str) -> float:
        match = re.search(r"Сумма перевода\s*([\d\s,]+)\s*₽", text)
        if match:
            return float(match.group(1).replace(" ", "").replace(",", "."))
        return None

    def _find_receipt_time(self, text: str):
        match = re.search(
            r"(\d{1,2})\s+(\w+)\s+(\d{4})\s+(\d{2}):(\d{2}):(\d{2})", text
        )
        if match:
            day, month_name, year, hour, minute, second = match.groups()
            month = MONTHS.get(month_name.lower())
            if month:
                return datetime(
                    int(year), month, int(day), int(hour), int(minute), int(second)
                )
        return None

    def _check_name(self, text: str) -> bool:
        match = re.search(
            r"ФИО получателя\s*([А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.?)", text
        )
        if match:
            name_from_cheque = match.group(1).strip().replace(".", "").lower()
            admin_name = ADMIN_NAME.strip().replace(".", "").lower()
            return name_from_cheque == admin_name
        return False
