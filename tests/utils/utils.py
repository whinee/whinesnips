from whinesnips.utils.utils import str2int


def test_str2int() -> None:
    assert str2int("1") == 1
    assert str2int("+1") == 1
    assert str2int("-1") == -1
    assert str2int("-1.0") is None
    assert str2int("+f") is None
