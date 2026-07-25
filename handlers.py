from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from dispatcher import dp  
from database import get_debt, add_user
from filters import RegisteredFilter, NotRegisteredFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, BotCommandScopeChat
from bot import bot
from config import ADMIN_ID

# Старт
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    await set_user_commands(user_id)
    await message.answer("✅ Бот работает через прокси!")

# Долг 
@dp.message(Command("mydebt"), RegisteredFilter())
async def get_debt_command(message: Message):
    user_id = message.from_user.id
    user_debt = get_debt(user_id)[0]
    await message.answer(f"💰 Твой долг: {user_debt} руб.")

# Регистрация
class Registration(StatesGroup):
    name = State()

@dp.message(Command("register"), NotRegisteredFilter())
async def register_start_command(message: Message, state: FSMContext):
    await state.set_state(Registration.name)
    await message.answer("Введите свое имя")

@dp.message(Registration.name)
async def register_name_command(message: Message):
    user_name = message.text
    user_id = message.from_user.id
    add_user((user_id, user_name))
    await set_user_commands(user_id)
    await message.answer("Поздравляем! Вы зарегестрированы")

# Функция обновления меню команд 
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
            BotCommand(command="add_user", description="Добавить пользователя"),
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