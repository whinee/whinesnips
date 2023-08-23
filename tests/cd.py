import pytest

from whinesnips.cd import CustomDict, flatten_element
from whinesnips.utils.exceptions import CDExceptions


class TestInitialize:
    def test_init_empty(self) -> None:
        """Initialize Empty CD."""

        assert CustomDict() == {}

    def test_init_with_dict(self) -> None:
        """Initialize CD with dict."""

        assert CustomDict({"a": 1, "b": 2}) == {"a": 1, "b": 2}

        assert CustomDict({"a": {"b": {"c": 3}}}) == {"a": {"b": {"c": 3}}}

    def test_init_with_wrong_key_types(self) -> None:
        """Initialize CD with wrong key types."""

        with pytest.raises(CDExceptions.API.TypeError.KeyNotStrOrInt):
            CustomDict({False: 1})  # type: ignore[arg-type]

        with pytest.raises(CDExceptions.API.TypeError.KeyNotStrOrInt):
            CustomDict({("waa",): 1})  # type: ignore[arg-type]


class TestDir:
    def test_basic(self) -> None:
        """Basic `dir` tests."""

        test = CustomDict({"a": {"b": {"c": [1, 2, 3]}}})

        assert test.dir("a/b/c") == [1, 2, 3]

        with pytest.raises(CDExceptions.API.KeyError.NotInElement):
            test.dir("a/b/d")

    def test_returns_cd(self) -> None:
        """Test if `modify` returns a CD when the indexed element is a dictionary."""

        assert isinstance(CustomDict({"a": {"b": {"c": 1}}}).dir("a/b"), CustomDict)

    def test_deeply_nested(self) -> None:
        """Deeply Nested CD."""

        # fmt: off
        test = CustomDict({"a": ("shit", "me", {"not": {"lol": [
            "why", "you", ["ask", "?", "cuz", {"why": "naught"}]],
        }})})
        # fmt: on
        assert test.dir(f"a/-1/not/lol/+2/{0-1}/why") == "naught"


class TestModify:
    def test_basic(self) -> None:
        """Basic `modify` tests."""

        test = CustomDict({"a": {"b": {"c": 3}}})
        test.modify("a/b/c", 4)
        assert test == {"a": {"b": {"c": 4}}}

        test = CustomDict({"a": 1})
        test.modify("a", 2)
        assert test == {"a": 2}

    def test_returns_cd(self) -> None:
        """Test if `modify` returns a CD."""

        assert isinstance(CustomDict({"a": 1}).modify("a", 2), CustomDict)

    def test_dict_dict(self) -> None:
        test = CustomDict({"a": {"b": "c"}})
        assert test.modify("a/b", "d") == {"a": {"b": "d"}}

    def test_dict_list(self) -> None:
        test = CustomDict({"a": ["b", "c"]})
        test.modify("a/1", "d")
        assert test == {"a": ["b", "d"]}
        test.insert("a/1", "c", strict=False)
        assert test == {"a": ["b", "c", "d"]}
        test.append("a", "e")
        assert test == {"a": ["b", "c", "d", "e"]}

    def test_list_list(self) -> None:
        test = CustomDict({"w": [["a", ["b", "c"]], ["e"]]})
        assert test.insert("w/0/1/2", "d") == {"w": [["a", ["b", "c", "d"]], ["e"]]}
        assert test.append("w/1", "f") == {"w": [["a", ["b", "c", "d"]], ["e", "f"]]}
        assert test.modify("w/0", "a") == {"w": ["a", ["e", "f"]]}


class TestInsert:
    def test_empty_dict(self) -> None:
        test = CustomDict()
        test.insert("a", 1, strict=False)
        assert test == {"a": 1}

    def test_empty_dict_nested_output_nie(self) -> None:
        test = CustomDict()
        with pytest.raises(CDExceptions.API.KeyError.NotInElement):
            test.insert("a/b/c", "d")

    def test_empty_dict_nested_output_init_empty_dict(self) -> None:
        test = CustomDict()
        assert test.insert("a/b/c", "d", strict=False) == {"a": {"b": {"c": "d"}}}

    def test_empty_dict_nested_output_init_one_deep_dict(self) -> None:
        test = CustomDict({"a": {}})
        assert test.insert("a/b/c", "d", strict=False) == {"a": {"b": {"c": "d"}}}

    def test_empty_dict_nested_output_init_two_deep_dict(self) -> None:
        test = CustomDict({"a": {"b": {}}})
        assert test.insert("a/b/c", "d", strict=False) == {"a": {"b": {"c": "d"}}}

    def test_empty_dict_nested_output_init_three_deep_dict(self) -> None:
        test = CustomDict({"a": {"b": {"c": {}}}})
        assert test.insert("a/b/c", "d", strict=False) == {"a": {"b": {"c": "d"}}}

    def test_empty_dict_nested_output_init_four_deep_dict(self) -> None:
        test = CustomDict({"a": {"b": {"c": "d"}}})
        assert test.insert("a/b/c", "d", strict=False) == {"a": {"b": {"c": "d"}}}
