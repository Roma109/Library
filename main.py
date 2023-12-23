import library


def main():
    lib = library.Library()
    interface = library.LibraryConsoleInterface(lib)
    interface.start()


if __name__ == '__main__':
    main()
