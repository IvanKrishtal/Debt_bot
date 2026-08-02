💰 Бот для учёта общих расходов
Telegram-бот для автоматизации учёта расходов в общежитии, квартире или небольшой группе.

Функционал

Пользовательские команды
/start — приветствие и информация о боте
/register — регистрация пользователя
/mydebt — просмотр текущего долга

Оплата через PDF-чек
Просто отправь в чат PDF-файл с чеком из банка. Бот сам:
определит банк (Сбер, Т-Банк, Яндекс, Озон, ВТБ)
распознает сумму, дату и получателя
проверит, что чек не старше 3 дней
спишет сумму с твоего долга

Админ-команды
/new_expense — распределить расход на всех участников
/set_debt — установить долг конкретному пользователю
/del_user — удалить пользователя
/remind — отправить напоминания всем должникам
/all — посмотреть список всех пользователей с долгами

Автоматические уведомления
Ежедневные напоминания должникам в 16:00 и 20:00

Стек технологий
Python 3.12
Aiogram 3 (Telegram Bot API)
SQLite
Tesseract OCR
PyPDF2 / pypdf
pdf2image + poppler
asyncio, apscheduler
Регулярные выражения

Поддерживаемые банки
Сбербанк — текстовый PDF
Т-Банк — текстовый PDF
Яндекс Банк — текстовый PDF
Озон Банк — текстовый PDF
ВТБ — скан PDF (OCR)

Установка и запуск

1. Клонируй репозиторий
git clone https://github.com/IvanKrishtal/Dept_bot.git
cd Dept_bot

2. Создай виртуальное окружение (опционально)
python -m venv venv
source venv/bin/activate  # на Windows: venv\Scripts\activate

3. Установи зависимости
pip install -r requirements.txt

4. Создай .env файл
В корневой папке создай файл .env со следующим содержимым:

BOT_TOKEN=твой_токен_от_BotFather
PROXY_URL=http://127.0.0.1:10809
ADMIN_ID=твой_telegram_id
ADMIN_NAME=Иван Павлович К
ADMIN_PHONE=89139331235

Где взять:
BOT_TOKEN — у бота @BotFather в Telegram
ADMIN_ID — у бота @userinfobot в Telegram
PROXY_URL — если используешь прокси (для России)

5. Запусти бота
python bot.py

Структура проекта
bot.py — точка входа
handlers.py — все команды и обработчики
database.py — работа с SQLite
filters.py — фильтры (админ, регистрация)
dispatcher.py — бот и диспетчер
config.py — настройки
parsers/ — парсеры PDF-чеков для разных банков

Требования
Python 3.10 или выше
Установленный Tesseract OCR (для распознавания сканов)
Установленный poppler (для pdf2image)

Установка Tesseract (Windows)
Скачай установщик: https://github.com/UB-Mannheim/tesseract/wiki
Установи и добавь в PATH: C:\Program Files\Tesseract-OCR
Скачай русский язык: https://github.com/tesseract-ocr/tessdata/raw/main/rus.traineddata
Положи в папку: C:\Program Files\Tesseract-OCR\tessdata

Установка poppler (Windows)
Скачай: https://github.com/oschwartz10612/poppler-windows/releases
Распакуй в C:\poppler
Добавь в PATH: C:\poppler\bin

Автор
Иван Кришталь — GitHub
