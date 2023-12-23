import sqlite3


class SQLiteDatabase:

    def __init__(self, name: str):
        self.name = name
        self.connection = sqlite3.connect(f"db/{name}.db", check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
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
            return self.cursor.execute('''SELECT books.id, books.author, books.name, genres.name AS genre FROM books
            JOIN genres ON genres.id = books.genre''').fetchall()

    def save_book(self, author: str, name: str, genre: int) -> int:
        with self.connection:
            self.cursor.execute("INSERT INTO books (author, name, genre) VALUES (?, ?, ?)",
                                (author, name, genre))
            return self.cursor.lastrowid

    def delete_book(self, id: int):
        with self.connection:
            self.cursor.execute("DELETE FROM books WHERE id = ?", (id,))

    def get_genres(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM genres").fetchall()

    def save_genre(self, name: str) -> int:
        with self.connection:
            self.cursor.execute("INSERT INTO genres (name) VALUES (?)", (name,))
            return self.cursor.lastrowid
