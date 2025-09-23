n = int(input())
passengers = [tuple(map(int, input().split())) for _ in range(n)]
t = int(input())
count = 0
for a, b in passengers:
    if a <= t <= b:
        count += 1
print(count)
