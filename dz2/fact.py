def fact_rec(n):
    if n <= 1:
        return 1
    return n * fact_rec(n-1)

def fact_it(n):
    result = 1
    for i in range(1, n+1):
        result *= i
    return result

if __name__ == '__main__':
    import timeit
    n = 100
    rec_time = timeit.timeit(f'fact_rec({n})', globals=globals(), number=100)
    it_time = timeit.timeit(f'fact_it({n})', globals=globals(), number=100)
    print(f"Рекурсивная версия: {rec_time:.6f} сек")
    print(f"Итерационная версия: {it_time:.6f} сек")
