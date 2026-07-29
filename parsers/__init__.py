from .base import BaseParser
from .sber import SberParser
from .vtb import VtbParser
from .tbank import TBankParser
from .yandex import YandexParser
from .ozon import OzonParser

PARSERS = {
    "sber": SberParser,
    "tbank": TBankParser,
    "yandex": YandexParser,
    "ozon": OzonParser,
    "vtb": VtbParser,
}
