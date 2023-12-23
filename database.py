import sqlite3


# Класс, представляющий SQLite датабазу программы.
class SQLiteDatabase:

    def __init__(self, name: str):
        self.name = name
        # подключаемся к базе данных
        self.connection = sqlite3.connect(f"db/{name}.db", check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        # создаём таблицы в бд если их нет
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        author TEXT NOT NULL,
        name TEXT NOT NULL,
        genre INTEGER
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
        )''')
        self.connection.commit()

    def get_books(self):
        with self.connection:
            # получаем список книг
            return self.cursor.execute('SELECT * FROM books').fetchall()

    def save_book(self, author: str, name: str, genre: int) -> int:
        with self.connection:
            # сохраняем информацию о книге
            self.cursor.execute("INSERT INTO books (author, name, genre) VALUES (?, ?, ?)",
                                (author, name, genre))
            # бд сама присваивает книге айдишник, возвращаем его
            return self.cursor.lastrowid

    def delete_book(self, id: int):
        with self.connection:
            # удаляем книгу по айди
            self.cursor.execute("DELETE FROM books WHERE id = ?", (id,))

    def get_genres(self):
        with self.connection:
            # достаём все жанры
            return self.cursor.execute("SELECT * FROM genres").fetchall()

    def save_genre(self, name: str) -> int:
        with self.connection:
            # сохраняем информацию о жанре в бд
            self.cursor.execute("INSERT INTO genres (name) VALUES (?)", (name,))
            # база данных сама присваивает жанру айдишник, возвращаем его
            return self.cursor.lastrowid
