import subprocess
import pytest

INTERPRETER = 'python'

def run_script(filename, input_data=None):
    proc = subprocess.run(
        [INTERPRETER, filename],
        input='\n'.join(input_data if input_data else []),
        capture_output=True,
        text=True,
        check=False
    )
    return proc.stdout.strip()

test_data = {
    'python_if_else': [
        ('1', 'Weird'),
        ('4', 'Not Weird'),
        ('3', 'Weird'),
        ('6','Weird'),
        ('22', 'Not Weird')
    ],
    'arithmetic_operators': [
        (['1', '2'], ['3', '-1', '2']),
        (['10', '5'], ['15', '5', '50'])
    ]
}

def test_hello_world():
    assert run_script('hello_world.py') == 'Hello, world!'

@pytest.mark.parametrize("input_data, expected", test_data['python_if_else'])
def test_python_if_else(input_data, expected):
    assert run_script('python_if_else.py', [input_data]) == expected

@pytest.mark.parametrize("input_data, expected", test_data['arithmetic_operators'])
def test_arithmetic_operators(input_data, expected):
    assert run_script('arithmetic_operators.py', input_data).split('\n') == expected

@pytest.mark.parametrize("s1,s2,expected", [
    ("abc", "cab", "YES"),
    ("abc", "def", "NO"),
    ("a", "a", "YES"),
    ("a", "b", "NO"),
    ("listen", "silent", "YES"),
    ("elbow", "below", "YES"),
    ("study", "dusty", "YES"),
    ("heart", "earth", "YES"),
    ("python", "java", "NO"),
    ("abcd", "dcba", "YES"),
    ("hello", "world", "NO"),
    ("aab", "baa", "YES"),
    ("abc", "abcd", "NO"),
    ("race", "care", "YES"),
])
def test_anagram(s1, s2, expected):
    assert run_script('anagram.py', [s1, s2]) == expected

def test_anagram_empty():
    result = run_script('anagram.py', ["\n", "\n"])
    assert result == "YES"

@pytest.mark.parametrize("a,b,expected", [
    ("4", "2", ["2", "2.0"]),
    ("5", "2", ["2", "2.5"]),
    ("9", "3", ["3", "3.0"]),
    ("7", "7", ["1", "1.0"]),
    ("10", "5", ["2", "2.0"]),
    ("1", "3", ["0", "0.3333333333333333"]),
    ("15", "4", ["3", "3.75"]),
    ("100", "7", ["14", "14.285714285714286"]),
    ("8", "1", ["8", "8.0"]),
    ("0", "5", ["0", "0.0"]),
])
def test_division(a, b, expected):
    assert run_script('division.py', [a, b]).split('\n') == expected

@pytest.mark.parametrize("nm,arr,A,B,expected", [
    ("3 2\n1 2 3\n1 3\n2 4", "", "", "", "1"),
    ("4 2\n1 2 3 4\n1 2\n3 4", "", "", "", "0"),
    ("2 1\n5 6\n5\n6", "", "", "", "0"),
    ("3 2\n1 2 3\n4 5\n6 7", "", "", "", "0"),
    ("3 2\n1 2 3\n1 2\n3 4", "", "", "", "1"),
])
def test_happiness(nm, arr, A, B, expected):
    input_data = nm.split('\n')
    assert run_script('happiness.py', input_data) == expected

def test_hello():
    assert run_script('hello.py') == 'Hello, world!'

@pytest.mark.parametrize("year,expected", [
    ("2000", "True"),
    ("1900", "False"),
    ("2004", "True"),
    ("2001", "False"),
    ("2400", "True"),
    ("1800", "False"),
    ("2016", "True"),
    ("2100", "False"),
    ("2024", "True"),
    ("1999", "False"),
])
def test_is_leap(year, expected):
    assert run_script('is_leap.py', [year]) == expected

@pytest.mark.parametrize("cmds,expected", [
    (["3", "append 1", "append 2", "print"], "[1, 2]"),
    (["4", "append 3", "insert 0 4", "print", "pop"], "[4, 3]"),
    (["5", "append 5", "append 6", "remove 5", "print", "reverse"], "[6]"),
    (["3", "append 7", "sort", "print"], "[7]"),
    (["4", "append 8", "append 9", "reverse", "print"], "[9, 8]"),
])
def test_lists(cmds, expected):
    output = run_script('lists.py', cmds)
    assert expected in output

@pytest.mark.parametrize("n,expected", [
    ("3", ["0", "1", "4"]),
    ("1", ["0"]),
    ("5", ["0", "1", "4", "9", "16"]),
    ("0", []),
    ("2", ["0", "1"]),
    ("4", ["0", "1", "4", "9"]),
    ("6", ["0", "1", "4", "9", "16", "25"]),
    ("7", ["0", "1", "4", "9", "16", "25", "36"]),
    ("8", ["0", "1", "4", "9", "16", "25", "36", "49"]),
    ("10", ["0", "1", "4", "9", "16", "25", "36", "49", "64", "81"]),
])
def test_loops(n, expected):
    result = run_script('loops.py', [n])
    if expected:
        assert result.split('\n') == expected
    else:
        assert result == ""

@pytest.mark.parametrize("n,A,B,expected", [
    ("2", "1 2\n3 4", "5 6\n7 8", ["19 22", "43 50"]),
    ("1", "2", "3", ["6"]),
    ("2", "0 1\n1 0", "1 0\n0 1", ["0 1", "1 0"]),
    ("2", "1 0\n0 1", "1 2\n3 4", ["1 2", "3 4"]),
    ("2", "2 2\n2 2", "2 2\n2 2", ["8 8", "8 8"]),
])
def test_matrix_mult(n, A, B, expected):
    input_data = [n] + A.split('\n') + B.split('\n')
    assert run_script('matrix_mult.py', input_data).split('\n') == expected

def test_max_word(tmp_path):
    test_text = "cat dog elephant lion"
    file_path = tmp_path / "example.txt"
    file_path.write_text(test_text)
    import shutil
    shutil.copy(str(file_path), "example.txt")
    result = run_script('max_word.py')
    assert "elephant" in result

@pytest.mark.parametrize("n,passengers,t,expected", [
    ("2", ["1 5", "6 10"], "7", "1"),
    ("3", ["1 3", "2 4", "5 7"], "2", "2"),
    ("1", ["1 2"], "1", "1"),
    ("2", ["1 2", "3 4"], "5", "0"),
    ("2", ["1 10", "5 15"], "12", "1"),
])
def test_metro(n, passengers, t, expected):
    input_data = [n] + passengers + [t]
    assert run_script('metro.py', input_data) == expected

@pytest.mark.parametrize("s,expected", [
    ("BANANA", "Stuart 12"),
    ("A", "Kevin 1"),
    ("B", "Stuart 1"),
    ("AEIOU", "Kevin 15"),
    ("ABAB", "Kevin 6"),
    ("BCDEF", "Stuart 13"),
    ("AEI", "Kevin 6"),
    ("BCD", "Stuart 6"),
    ("AEIOUBCDF", "Kevin 35"),
    ("XUAEIOUYZ", "Kevin 33"),
])
def test_minion_game(s, expected):
    assert run_script('minion_game.py', [s]) == expected

@pytest.mark.parametrize("n,students,expected", [
    ("3", ["Harry", "37.21", "Berry", "37.21", "Tina", "37.2"], ["Berry", "Harry"]),
    ("2", ["Anna", "50", "Bob", "40"], ["Anna"]),
    ("4", ["A", "10", "B", "20", "C", "20", "D", "30"], ["B", "C"]),
    ("2", ["A", "1", "B", "2"], ["B"]),
    ("3", ["A", "1", "B", "1", "C", "2"], ["C"]),
])
def test_nested_list(n, students, expected):
    input_data = [n] + students
    output = run_script('nested_list.py', input_data).split('\n')
    assert output == expected

def test_price_sum():
    result = run_script('price_sum.py')
    assert result == '6842.84 5891.06 6810.9'

@pytest.mark.parametrize("n,expected", [
    ("3", "123"),
    ("1", "1"),
    ("5", "12345"),
    ("0", ""),
    ("2", "12"),
    ("4", "1234"),
    ("6", "123456"),
    ("7", "1234567"),
    ("8", "12345678"),
    ("9", "123456789"),
    ("10", "12345678910"),
    ("15", "123456789101112131415"),
    ("20", "1234567891011121314151617181920"),
])
def test_print_function(n, expected):
    result = run_script('print_function.py', [n]).replace('\n', '')
    assert result == expected

@pytest.mark.parametrize("n,arr,expected", [
    ("5", "2 3 6 6 5", "5"),
    ("3", "1 2 3", "2"),
    ("4", "4 4 4 3", "3"),
    ("2", "10 20", "10"),
    ("6", "1 2 3 4 5 6", "5"),
    ("4", "10 10 9 8", "9"),
    ("7", "1 1 2 2 3 3 4", "3"),
    ("5", "5 4 3 2 1", "4"),
    ("3", "100 99 98", "99"),
    ("8", "8 7 6 5 4 3 2 1", "7"),
])
def test_second_score(n, arr, expected):
    assert run_script('second_score.py', [n, arr]) == expected

@pytest.mark.parametrize("s,expected", [
    ("a b c", "a-b-c"),
    ("hello world", "hello-world"),
    ("one", "one"),
    ("", ""),
    ("split join", "split-join"),
    ("this is a test", "this-is-a-test"),
    ("python programming", "python-programming"),
    ("  spaces  around  ", "spaces-around"),
    ("single", "single"),
    ("multiple   spaces   between", "multiple-spaces-between"),
])
def test_split_and_join(s, expected):
    assert run_script('split_and_join.py', [s]) == expected

@pytest.mark.parametrize("s,expected", [
    ("aBc", "AbC"),
    ("HELLO", "hello"),
    ("world", "WORLD"),
    ("123", "123"),
    ("", ""),
    ("PyThOn", "pYtHoN"),
    ("MixedCASE", "mIXEDcase"),
    ("lower case", "LOWER CASE"),
    ("UPPER CASE", "upper case"),
    ("Numbers123", "nUMBERS123"),
])
def test_swap_case(s, expected):
    assert run_script('swap_case.py', [s]) == expected

@pytest.mark.parametrize("input_data,expected_items", [
    (["10 3", "золото 5 100", "серебро 3 60", "медь 2 20"], ["золото", "серебро", "медь"]),
    (["5 2", "алмаз 3 150", "рубин 4 200"], ["рубин", "алмаз"]),
    (["8 3", "item1 4 40", "item2 3 30", "item3 2 25"], ["item2", "item3", "item1"]),
    (["15 4", "a 10 100", "b 8 80", "c 6 60", "d 4 40"], ["a", "b"]),
    (["7 2", "heavy 8 80", "light 2 30"], ["light", "heavy"]),
])
def test_pirate_ship(input_data, expected_items):
    output = run_script('pirate_ship.py', input_data)
    for item in expected_items:
        assert item in output
