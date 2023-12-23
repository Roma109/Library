import library


def main():
    # инициализируем библиотеку
    lib = library.Library()
    # инициализируем консольный интерфейс для библиотеки
    interface = library.LibraryConsoleUI(lib)
    interface.start()


if __name__ == '__main__':
    main()
