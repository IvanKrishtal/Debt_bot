import re
from datetime import datetime
from .base import BaseParser
from config import ADMIN_NAME


class TBankParser(BaseParser):
    def _find_debt(self, text: str) -> float | None:
        # * Ищем по "Итого"
        match = re.search(r"Итого\s*([\d\s,]+)\s*[₽i]?", text)
        if match:
            num_str = match.group(1).replace(" ", "").replace(",", ".")
            try:
                return float(num_str)
            except ValueError:
                return None
        return None

    def _find_receipt_time(self, text: str):
        match = re.search(r"(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2}):(\d{2})", text)
        if match:
            day, month, year, hour, minute, second = match.groups()
            return datetime(
                int(year), int(month), int(day), int(hour), int(minute), int(second)
            )
        return None

    def _check_name(self, text: str) -> bool:
        # * Ищем "Получатель" и имя после него
        match = re.search(r"Получатель\s*([А-ЯЁ][а-яё]+\s[А-ЯЁ]\.?)", text)
        if match:
            name_from_cheque = match.group(1).strip().replace(".", "").lower()
            admin_first = ADMIN_NAME.split()[0].lower()
            admin_last = ADMIN_NAME.split()[2].lower()
            return name_from_cheque == f"{admin_first} {admin_last}"
        return False
