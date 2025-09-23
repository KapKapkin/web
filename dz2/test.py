import pytest
import math
import os
import tempfile
from unittest.mock import patch

from fact import fact_rec, fact_it
from show_employee import show_employee
from sum_and_sub import sum_and_sub
from process_list import process_list, process_list_gen
from my_sum import my_sum
from files_sort import sort_files
from file_search import search_file
from email_validation import fun as email_validation
from fibonacci import fibonacci, fibonacci_cubes
from average_scores import compute_average_scores
from plane_angle import Point, plane_angle
from phone_number import format_phone_number, sort_and_format_phones
from people_sort import people_sort
from complex_numbers import Complex
from circle_square_mk import circle_square_mk
from log_decorator import function_logger

class TestFactorial:
    @pytest.mark.parametrize("n,expected", [
        (1, 1),
        (2, 2),
        (3, 6),
        (4, 24),
        (5, 120),
        (0, 1),
        (10, 3628800),
    ])
    def test_fact_rec(self, n, expected):
        assert fact_rec(n) == expected

    @pytest.mark.parametrize("n,expected", [
        (1, 1),
        (2, 2),
        (3, 6),
        (4, 24),
        (5, 120),
        (0, 1),
        (10, 3628800),
    ])
    def test_fact_it(self, n, expected):
        assert fact_it(n) == expected

class TestShowEmployee:
    def test_with_salary(self):
        assert show_employee("Иванов Иван Иванович", 30000) == "Иванов Иван Иванович: 30000 ₽"

    def test_without_salary(self):
        assert show_employee("Петров Петр Петрович") == "Петров Петр Петрович: 100000 ₽"

    def test_zero_salary(self):
        assert show_employee("Сидоров Сидор Сидорович", 0) == "Сидоров Сидор Сидорович: 0 ₽"

class TestSumAndSub:
    @pytest.mark.parametrize("a,b,expected", [
        (5, 3, (8, 2)),
        (10, 4, (14, 6)),
        (-5, 3, (-2, -8)),
        (0, 0, (0, 0)),
        (3.5, 2.5, (6.0, 1.0)),
    ])
    def test_sum_and_sub(self, a, b, expected):
        assert sum_and_sub(a, b) == expected

class TestProcessList:
    @pytest.mark.parametrize("arr,expected", [
        ([1, 2, 3, 4], [1, 4, 27, 16]),
        ([2, 4, 6], [4, 16, 36]),
        ([1, 3, 5], [1, 27, 125]),
        ([0], [0]),
        ([10, 11], [100, 1331]),
    ])
    def test_process_list(self, arr, expected):
        assert process_list(arr) == expected

    @pytest.mark.parametrize("arr,expected", [
        ([1, 2, 3, 4], [1, 4, 27, 16]),
        ([2, 4, 6], [4, 16, 36]),
        ([1, 3, 5], [1, 27, 125]),
    ])
    def test_process_list_gen(self, arr, expected):
        assert list(process_list_gen(arr)) == expected

class TestMySum:
    def test_no_args(self):
        assert my_sum() == 0

    def test_single_arg(self):
        assert my_sum(5) == 5

    def test_multiple_args(self):
        assert my_sum(1, 2, 3, 4, 5) == 15

    def test_floats(self):
        assert my_sum(1.5, 2.5, 3.0) == 7.0

    def test_negative_numbers(self):
        assert my_sum(-1, -2, -3) == -6

class TestFilesSort:
    def test_sort_files(self, tmp_path):

        (tmp_path / "a.py").touch()
        (tmp_path / "b.txt").touch()
        (tmp_path / "c.py").touch()
        (tmp_path / "a.txt").touch()

        with patch('builtins.print') as mock_print:
            sort_files(str(tmp_path))
            calls = [call[0][0] for call in mock_print.call_args_list]
            expected_order = ["a.py", "c.py", "a.txt", "b.txt"]
            assert calls == expected_order

class TestEmailValidation:
    @pytest.mark.parametrize("email,expected", [
        ("lara@mospolytech.ru", True),
        ("brian-23@mospolytech.ru", True),
        ("britts_54@mospolytech.ru", True),
        ("invalid@", False),
        ("@mospolytech.ru", False),
        ("test@domain", False),
        ("test.email@domain.com", False),
        ("test@domain.toolongextension", False),
    ])
    def test_email_validation(self, email, expected):
        assert email_validation(email) == expected

class TestFibonacci:
    @pytest.mark.parametrize("n,expected", [
        (1, [0]),
        (2, [0, 1]),
        (5, [0, 1, 1, 2, 3]),
        (8, [0, 1, 1, 2, 3, 5, 8, 13]),
    ])
    def test_fibonacci(self, n, expected):
        assert fibonacci(n) == expected

    @pytest.mark.parametrize("n,expected", [
        (1, [0]),
        (2, [0, 1]),
        (5, [0, 1, 1, 8, 27]),
    ])
    def test_fibonacci_cubes(self, n, expected):
        assert fibonacci_cubes(n) == expected

class TestAverageScores:
    def test_compute_average_scores(self):
        scores = [(89, 90, 78, 93, 80), (90, 91, 85, 88, 86), (91, 92, 83, 89, 90.5)]
        expected = (90.0, 91.0, 82.0, 90.0, 85.5)
        assert compute_average_scores(scores) == expected

    def test_single_subject(self):
        scores = [(100, 90, 80)]
        expected = (100.0, 90.0, 80.0)
        assert compute_average_scores(scores) == expected

class TestPlaneAngle:
    def test_point_operations(self):
        p1 = Point(1, 2, 3)
        p2 = Point(4, 5, 6)

        diff = p1 - p2
        assert diff.x == -3 and diff.y == -3 and diff.z == -3

        cross = p1.cross(p2)
        assert cross.x == -3 and cross.y == 6 and cross.z == -3

        assert p1.dot(p2) == 32

        assert abs(p1.magnitude() - math.sqrt(14)) < 1e-10

class TestPhoneNumber:
    @pytest.mark.parametrize("phone,expected", [
        ("89175551234", "+7 (917) 555-12-34"),
        ("79175551234", "+7 (917) 555-12-34"),
        ("09175551234", "+7 (917) 555-12-34"),
        ("9175551234", "+7 (917) 555-12-34"),
    ])
    def test_format_phone_number(self, phone, expected):
        assert format_phone_number(phone) == expected

class TestPeopleSort:
    def test_people_sort(self):
        people = [
            {'name': 'Robert Bustle', 'age': 32, 'gender': 'M'},
            {'name': 'Mike Thomson', 'age': 20, 'gender': 'M'},
            {'name': 'Andria Bustle', 'age': 30, 'gender': 'F'}
        ]
        sorted_people = people_sort(people)
        ages = [p['age'] for p in sorted_people]
        assert ages == [20, 30, 32]

class TestComplexNumbers:
    def test_complex_operations(self):
        c1 = Complex(2, 1)
        c2 = Complex(5, 6)

        result = c1 + c2
        assert result.real == 7 and result.imaginary == 7

        result = c1 - c2
        assert result.real == -3 and result.imaginary == -5

        result = c1 * c2
        assert result.real == 4 and result.imaginary == 17

    def test_complex_str(self):
        assert str(Complex(2, 1)) == "2.00+1.00i"
        assert str(Complex(2, -1)) == "2.00-1.00i"
        assert str(Complex(0, 5)) == "0.00+5.00i"
        assert str(Complex(5, 0)) == "5.00+0.00i"

class TestCircleSquareMK:
    def test_circle_square_mk(self):

        result = circle_square_mk(1, 1000)

        assert 2.5 < result < 4.0

    def test_circle_square_mk_zero_radius(self):
        assert circle_square_mk(0, 100) == 0

class TestLogDecorator:
    def test_function_logger(self, tmp_path):
        log_file = tmp_path / "test.log"

        @function_logger(str(log_file))
        def test_func(x, y=10):
            return x + y

        result = test_func(5, y=15)
        assert result == 20

        assert log_file.exists()
        content = log_file.read_text()
        assert "test_func" in content
        assert "Positional args: (5,)" in content
        assert "Keyword args: {'y': 15}" in content
        assert "Return value: 20" in content
