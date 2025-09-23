def process_list(arr):
    return [x**2 if x % 2 == 0 else x**3 for x in arr]

def process_list_gen(arr):
    for x in arr:
        yield x**2 if x % 2 == 0 else x**3

if __name__ == '__main__':
    import timeit
    test_arr = list(range(1000))
    lc_time = timeit.timeit('process_list(test_arr)', globals=globals(), number=1000)
    gen_time = timeit.timeit('list(process_list_gen(test_arr))', globals=globals(), number=1000)
    print(f"List comprehension: {lc_time:.6f} сек")
    print(f"Generator: {gen_time:.6f} сек")
