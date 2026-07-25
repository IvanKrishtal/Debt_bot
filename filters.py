from aiogram.filters import BaseFilter
from aiogram.types import Message

from database import get_debt


class RegisteredFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = get_debt(message.from_user.id)
        return user is not None

class NotRegisteredFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = get_debt(message.from_user.id)
        return user is None   # ← True, если пользователя нет