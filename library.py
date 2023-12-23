import database


class Book:

    def __init__(self, id: int, author: str, name: str, genre: str):
        self.id = id
        self.author = author
        self.name = name
        self.genre = genre

    def __contains__(self, item: str):
        return item.lower() in self.author.lower() or item in self.name.lower()


class Library:

    def __init__(self, name: str = "library"):
        self.name = name
        self.bookshelf = dict()
        self.genres = dict()
        self.db = database.SQLiteDatabase(name)
        self.load_data()

    def load_data(self):
        self.bookshelf.clear()
        for book_data in self.db.get_books():
            self.bookshelf[book_data['id']] = Book(book_data['id'], book_data['author'], book_data['name'], book_data['genre'])
        for genre_data in self.db.get_genres():
            self.genres[genre_data['id']] = genre_data['name']

    def create_book(self, author: str, name: str, genre: str):
        if genre not in self.genres.values():
            self.genres[self.db.save_genre(genre)] = genre
        id = self.db.save_book(author, name, self.get_genre_id(genre))
        book = Book(id, author, name, genre)
        self.bookshelf[id] = book
        return book

    def remove_book(self, id: int):
        if id not in self.bookshelf:
            raise ValueError(f"Unknown book id: {id}")
        del self.bookshelf[id]
        self.db.delete_book(id)

    def get_book(self, id: int):
        if id not in self.bookshelf:
            return None
        return self.bookshelf[id]

    def get_books(self):
        return self.bookshelf.values()

    def find_by_keyword(self, word: str):
        books = []
        for book in self.get_books():
            if word in book:
                books.append(book)
        return books

    def find_by_genre(self, genre: str):
        books = []
        genre = genre.lower()
        for book in self.get_books():
            if book.genre.lower() == genre:
                books.append(book)
        return books

    def get_genre_id(self, genre: str):
        for id in self.genres:
            if self.genres[id] == genre:
                return id
        return None


class LibraryConsoleInterface:

    def __init__(self, library):
        self.library = library
        self.commands = {"создать книгу": self.create_book,
                         "список книг": self.list_books,
                         "найти по жанру": self.find_books_by_genre,
                         "найти по ключевому слову": self.find_books_by_keyword,
                         "информация о книге": self.get_book,
                         "удалить книгу": self.delete_book}

    def start(self):
        while True:
            print(f"Выберите команду: {', '.join(self.commands.keys())}")
            inp = input().lower()
            if inp in self.commands:
                self.commands[inp]()
            else:
                print("Неизвестная команда")

    def create_book(self):
        print("Введите автора: ", end="")
        author = input()
        print("Введите название книги: ", end="")
        name = input()
        print("Выберите жанр книги:", *self.library.genres.values())
        print("Или добавьте новый жанр")
        genre = input().lower()
        book = self.library.create_book(author, name, genre)
        print(f"Книга создана, айди: {book.id}")

    def list_books(self):
        if self.library.bookshelf:
            self.print_books(self.library.get_books())
        else:
            print("Список книг пуст")

    def find_books_by_keyword(self):
        print("Введите ключевое слово: ", end="")
        word = input()
        books = self.library.find_by_keyword(word)
        if books:
            self.print_books(books)
        else:
            print("Книг не найдено")

    def find_books_by_genre(self):
        print("Введите жанр: ", end="")
        genre = input()
        books = self.library.find_by_genre(genre)
        if books:
            self.print_books(books)
        else:
            print("Книг с таким жанром не найдено")

    def delete_book(self):
        print("Введите айди книги: ", end="")
        inp = input()
        if not inp.isnumeric():
            self.delete_book()
            return
        book = self.library.get_book(int(inp))
        if book is None:
            print("Книги с таким айди не найдено")
            self.delete_book()
        self.library.remove_book(book.id)
        print("Книга удалена")

    def get_book(self):
        print("Введите айди книги: ", end="")
        inp = input()
        if not inp.isnumeric():
            self.get_book()
            return
        id = int(inp)
        book = self.library.get_book(id)
        if book is None:
            print("Книги с таким айди не найдено")
        print(f"{book.id} - Автор: {book.author}, название: {book.name}, жанр: {book.genre}")

    def print_books(self, books):
        for book in books:
            print(f"{book.id} - Автор: {book.author}, название: {book.name}")
