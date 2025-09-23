import re

def fun(email):
    pattern = r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9]+\.[a-zA-Z]{1,3}$'
    return bool(re.fullmatch(pattern, email))

if __name__ == '__main__':
    n = int(input())
    emails = [input().strip() for _ in range(n)]
    valid = sorted(filter(fun, emails))
    print(valid)
