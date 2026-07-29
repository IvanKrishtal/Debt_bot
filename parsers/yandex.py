import re
from datetime import datetime
from .base import BaseParser
from config import ADMIN_NAME, ADMIN_PHONE


class YandexParser(BaseParser):
    def _find_debt(self, text: str) -> float | None:
        match = re.search(r"Сумма операции\s*([\d\s,]+)\s*₽", text)
        if match:
            num_str = re.sub(r"[^\d,]", "", match.group(1)).replace(",", ".")
            try:
                return float(num_str)
            except ValueError:
                return None
        return None

    def _find_receipt_time(self, text: str):
        match = re.search(
            r"Дата и время операции МСК\s*(\d{2})\.(\d{2})\.(\d{4})\s+в\s+(\d{2}):(\d{2})",
            text,
        )
        if match:
            day, month, year, hour, minute = match.groups()
            return datetime(int(year), int(month), int(day), int(hour), int(minute))
        return None

    def _check_name(self, text: str) -> bool:
        match = re.search(r"Куда\s*(\+7[\d\s\-]+)", text)
        if match:
            phone_from_cheque = re.sub(r"\D", "", match.group(1))[-10:]
            admin_phone = re.sub(r"\D", "", ADMIN_PHONE)[-10:]
            return phone_from_cheque == admin_phone
        return False
