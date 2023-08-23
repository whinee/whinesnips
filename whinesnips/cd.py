import warnings
from enum import Enum
from typing import Any

from . import DEF_STR

try:
    from .utils.exceptions import CDExceptions
    from .utils.types import CustomDictType, Kwargs
    from .utils.utils import str2int
except ImportError:
    from whinesnips.utils.exceptions import CDExceptions
    from whinesnips.utils.types import CustomDictType, Kwargs
    from whinesnips.utils.utils import str2int

warnings.filterwarnings("ignore")

# Program Constants
BEHAVIOR = Enum("BEHAVIOR", ["modify", "insert", "append"])
DEFAULT_SEP = "/"


def flatten_element(elem: CustomDictType, sep: str = DEFAULT_SEP) -> "CustomDict":
    flattened_dict = {}
    stack = [(elem, "")]

    while stack:
        current_elem, parent_key = stack.pop(0)

        if isinstance(current_elem, list) or isinstance(current_elem, tuple):
            for i, item in enumerate(current_elem):
                item_key = str(i)
                new_key = f"{parent_key}{sep}{item_key}" if parent_key else item_key
                if isinstance(item, dict):
                    stack.append((item, new_key))
                else:
                    flattened_dict[new_key] = item
        elif isinstance(current_elem, dict):
            for key, value in current_elem.items():
                if not isinstance(key, int) and not isinstance(key, str):
                    raise CDExceptions.API.TypeError.KeyNotStrOrInt(type(key))
                new_key = f"{parent_key}{sep}{key}" if parent_key else str(key)

                if isinstance(value, dict):
                    stack.append((value, new_key))
                elif isinstance(value, list) or isinstance(value, tuple):
                    for i, item in enumerate(value):
                        item_key = f"{new_key}{sep}{i}"
                        flattened_dict[item_key] = item
                else:
                    flattened_dict[new_key] = value

    return CustomDict(flattened_dict)


class CustomDict(dict):  # type: ignore[type-arg]
    """Custom dictionary."""

    def __init__(self, *args: CustomDictType, **kwargs: Kwargs) -> None:  # type: ignore[no-untyped-def]
        if args:
            arg = args[0]
            if isinstance(arg, dict):
                for key, value in arg.items():
                    self[key] = value
            else:
                for key, value in arg:
                    self[key] = value

        for key in kwargs.keys():
            if not isinstance(key, int | str):
                raise CDExceptions.API.TypeError.KeyNotStrOrInt(type(key))

        super().__init__(*args, **kwargs)

    def __setitem__(self, key: int | str, value: Any) -> None:
        if not (
            (isinstance(key, int) and (not isinstance(key, bool)))
            or isinstance(key, str)
        ):
            raise CDExceptions.API.TypeError.KeyNotStrOrInt(type(key))
        super().__setitem__(key, value)

    def __getitem__(self, key: str) -> Any:
        op = super().__getitem__(key)
        if op.__class__.__mro__[-2] is dict:
            return CustomDict(op)
        return op

    def traverse(
        self,
        path: str,
        sep: str,
    ) -> tuple[int, dict[str, Any]]:
        """
        Given a path, traverse the element (self, which is a dictionary).

        The function returns a tuple of integer and dictionary.
        The integer is the return state. Hereunder return states,
        their description and corresponding return's description.

        | State | Description                       | Return Description                    |
        |------:|----------------------------------:|:--------------------------------------|
        | 0     | Path fully traversed              | Indexed Item                          |
        | 1     | Path's not in element             | Kwargs for CDEA.KeyError.NotInElement |
        | 2     | Path's current index not in range | Kwargs for CDEA.IndexError.OutOfRange |

        When the path is fully traversed (state 0),
        it gives out the following dictionary and the corresponding keys' types:

        ```python
            {
                "value": Any,
                "key_type_kv": dict[int | str, str],
            }
        ```

        Whereas:

        - `value` is the indexed item
        - `key_type_kv` is key-value pair (dict) of keys that are used to
        traverse the element and the type of the element traversed.
        The keys will be evaluated so that list indexes will be in integer.
        Or when an integer is used as a key in the element,
        it will also show up as such in here.
        The element type will be in string, and the only allowed ones are
        `dict`, `list` and `tuple`.

        Consider the following:

        ```python
        test = CustomDict({"w": (["a", {"b": "c"}], ["d"])})
        ```

        When traversed with the following:

        ```python
        test.traverse("w/-2/+1/b")
        ```

        The following should be returned:

        ```python
        {
            "value": "c",
            "key_type_kv": {
                "w": "dict",
                 -2: "tuple",
                  1: "list",
                "b": "dict"
            },
        }
        ```

        Args:
            path (str): Path to traverse.
            sep (str): Seperator of the path for individual indexes.

        Raises:
            CDExceptions.API.IndexError.EmptyString:
            Raised when the currently traversed element is a list or tuple,
            and the current key is an empty string.
            CDExceptions.API.IndexError.NotInteger:
            Raised when the currently traversed element is a list or tuple,
            and the current key is not a valid integer.
            CDExceptions.API.TypeError.CurrentElementNotDictListOrTuple:
            Raised when the currently traversed element is not the last element
            to index and is not a dict, list, or tuple.

        Returns:
            tuple[int, dict[str, int]]: _description_
        """

        # Initialize Empty Variables
        key_type_kv: dict[int | str, str] = {}

        # Initialize Variables
        elem = self
        idx = 0
        og_path = path

        while True:
            tc = type(elem).__mro__[-2]
            path_ls = path.split(sep)

            key: int | str = path_ls[0]
            ls_idx = str2int(key)
            is_not_last = len(path_ls) > 1

            # If Element is a dictionary
            if tc is dict:
                idx += 1
                typed_elem: dict[int | str, Any] = elem  # type: ignore[assignment]
                if (key not in typed_elem) and (ls_idx is not None):
                    key = ls_idx
                if key in typed_elem:
                    key_type_kv[key] = "dict"
                    if is_not_last:
                        path = path.replace(str(key) + sep, "", 1)
                        elem = typed_elem[key]
                    else:
                        return 0, {"value": typed_elem[key], "key_type_kv": key_type_kv}
                else:
                    return 1, {"idx": idx, "key_type_kv": key_type_kv}

            # If element is a list or a tuple
            elif isinstance(elem, list) or isinstance(elem, tuple):
                if len(key) < 0:
                    raise CDExceptions.API.IndexError.EmptyString(
                        sep=sep,
                        og_path=og_path,
                        idx=idx,
                        tc=tc,
                    )
                if ls_idx is None:
                    raise CDExceptions.API.IndexError.NotInteger(
                        sep=sep,
                        og_path=og_path,
                        idx=idx,
                        tc=tc,
                        key=key,
                    )
                len_iter = len(elem)
                if len_iter > ls_idx > (-1 - len_iter):
                    key_type_kv[ls_idx] = tc.__name__
                    if is_not_last:
                        path = path.replace(key + sep, "", 1)
                        elem = elem[ls_idx]
                        idx += 1
                    else:
                        return 0, {"value": elem[ls_idx], "key_type_kv": key_type_kv}
                else:
                    return 2, {"idx": idx, "ls_idx": ls_idx, "len_iter": len_iter}

            # If element is neither a dictionary, list, or a tuple
            else:
                raise CDExceptions.API.TypeError.CurrentElementNotDictListOrTuple(
                    sep=sep,
                    og_path=og_path,
                    idx=idx,
                    tc=tc,
                )

    def dir(
        self,
        path: str = DEF_STR,
        de: Any = DEF_STR,
        sep: str = DEFAULT_SEP,
    ) -> Any:
        if path == DEF_STR:
            return self
        if path == "":
            if "" in self:
                return self[""]
            return self
        state, op = self.traverse(path=path, sep=sep)
        match state:
            case 0:
                value = op["value"]
                if isinstance(value, dict):
                    return CustomDict(value)
                return value
            case 1:
                if de != DEF_STR:
                    return de
                raise CDExceptions.API.KeyError.NotInElement(
                    sep=sep,
                    og_path=path,
                    **op,
                )
            case 2:
                if de != DEF_STR:
                    return de
                raise CDExceptions.API.IndexError.OutOfRange(
                    sep=sep,
                    og_path=path,
                    **op,
                )
            case _:
                raise CDExceptions.Internals.StateUnexpected(state=state, max_state=2)

    def modify(
        self,
        path: str = DEF_STR,
        value: Any = DEF_STR,
        sep: str = DEFAULT_SEP,
    ) -> "CustomDict":
        if (path == DEF_STR) or (value == DEF_STR):
            return self
        state, op = self.traverse(path=path, sep=sep)
        match state:
            case 0:
                keys = list(op["key_type_kv"].keys())
                if len(keys) > 1:
                    current = self.copy()
                else:
                    current = self
                last_key = keys.pop()
                for key in keys:
                    current = current[key]
                current[last_key] = value
                return self
            case 1:
                raise CDExceptions.API.KeyError.NotInElement(
                    sep=sep,
                    og_path=path,
                    **op,
                )
            case 2:
                raise CDExceptions.API.IndexError.OutOfRange(
                    sep=sep,
                    og_path=path,
                    **op,
                )
            case _:
                raise CDExceptions.Internals.StateUnexpected(state=state, max_state=2)

    def insert(
        self,
        path: str = DEF_STR,
        value: Any = DEF_STR,
        sep: str = DEFAULT_SEP,
        strict: bool = True,
    ) -> "CustomDict":
        if (path == DEF_STR) or (value == DEF_STR):
            return self

        og_path = path
        *path_ls, last_key = path.split(sep)
        lk_ls_idx = str2int(last_key)

        if len(path_ls) > 0:
            path = sep.join(path_ls)
            state, op = self.traverse(path=path, sep=sep)

            match state:
                case 0:
                    keys = list(op["key_type_kv"].keys())
                    idx = len(keys)
                    if idx > 1:
                        current = self.copy()
                    else:
                        current = self
                    second_last_key = keys.pop()
                    for key in keys:
                        current = current[key]

                    tc = type(current[second_last_key]).__mro__[-2]
                    tcn = tc.__name__
                    match tcn:
                        case "dict":
                            if strict:
                                raise CDExceptions.API.TypeError.CurrentElementNotListOrTuple(
                                    sep=sep,
                                    og_path=path,
                                    idx=idx,
                                    tc=tc,
                                )
                            if (last_key not in current) and (lk_ls_idx is not None):
                                last_key = lk_ls_idx  # type: ignore[assignment]
                            current[second_last_key][last_key] = value
                        case "list" | "tuple":
                            if len(last_key) < 0:
                                raise CDExceptions.API.IndexError.EmptyString(
                                    sep=sep,
                                    og_path=og_path,
                                    idx=idx,
                                    tc=tc,
                                )
                            if lk_ls_idx is None:
                                raise CDExceptions.API.IndexError.NotInteger(
                                    sep=sep,
                                    og_path=og_path,
                                    idx=idx,
                                    tc=tc,
                                    key=last_key,
                                )
                            op_value = list(op["value"])
                            op_value.insert(lk_ls_idx, value)
                            if tcn == "tuple":
                                op_value = tuple(op_value)  # type: ignore[assignment]
                            current[second_last_key] = op_value  # type: ignore[assignment]
                case 1:
                    if strict:
                        raise CDExceptions.API.KeyError.NotInElement(
                            sep=sep,
                            og_path=path,
                            **op,
                        )

                    key_type_kv = op["key_type_kv"]
                    path_ls_traversed = list(key_type_kv.keys())
                    len_path_ls_traversed = len(path_ls_traversed)
                    path_ls_left = path.split(sep)[len_path_ls_traversed:]

                    current = self.copy()

                    for key in path_ls_traversed:
                        current = current[key]

                    if (len_path_ls_traversed == 0) or (
                        list(key_type_kv.values())[-1] == "dict"
                    ):
                        pass
                    elif path_ls_left[0] == "0":
                        path_ls_left = path_ls_left[1:]
                        current[0] = {}
                        current = current[0]
                    else:
                        raise CDExceptions.API.TypeError.CurrentElementNotDict(
                            sep=sep,
                            og_path=path,
                            idx=len_path_ls_traversed,
                            tc=type(current),
                        )

                    if len_path_ls_traversed == 0:
                        current = {last_key: value}
                        first_left_key = path_ls_left[0]
                        for key in path_ls_left[1:]:
                            current = {key: current}
                        self[first_left_key] = current
                    else:
                        for key in path_ls_left:
                            current[key] = {}
                            current = current[key]
                        current[last_key] = value
                case 2:
                    raise CDExceptions.API.IndexError.OutOfRange(
                        sep=sep,
                        og_path=path,
                        **op,
                    )
                case _:
                    raise CDExceptions.Internals.StateUnexpected(
                        state=state,
                        max_state=2,
                    )
        else:
            if strict:
                raise CDExceptions.API.TypeError.CurrentElementNotListOrTuple(
                    sep=sep,
                    og_path=path,
                    idx=1,
                    tc=dict,
                )
            current = self
            if (last_key not in current) and (lk_ls_idx is not None):
                last_key = lk_ls_idx  # type: ignore[assignment]
            current[last_key] = value

        return self

    def append(
        self,
        path: str = DEF_STR,
        value: Any = DEF_STR,
        sep: str = DEFAULT_SEP,
    ) -> "CustomDict":
        if (path == DEF_STR) or (path == "") or (value == DEF_STR):
            return self

        state, op = self.traverse(path=path, sep=sep)
        match state:
            case 0:
                keys = list(op["key_type_kv"].keys())
                idx = len(keys)
                if idx > 1:
                    current = self.copy()
                else:
                    current = self

                for key in keys:
                    current = current[key]

                tc = type(current).__mro__[-2]
                tcn = tc.__name__
                match tcn:
                    case "dict":
                        raise CDExceptions.API.TypeError.CurrentElementNotListOrTuple(
                            sep=sep,
                            og_path=path,
                            idx=idx,
                            tc=tc,
                        )
                    case "list" | "tuple":
                        current.append(value)
                return self
            case 1:
                raise CDExceptions.API.KeyError.NotInElement(
                    sep=sep,
                    og_path=path,
                    **op,
                )
            case 2:
                raise CDExceptions.API.IndexError.OutOfRange(
                    sep=sep,
                    og_path=path,
                    **op,
                )
            case _:
                raise CDExceptions.Internals.StateUnexpected(state=state, max_state=2)

    def flatten(
        self,
        path: str = DEF_STR,
        sep: str = DEFAULT_SEP,
        flat_sep: str = DEFAULT_SEP,
    ) -> "CustomDict":
        if path == DEF_STR:
            return CustomDict(flatten_element(self, sep=flat_sep))
        if path == "":
            if "" in self:
                if isinstance(self[""], dict | list | tuple):
                    return CustomDict(flatten_element(self[""], sep=flat_sep))  # type: ignore[arg-type]
                raise CDExceptions.API.TypeError.CurrentElementNotDictListOrTuple(
                    sep=sep,
                    og_path=path,
                    idx=0,
                    tc=type(self[""]).__mro__[-2],
                )
            return CustomDict(flatten_element(self, sep=flat_sep))
        state, op = self.traverse(path=path, sep=sep)
        match state:
            case 0:
                value = op["value"]
                if isinstance(value, dict | list | tuple):
                    return CustomDict(flatten_element(value, sep=flat_sep))  # type: ignore[arg-type]
                raise CDExceptions.API.TypeError.CurrentElementNotDictListOrTuple(
                    sep=sep,
                    og_path=path,
                    idx=path.count(sep),
                    tc=type(value).__mro__[-2],
                )
            case 1:
                raise CDExceptions.API.KeyError.NotInElement(
                    sep=sep,
                    og_path=path,
                    **op,
                )
            case 2:
                raise CDExceptions.API.IndexError.OutOfRange(
                    sep=sep,
                    og_path=path,
                    **op,
                )
            case _:
                raise CDExceptions.Internals.StateUnexpected(state=state, max_state=2)
