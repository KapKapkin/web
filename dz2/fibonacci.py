def fibonacci(n):
    a, b = 0, 1
    fib = []
    for _ in range(n):
        fib.append(a)
        a, b = b, a + b
    return fib

def fibonacci_cubes(n):
    return list(map(lambda x: x**3, fibonacci(n)))

if __name__ == '__main__':
    n = int(input())
    cubes = fibonacci_cubes(n)
    print(cubes)
