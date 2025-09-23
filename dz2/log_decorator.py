import datetime

def function_logger(log_file):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.datetime.now()

            result = func(*args, **kwargs)

            end_time = datetime.datetime.now()
            duration = end_time - start_time

            with open(log_file, 'a') as f:
                f.write(f"{func.__name__}\n")
                f.write(f"{start_time}\n")
                f.write(f"Positional args: {args}\n")
                f.write(f"Keyword args: {kwargs}\n")
                f.write(f"Return value: {result if result is not None else '-'}\n")
                f.write(f"{end_time}\n")
                f.write(f"{duration}\n\n")

            return result
        return wrapper
    return decorator
