import bidict

import database


# класс описывающий книгу
class Book:

    def __init__(self, id: int, author: str, name: str, genre: str):
        self.id = id
        self.author = author
        self.name = name
        self.genre = genre

    # проверяет вхождение строки в основные поля книги
    def __contains__(self, item: str):
        return item.lower() in self.author.lower() or item in self.name.lower()


# класс описывающий библиотеку
class Library:

    def __init__(self, name: str = "library"):
        self.name = name
        # создаём книжную полку - словарь в котором ключ - айди книги, значения - сама книга
        self.bookshelf = dict()
        # для жанров используем двухсторонний словарь, чтобы можно было получать не только жанр по айди, но и айди по жанру
        # жанры не могут повторяться, так что конфликтов быть не может
        self.genres = bidict.bidict()
        self.db = database.SQLiteDatabase(name)
        self.load_data()

    def load_data(self):
        # загружаем информацию о книгах
        # бд автоматически находит название жанра по записанному айдишнику, так что не нужно сверять все жанры по айди
        for book_data in self.db.get_books():
            self.bookshelf[book_data['id']] = Book(book_data['id'], book_data['author'], book_data['name'], book_data['genre'])
        # загружаем информацию о жанрах
        for genre_data in self.db.get_genres():
            self.genres[genre_data['id']] = genre_data['name']

    def create_book(self, author: str, name: str, genre: str):
        # проверяем использовался ли жанр до этого, если нет записываем его в бд
        if genre not in self.genres.values():
            # при сохранении жанра бд присваивает ему айди и возвращает его
            # используем это айди для записи жанра в словарь
            self.genres[self.db.save_genre(genre)] = genre
        # записываем информацию о книге в бд, база данных присваивает книге айди и возвращает его
        # айди жанра книги получаем через двухсторонний словарь
        book_id = self.db.save_book(author, name, self.genres[genre])
        # используем это айди для создания книги
        book = Book(book_id, author, name, genre)
        self.bookshelf[book_id] = book
        return book

    def remove_book(self, book_id: int):
        # нельзя удалить книгу которой нет, поэтому если книги нет кидаем ошибку
        if book_id not in self.bookshelf:
            raise ValueError(f"Unknown book id: {book_id}")
        # удаляем книгу из списка книг и датабазы
        del self.bookshelf[book_id]
        self.db.delete_book(book_id)

    def get_book(self, book_id: int):
        # проверяем наличие книги в хранилище чтобы избежать ошибок
        if book_id not in self.bookshelf:
            return None
        return self.bookshelf[book_id]

    def get_books(self):
        # используется для итерации по книгам
        return self.bookshelf.values()

    def find_by_keyword(self, word: str):
        books = []
        # проверяем вхождение ключевого слова в каждой книге, записываем результат в список
        for book in self.get_books():
            if word in book:
                books.append(book)
        return books

    def find_by_genre(self, genre: str):
        books = []
        genre = genre.lower()
        # сравниваем данный жанр с жанром каждой книги, записываем результат в список
        for book in self.get_books():
            if book.genre.lower() == genre:
                books.append(book)
        return books


# Класс представляющий пользовательский интерфейс библиотеки в консоли
# Этот класс является посредником между пользователем и библиотекой
# Фактически он не выполняет никакую работу, лишь передаёт запросы пользователя библиотеке и выводит результат
class LibraryConsoleUI:

    def __init__(self, library: Library):
        self.library = library
        # команды представляют из себя словарь, в котором каждая команда привязана к определённой строке
        # команда выполняется когда пользователь вводит в консоль соответствующую строку
        self.commands = {"создать книгу": self.create_book,
                         "список книг": self.list_books,
                         "найти по жанру": self.find_books_by_genre,
                         "найти по ключевому слову": self.find_books_by_keyword,
                         "информация о книге": self.get_book,
                         "удалить книгу": self.delete_book}

    def start(self):
        # блокируем поток бесконечным циклом
        while True:
            # выводим список команд и ждём ввод пользователя
            inp = input(f"Выберите команду: {', '.join(self.commands.keys())}").lower()
            # если пользователь ввёл правильную команду передаём управление программой исполнителю этой команды
            # иначе указываем на ошибку и заново просим команду
            if inp in self.commands:
                self.commands[inp]()
            else:
                print("Неизвестная команда")

    def create_book(self):
        # команда добавления книги в библиотеку
        # собираем у пользователя данные о будущей книге
        author = input("Введите автора: ")
        name = input("Введите название книги: ")
        # выводим список ранее использованных жанров
        print("Выберите жанр книги:", *self.library.genres.values())
        print("Или добавьте новый жанр")
        genre = input().lower()
        # передаём запись книги в оперативку и базу данных библиотеке
        book = self.library.create_book(author, name, genre)
        print(f"Книга создана, айди: {book.id}")

    def list_books(self):
        # команда для вывода списка всех книг
        if self.library.bookshelf:
            self.print_books(self.library.get_books())
        else:
            print("Список книг пуст")

    def find_books_by_keyword(self):
        # команда для поиска книг по ключевому слову
        print("Введите ключевое слово: ", end="")
        # избегаем названия переменной keyword, т.к. это название занято одной из встроенных библиотек питона
        word = input()
        # поиском книг занимается библиотека
        books = self.library.find_by_keyword(word)
        # выводим результат или сообщение об отсутствии результата
        if books:
            self.print_books(books)
        else:
            print("Книг не найдено")

    def find_books_by_genre(self):
        # команда для поиска книг по жанру
        print("Введите жанр: ", end="")
        genre = input()
        # работу с книгами выполняет библиотека
        books = self.library.find_by_genre(genre)
        # выводим результат или сообщение о его отсутствии
        if books:
            self.print_books(books)
        else:
            print("Книг с таким жанром не найдено")

    def delete_book(self):
        # команда для удаления книги из библиотеки
        inp = input("Введите айди книги: ")
        # проверяем ввод с консоли на валидность, просим айди пока пользователь его не предоставит
        while not inp.isnumeric():
            inp = input("Введите число ")
        # работой с книгами занимается библиотека
        book = self.library.get_book(int(inp))
        # проверяем нашлась ли книга
        if book is None:
            print("Книги с таким айди не найдено")
            return
        # удаляем книгу из библиотеки
        self.library.remove_book(book.id)
        print("Книга удалена")

    def get_book(self):
        # команда для поиска книги по айди
        inp = input("Введите айди книги: ")
        # проверяем ввод пользователя на валидность
        while not inp.isnumeric():
            inp = input("Введите число ")
        book_id = int(inp)
        # ищем в библиотеке книгу
        book = self.library.get_book(book_id)
        # выводим сообщение если книги не нашлось, иначе выводим информацию о книге
        if book is None:
            print("Книги с таким айди не найдено")
            return
        print(f"{book.id} - Автор: {book.author}, название: {book.name}, жанр: {book.genre}")

    def print_books(self, books):
        # метод используемый для вывода коллекции книг
        for book in books:
            print(f"{book.id} - Автор: {book.author}, название: {book.name}")
