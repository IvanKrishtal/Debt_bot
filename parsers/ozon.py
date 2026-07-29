import re
from datetime import datetime
from .base import BaseParser
from config import ADMIN_NAME


class OzonParser(BaseParser):
    def _find_debt(self, text: str) -> float | None:
        match = re.search(r"Сумма\s*([\d\s,]+)\s*₽", text)
        if match:
            num_str = re.sub(r"[^\d,]", "", match.group(1)).replace(",", ".")
            try:
                return float(num_str)
            except ValueError:
                return None
        return None

    def _find_receipt_time(self, text: str):
        match = re.search(r"(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2})", text)
        if match:
            day, month, year, hour, minute = match.groups()
            return datetime(int(year), int(month), int(day), int(hour), int(minute))
        return None

    def _check_name(self, text: str) -> bool:
        match = re.search(r"Получатель\s*([А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.?)", text)
        if match:
            name_from_cheque = match.group(1).strip().replace(".", "").lower()
            admin_name = ADMIN_NAME.strip().replace(".", "").lower()
            return name_from_cheque == admin_name
        return False
