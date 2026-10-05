from tools import calculator


def test_calculator_normal():
    assert calculator("17*23+5") == "396"
    assert calculator("2**10") == "1024"
    assert calculator("10 / 4") == "2.5"


def test_calculator_empty_input():
    for expr in ("", "   "):
        result = calculator(expr)
        assert result.startswith("calculation error"), result


def test_calculator_error():
    assert calculator("1/0") == "calculation error: division by zero"
    assert "only numbers and arithmetic" in calculator("__import__('os')")
