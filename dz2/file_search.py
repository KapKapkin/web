import os
import sys

def search_file(filename, current_path=None):
    if current_path is None:
        current_path = os.path.dirname(os.path.abspath(__file__))

    for item in os.listdir(current_path):
        item_path = os.path.join(current_path, item)
        if os.path.isfile(item_path) and item == filename:
            with open(item_path, 'r') as f:
                for i, line in enumerate(f):
                    if i < 5:
                        print(line.strip())
                    else:
                        break
            return True
        elif os.path.isdir(item_path):
            os.chdir(item_path)
            found = search_file(filename, os.getcwd())
            os.chdir("..")
            if found:
                return True
    return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Укажите имя файла для поиска")
    else:
        if not search_file(sys.argv[1]):
            print(f"Файл {sys.argv[1]} не найден")
