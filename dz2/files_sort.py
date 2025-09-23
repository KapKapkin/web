import os
import sys

def sort_files(dir_path):
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    files.sort(key=lambda x: (os.path.splitext(x)[1], x))
    for f in files:
        print(f)

if __name__ == '__main__':
    sort_files(sys.argv[1])
