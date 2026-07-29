# * ВСТРОЕННЫЕ БИБЛИОТЕКИ
from datetime import datetime, timedelta

# * AIOGRAM
from aiogram import F, types
from aiogram.filters import Command
from aiogram.types import Message, BotCommand, BotCommandScopeChat
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# * КОНФИГИ И ЯДРО БОТА
from bot import bot
from config import ADMIN_ID, ADMIN_NAME, CHECK_DAYS, DEBT_FLOOR
from dispatcher import dp

# * БАЗА ДАННЫХ
from database import get_debt, get_user, add_user, set_debt, del_user, get_all_users

# * ФИЛЬТРЫ
from filters import RegisteredFilter, NotRegisteredFilter, AdminFilter

# * ПАРСЕРЫ PDF
from parsers import (
    BaseParser,
    SberParser,
    TBankParser,
    YandexParser,
    OzonParser,
    VtbParser,
    PARSERS,
)


# * Старт
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    await set_user_commands(user_id)
    await message.answer("✅ Бот работает через прокси!")


# * Долг
@dp.message(Command("mydebt"), RegisteredFilter())
async def get_debt_command(message: Message):
    user_id = message.from_user.id
    user_debt = get_debt(user_id)[0]
    await message.answer(f"💰 Твой долг: {user_debt} руб.")


# * Регистрация
class Registration(StatesGroup):
    name = State()


@dp.message(Command("register"), NotRegisteredFilter())
async def register_start_command(message: Message, state: FSMContext):
    await state.set_state(Registration.name)
    await message.answer("Введите свое имя")


@dp.message(Registration.name)
async def register_name_command(message: Message, state: FSMContext):
    user_name = message.text
    user_id = message.from_user.id
    add_user((user_id, user_name))
    await set_user_commands(user_id)
    await state.clear()
    await message.answer("Поздравляем! Вы зарегестрированы")


# * Список всех пользователей
@dp.message(Command("all"), AdminFilter())
async def all_users_command(message: Message):
    users = get_all_users()

    if not users:
        await message.answer("💤 Таблица пуста")
        return

    text = "📋 Список пользователей\n\n"
    for data in users:
        text += f"Id: {data[0]}\nName: {data[1]}\nDebt: {data[2]}\n\n"
    await message.answer(text)


# * Удаление пользователя
# TODO добавить функцию удаления пользователя


# * Обработчик файлов
@dp.message(F.document, RegisteredFilter())
async def handle_document(message: Message):
    doc = message.document

    # ! Проверка формата файла
    if not doc.file_name.endswith(".pdf"):
        await message.answer("❌ Отправь чек в формате PDF")
        return

    # * Скачивание файла
    file = await bot.get_file(doc.file_id)
    file_bytes = await bot.download_file(file.file_path)
    if hasattr(file_bytes, "read"):
        file_bytes = file_bytes.read()

    # * Извлечение текста и определение банка
    base = BaseParser()
    text = base.parse(file_bytes)
    if text is None:
        await message.answer("❌ Не удалось извлечь текст из файла")
        return

    bank = base.detect_bank(text)
    if bank == "unknown":
        await message.answer("❌ Не удалось определить банк по чеку")
        return

    # * Выбор парсера для банка
    parser = PARSERS.get(bank)
    parser = parser()

    # * Парсинг данных
    debt = parser._find_debt(text)
    receipt_time = parser._find_receipt_time(text)
    admin_flag = parser._check_name(text)

    # ? Проверка: найдена ли сумма
    if debt is None:
        await message.answer("❌ Не удалось найти сумму в чеке")
        return

    # ? Проверка: найдена ли дата
    if receipt_time is None:
        await message.answer("❌ Не удалось найти дату в чеке")
        return

    # ? Проверка: совпадает ли получатель
    if not admin_flag:
        await message.answer(
            f"⛔ Ошибка: получатель не совпадает с необходимым\n"
            f"Необходимый получатель: {ADMIN_NAME}"
        )
        return

    # # ? Проверка: не просрочен ли чек
    if receipt_time < datetime.now() - timedelta(days=CHECK_DAYS):
        await message.answer(f"⛔ Ошибка: чек старше {CHECK_DAYS} дней")
        return

    # * Всё ок — списываем долг
    user_id = message.from_user.id
    new_debt = max(0, get_debt(user_id)[0] - debt)
    new_debt = 0 if new_debt < DEBT_FLOOR else new_debt
    set_debt(user_id, new_debt)

    if new_debt == 0:
        await message.answer("✅ Ты всё оплатил!")
    else:
        await message.answer(f"💰 Остаток: {new_debt} ₽")


# * Функция обновления меню команд
async def set_user_commands(user_id: int):
    if get_debt(user_id) is None:
        commands = [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="register", description="Зарегистрироваться"),
        ]
    elif user_id == ADMIN_ID:
        commands = [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="mydebt", description="Мой долг"),
            BotCommand(command="all", description="Все должники"),
            BotCommand(command="pay", description="Оплатить долг"),
            BotCommand(command="help", description="Помощь"),
            BotCommand(command="del_user", description="Удалить пользователя"),
            BotCommand(command="newexpense", description="Новый расход"),
            BotCommand(command="set_debt", description="Установить долг"),
        ]
    else:
        commands = [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="mydebt", description="Мой долг"),
            BotCommand(command="all", description="Все должники"),
            BotCommand(command="pay", description="Оплатить долг"),
            BotCommand(command="help", description="Помощь"),
        ]
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=user_id))
