n = int(input())
students = []
for _ in range(n):
    name = input()
    score = float(input())
    students.append([name, score])
second_lowest = sorted(set(score for name, score in students))[1]
names = sorted([name for name, score in students if score == second_lowest])
for name in names:
    print(name)
