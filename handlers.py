# * ВСТРОЕННЫЕ БИБЛИОТЕКИ
from datetime import datetime, timedelta

# * AIOGRAM
from aiogram import F, types
from aiogram.filters import Command
from aiogram.types import (
    Message,
    BotCommand,
    BotCommandScopeChat,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# * КОНФИГИ И ЯДРО БОТА
from dispatcher import bot
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
    user = get_user(user_id)

    if user is None:
        await message.answer("👋 Привет! Ты не зарегистрирован. \nНапиши /register")
        return

    await message.answer(
        f"👋 Привет, {user[1]}!\n"
        f"💰 /mydebt - выводит твой долг"
        "📎 Чтобы оплатить, просто отправь PDF-чек в этот чат."
    )


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
    await message.answer("Поздравляем! Вы зарегистрированы")


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


# * Отправка сообщений о долге
@dp.message(Command("remind"), AdminFilter())
async def remind_command(message: Message = None):
    for user_data in get_all_users():
        if user_data[2] > 0:
            await bot.send_message(
                user_data[0], f"🔔 Напоминание:\nВаш долг составляет {user_data[2]} ₽"
            )
        if message:
            await message.answer(f"✅ Уведомления отправлены успешно! ")


# * Установление долга пользователю
class SetDebt(StatesGroup):
    waiting_new_debt = State()


@dp.message(Command("set_debt"), AdminFilter())
async def set_debt_command(message: Message):
    users = get_all_users()

    buttons = []
    for user in users:
        user_id, name, debt = user
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{name}: {debt}", callback_data=f"set_debt_{user_id}"
                )
            ]
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(
            "Выбери пользователя для изменения долга:", reply_markup=keyboard
        )


@dp.callback_query(F.data.startswith("set_debt"))
async def set_debt_amount(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[2])
    await state.update_data(user_id=user_id)
    await callback.message.edit_text("Введите сумму нового долга: ")
    await state.set_state(SetDebt.waiting_new_debt)
    await callback.answer()


@dp.message(SetDebt.waiting_new_debt)
async def set_debt_save(message: Message, state: FSMContext):
    try:
        new_debt = float(message.text)
    except ValueError:
        await message.answer("❌ Введи число")
        return

    data = await state.get_data()
    user_id = data["user_id"]

    old_debt = get_debt(user_id)[0]
    name = get_user(user_id)[1]

    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Да", callback_data=f"confirm_debt_{user_id}_{new_debt}"
            ),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel_debt"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(
        f"Поменять у {name} долг с {old_debt} ₽ на {new_debt} ₽?", reply_markup=keyboard
    )


@dp.callback_query(F.data.startswith("confirm_debt_"))
async def confirm_debt(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    user_id = int(parts[2])
    new_debt = float(parts[3])

    set_debt(user_id, new_debt)
    await state.clear()
    await callback.message.edit_text("✅ Долг обновлён")
    await callback.answer()


@dp.callback_query(F.data == "cancel_debt")
async def cancel_debt(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Действие отменено")
    await callback.answer()


# * Создание общего расхода — сумма делится между всеми участниками
class NewExpense(StatesGroup):
    waiting_amount = State()


@dp.message(Command("new_expense"), AdminFilter())
async def newexpense_start(message: Message, state: FSMContext):
    await message.answer("Введите сумму расхода:")
    await state.set_state(NewExpense.waiting_amount)


@dp.message(NewExpense.waiting_amount)
async def newexpense_save(message: Message, state: FSMContext):
    try:
        total = float(message.text)
    except ValueError:
        await message.answer("❌ Введи число")
        return

    users = get_all_users()
    if not users:
        await message.answer("❌ Нет пользователей")
        await state.clear()
        return

    amount_per_user = round(total / len(users), 2)

    for user_id, name, debt in users:
        new_debt = debt + amount_per_user
        set_debt(user_id, new_debt)
        await bot.send_message(
            user_id, f"🔔 Новый расход!\nНужно оплатить: {new_debt} ₽"
        )

    await message.answer(f"✅ Расход {total} ₽ распределён на {len(users)} человек")
    await state.clear()


# * Удаление пользователя
class DeleteUser(StatesGroup):
    confirm = State()


@dp.message(Command("del_user"), AdminFilter())
async def del_user_command(message: Message):
    users = get_all_users()

    buttons = []
    for user in users:
        user_id, name, _ = user
        buttons.append(
            [InlineKeyboardButton(text=name, callback_data=f"del_{user_id}")]
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Выбери пользователя для удаления:", reply_markup=keyboard)


@dp.callback_query(F.data.startswith("del_"))
async def confirm_delete(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[1])
    user = get_user(user_id)

    if not user:
        await callback.message.edit_text("❌ Пользователь не найден")
        await state.clear()
        await callback.answer()
        return

    buttons = [
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{user_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        f"Удалить пользователя {user[1]}?", reply_markup=keyboard
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("confirm_"))
async def delete_user_confirm(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[1])
    del_user(user_id)
    await set_user_commands(user_id)
    await state.clear()
    await callback.message.edit_text("✅ Пользователь удалён")
    await callback.answer()


@dp.callback_query(F.data == "cancel")
async def cancel_delete(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Удаление отменено")
    await callback.answer()


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
            BotCommand(command="new_expense", description="Распределить сумму покупки"),
            BotCommand(command="remind", description="отправить уведомления"),
            BotCommand(command="mydebt", description="Мой долг"),
            BotCommand(command="all", description="Все должники"),
            BotCommand(command="del_user", description="Удалить пользователя"),
            BotCommand(command="set_debt", description="Установить долг пользователя"),
        ]
    else:
        commands = [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="mydebt", description="Мой долг"),
        ]
    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=user_id))
