import sqlite3

# * Таблица Users: id — Telegram ID, name — имя пользователя, debt — текущий долг


def init_db():
    # Создание базы данных
    db = sqlite3.connect("debt.db")
    cursor = db.cursor()

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            debt REAL DEFAULT 0
        )""")

    db.commit()
    db.close()


def add_user(user_data: tuple):
    # Добавление пользователя в базу
    db = sqlite3.connect("debt.db")
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO Users (id, name) VALUES (?, ?)", (user_data[0], user_data[1])
    )

    db.commit()
    db.close()


def del_user(user_id: int):
    # Удаление пользователя из базы
    db = sqlite3.connect("debt.db")
    cursor = db.cursor()

    cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))

    db.commit()
    db.close()


def set_debt(user_id: int, new_debt: float):
    db = sqlite3.connect("debt.db")
    cursor = db.cursor()

    cursor.execute("UPDATE Users SET debt = ? WHERE id = ? ", (new_debt, user_id))

    db.commit()
    db.close()


def get_debt(user_id: int) -> tuple:
    db = sqlite3.connect("debt.db")
    cursor = db.cursor()

    cursor.execute("SELECT debt FROM Users WHERE id = ? ", (user_id,))
    user_debt = cursor.fetchone()

    db.close()
    return user_debt


def get_user(user_id: int) -> tuple:
    db = sqlite3.connect("debt.db")
    cursor = db.cursor()

    cursor.execute("SELECT id, name, debt FROM Users WHERE id = ? ", (user_id,))
    user = cursor.fetchone()

    db.close()
    return user


def get_all_users() -> list[tuple]:
    db = sqlite3.connect("debt.db")
    cursor = db.cursor()

    cursor.execute("SELECT id, name, debt FROM Users ORDER BY debt DESC")
    users = cursor.fetchall()

    db.close()
    return users
