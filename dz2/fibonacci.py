n = int(input())

def fibonacci(n):
    a, b = 0, 1
    fib = []
    for _ in range(n):
        fib.append(a)
        a, b = b, a + b
    return fib

cubes = list(map(lambda x: x**3, fibonacci(n)))
print(cubes)