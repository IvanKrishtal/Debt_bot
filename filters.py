from aiogram.filters import BaseFilter
from aiogram.types import Message
from config import ADMIN_ID

from database import get_debt


class RegisteredFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = get_debt(message.from_user.id)
        return user is not None


class NotRegisteredFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = get_debt(message.from_user.id)
        return user is None


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id != ADMIN_ID:
            return False
        return await RegisteredFilter().__call__(message)
