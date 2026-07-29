"""
BASE PARSER — ЯДРО СИСТЕМЫ РАСПОЗНАВАНИЯ ЧЕКОВ

Задача: превратить PDF (текст или скан) в структурированный текст.
Подход: сначала пробуем pypdf (быстро), если пусто — запускаем OCR (медленно, но надёжно).

Банк определяется по уникальным ключевым словам (BANK_SIGNATURES).
Дочерние парсеры переопределяют методы _find_debt, _find_receipt_time, _check_name.
"""

from io import BytesIO
from pypdf import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
import os


class BaseParser:
    """
    Родительский класс для всех парсеров банков.
    Содержит общую логику: извлечение текста, OCR, определение банка.
    """

    # * Уникальные фразы для определения банка по тексту чека
    BANK_SIGNATURES = {
        "sber": ["деньги может вернуть только получатель"],
        "ozon": ["служба поддержки ozon банка:", "ООО «ОЗОН БАНК»"],
        "yandex": ["yabank.yandex.ru", "welcome@bank.yandex.ru"],
        "tbank": ["fb@tbank.ru", "tbank"],
        "vtb": ["банк втб", "втб"],
    }

    def parse(self, file_bytes: bytes):
        # * Сначала пробуем прочитать как текстовый PDF
        text = self._extract_text_from_pdf(file_bytes)
        if text.strip():
            return text

        # * Если текст пустой — пробуем OCR (скан)
        ocr_text = self._extract_text_with_ocr(file_bytes)
        return ocr_text

    def _extract_text_from_pdf(self, file_bytes: bytes) -> str:
        reader = PdfReader(BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    def _extract_text_with_ocr(self, file_bytes: bytes) -> str:
        images = convert_from_bytes(file_bytes, dpi=350)
        raw_text = ""
        for img in images:
            img = img.convert("L")
            raw_text += (
                pytesseract.image_to_string(img, lang="rus", config="--psm 6") + "\n"
            )

        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        return "\n".join(lines)

    def detect_bank(self, text: str) -> str:
        text_lower = text.lower()
        for bank, keywords in self.BANK_SIGNATURES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return bank
        return "unknown"

    # ! МЕТОДЫ ДЛЯ ПЕРЕОПРЕДЕЛЕНИЯ

    def _find_debt(self, text: str) -> float:
        raise NotImplementedError("_find_debt не реализован")

    def _find_receipt_time(self, text: str):
        raise NotImplementedError("_find_receipt_time не реализован")

    def _check_name(self, text: str) -> bool:
        raise NotImplementedError("_check_name не реализован")
