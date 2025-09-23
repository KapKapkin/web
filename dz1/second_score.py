n = int(input())
arr = list(map(int, input().split()))
unique_scores = sorted(set(arr), reverse=True)
print(unique_scores[1])
