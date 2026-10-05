from tools import python_exec


def test_python_exec_normal():
    assert python_exec("print(sum(range(10)))") == "45"


def test_python_exec_empty_output():
    assert python_exec("x = 1") == "Code ran but the output is empty"


def test_python_exec_error():
    assert "ZeroDivisionError" in python_exec("1/0")
