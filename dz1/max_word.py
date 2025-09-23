import re
with open('example.txt') as f:
    words = re.findall(r'\b\w+\b', f.read())
max_len = max(len(word) for word in words)
for word in words:
    if len(word) == max_len:
        print(word)
