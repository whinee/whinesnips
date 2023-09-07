import ast
import difflib
import hashlib
import inspect
import itertools
import os
import re
import shlex
import shutil
import sys
import unicodedata
import warnings
from collections.abc import Callable, Generator, Iterable, Sized
from datetime import datetime
from itertools import cycle
from multiprocessing import Pool, pool
from os import makedirs
from os.path import dirname as dn
from os.path import realpath as rp
from re import Pattern
from subprocess import call
from typing import Any, Final, Optional

try:
    from .. import PSH
    from . import exceptions, types
except ImportError:
    from whinesnips import PSH
    from whinesnips.utils import exceptions, types


warnings.filterwarnings("ignore")

# Constants
PR = ["alpha", "beta", "rc"]  # Prerelease strings
CATEGORIES: Final[set[str]] = {"Cn"}

# Derived Constants
ALL_CHARS: Final[Generator[str, None, None]] = (chr(i) for i in range(sys.maxunicode))
CCHARS: Final[str] = "".join(
    map(chr, itertools.chain(range(0x00, 0x20), range(0x7F, 0xA0))),
)
CCHARS_RE: Final[Pattern[str]] = re.compile("[%s]" % re.escape(CCHARS))


# Class
class PoolTerminate:
    def __init__(self, pool: pool.Pool, callback: types.CallableAny) -> None:
        self.called = False
        self.pool = pool
        self.callback = callback

    def inner(self, err: bool, *args: types.Args, **kwargs: types.Kwargs) -> None:
        if err and (not self.called):
            self.called = True
            self.pool.terminate()
            self.callback(*args, **kwargs)


class CallbackGetResult:
    def __init__(self) -> None:
        self.args: tuple[None] | tuple[Any, ...] = ()

    def callback(self, *args: types.Args) -> None:
        self.args = args

    def get(self) -> tuple[None] | tuple[Any, ...]:
        return self.args


# Functions
def calc_hash(input: str) -> str:
    """
    Given a string, calculate its hash and return it.

    Args:
        input (str): String to hash.

    Returns:
        str: Hash of the string.
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input.encode("utf-8"))
    return sha256_hash.hexdigest()


def cycle_2ls(a: Sized, b: Sized) -> Iterable[Any]:
    """
    Given two list, iterate through both of them, and cycle the shorter list until the longer list has been exhausted.

    Args:
    - a (`Sized`): First sized iterable.
    - b (`Sized`): Second sized iterable.

    Returns:
    `Iterable[Any]`: _description_
    """
    if len(a) > len(b):
        return zip(a, cycle(b), strict=False)  # type: ignore[arg-type, call-overload, no-any-return]
    return zip(cycle(a), b, strict=False)  # type: ignore[arg-type, call-overload, no-any-return]


def dnn(fn: str, n: int) -> str:
    """
    Dirname N-th times.

    Given a file name and a number, find the parent directory of the given filename as many times as the given number.

    Args:
    - fn (`str`): The filename to find the parent directory of.
    - n (`int`): How many times the parent directory of the given filename should be found.

    Returns:
    `str`: Parent directory of the given filename.
    """
    op = fn
    for _ in range(n):
        op = os.path.dirname(op)
    return op


def dnrp(file: str, n: Optional[int] = None) -> str:
    """
    Get the directory component of a pathname by n times recursively then return it.

    Args:
    - file (`str`): File to get the directory of.
    - n (`Optional[int]`, optional): Number of times to get up the directory???? Defaults to 1.

    Returns:
    `str`: The directory component got recursively by n times from the given pathname
    """
    op = rp(file)
    for _ in range(ivnd(n, 1)):
        op = dn(op)
    return op


def dpop(
    d: dict[Any, Any],
    pop: list[int | list[str | int | tuple[str, ...]] | str],
    de: Optional[Any] = None,
) -> Any:
    """
    Iterate through the preferred order of precedence (`pop`) and see if the value exists in the dictionary. If it does, return it. If not, return `de`.

    Args:
    - d (`Dict[Any, Any]`): Dictionary to retrieve the value from.
    - pop (`list[int | tuple[str | int | tuple] | str]`): List of keys to iterate through.
    - de (`Any`, optional): Default object to be returned. Defaults to None.

    Returns:
    `Any`: Retrieved value.
    """

    for i in pop:
        if op := d.get(i):
            return op
    return de


def dt_ts(ts: str) -> str:
    """
    Convert the given unix timestamp to ISO 8601 format.

    Args:
    - ts (`str`): unix timestamp to be converted to ISO 8601 format

    Returns:
    `str`: Formatted datetime string
    """

    return (datetime.utcfromtimestamp(int(ts))).strftime("%Y-%m-%dT%H:%M:%S")


def file_exists(fp: str) -> str:
    """
    Check if the given file path exists.

    Args:
    - fp (`str`): File path to check if it exists.

    Raises:
    - `exceptions.GeneralExceptions.ValidationError.FileNotFound`: Raised when a file in the path is not found.

    Returns:
    `str`: Return `fp` when file path exists.
    """
    if not os.path.exists(fp):
        raise exceptions.GeneralExceptions.ValidationError.FileNotFound(fp)
    return fp


def fill_ls(
    *,
    ls: types.SequenceAny,
    length: int,
    filler: Optional[Any] = None,
) -> types.SequenceAny:
    """
    Fill given list (`ls`) with `filler` up to `length`.

    Args:
    - ls (`types.SequenceAny`): List to fill with `filler` up to `length`
    - length (`int`): Length of the list to achieve.
    - filler (`Optional[Any]`, optional): Filler to use. Defaults to `None`.

    Returns:
    `types.SequenceAny`: Filled list.
    """
    lls = len(ls)
    if lls < length:
        return ls

    return [*ls, *[filler for _ in range(length - lls)]]


def fn(relative_path: str, idx: Optional[int] = None) -> str:
    """
    Given a path, output the same path, relative to the absolute directory path of the file that invoked this function.

    An optional argument `idx` can be supplied to change what script to get the absolute directory path from. Consider the following scenario:

    A helper function in `src/utils/utils` that takes in a relative path as an argument wants to transform the path into one relative to the caller's path. However, the said function needs to call this function directly. Said function can then use an index of `2` so that the given path to this function will be processed to be relative from the caller's path, not from the funciton in `src/utils/utils`.

    Args:
    - relative_path (`str`): Path to output relative to the caller's path.
    - idx (`Optional[int]`, optional): Index of the stack to relativize the path from. Defaults to `1`.

    Returns:
    `str`: Path relative to the caller's path.
    """
    if idx is None:
        idx = 1
    return os.path.normpath(
        os.path.join(os.path.dirname(inspect.stack()[idx][1]), relative_path),
    )


def half_round(n: float | int) -> int:
    """
    Given a number, half it, then round it to nearest ones place.

    Args:
    - n (`float | int`): number to half and round.

    Returns:
    `int`: half and rounded number.
    """

    return round(n / 2)


def inmd(fp: str, ls: Optional[list[str]] = None) -> str:
    """
    If given file path is not a directory, make one of the same name.

    Args:
    - fp (`str`): File path to check if it is a directory, and if not, to make one of the same name.
    - ls (`Optional[list[str]]`, optional): A list of string to which this function can append the file path to if the given file path is not a directory. Defaults to `None`.

    Returns:
    `str`: Given filepath.
    """

    pd = os.path.dirname(fp)
    if (pd) and (not os.path.isdir(pd)):
        makedirs(pd)
        if ls:
            ls.append(pd)
    return fp


def iter_ls_with_items(
    ls: types.ListAny,
    *items: types.ListAny,
) -> Generator[tuple[Any, ...], None, None]:
    for i in ls:
        yield i, *items


def ivnd(var: Any, de: Any) -> Any:
    """
    "If Var None, Default".

    If `var` is `None`, return `de` else `var`.

    Args:
    - var (`Any`): Variable to check if it is None.
    - de (`Any`): Default value to return if var is None.

    Returns:
    `Any`: `var` if `var` is not None else `de`.
    """
    if var is None:
        return de
    return var


def le(expr: str) -> Any:
    """
    Literal Evaluation.

    Args:
    - expr (`str`): Expression to be evaluated.

    Returns:
    `Any`: Expression literally evaluated.
    """
    if expr is not None:
        return ast.literal_eval(expr)


def noop(*args: types.ListAny, **kwargs: dict[str, Any]) -> None:
    """No operation."""


def noop_single_kwargs(arg: Any) -> Any:
    return arg


def repl(s: str, repl_dict: dict[str, list[str]]) -> str:
    """
    Iterate through the dictionary, find the values in the given string and replace it with the corresponding key, and output the modified string.

    Args:
    - s (`str`): String to modify the contents of.
    - repl_dict (`dict[str, list[str]]`): Key-value pairs of string to replace the substring with and list of string to replace with the corresponding key.

    Returns:
    `str`: Modified string.
    """
    op = s
    for k, v in repl_dict.items():
        if v:
            for i in v:
                op = op.replace(i, k)
    return op


def rfnn(*args: types.ListAny) -> Any:
    """
    Return First Non-None.

    Return the first argument that is not `None`, else return `None`.

    Returns:
    `Any`: The first argument that is not `None`, else `None`.
    """
    for i in args:
        if i is not None:
            return i


def run_cmd(cmd: str) -> None:
    """
    Given a string, execute it as a shell command.

    Args:
    - cmd (`str`): Shell command to excute.
    """
    call(shlex.split(cmd))


def run_mp(func: types.CallableAny, iterable: types.IterAny) -> types.ListAny:
    with Pool() as pool:
        return pool.map(func, iterable)


def run_mp_star(func: types.CallableAny, iterable: types.IterIterAny) -> types.ListAny:
    with Pool() as pool:
        return pool.starmap(func, iterable)


def run_mp_qir(
    func: types.CallableAny,
    iterable: types.IterAny,
    callback: types.CallableAny,
) -> None:
    """
    Run `multiprocessing.Pool().map_async()`, and quit in return.

    Iterate over `iterable` and apply iterated item to `func` asynchronously. Wait for a single process in the pool to return, and terminate the pool.

    This function requires the given function to return a bool, or an iterable with its first item as a bool. This bool is then used to decide whether to trigger the callback and terminate the pool.
    """
    if callback is None:
        callback = noop
    with Pool() as pool:
        for i in iterable:
            pool.apply_async(
                func,
                args=(i,),
                callback=PoolTerminate(pool, callback).inner,
            )
        pool.close()
        pool.join()


def run_mp_star_qir(
    func: types.CallableAny,
    iterable: types.IterIterAny,
    callback: types.CallableAny,
) -> None:
    """
    Run `multiprocessing.Pool().starmap_async()`, and quit in return.

    Iterate over `iterable` and apply iterated items to `func` asynchronously. Wait for a single process in the pool to return, and terminate the pool.
    """
    if callback is None:
        callback = noop
    with Pool() as pool:
        for i in iterable:
            pool.apply_async(func, args=i, callback=PoolTerminate(pool, callback).inner)
        pool.close()
        pool.join()


def run_mp_qgr(func: types.CallableAny, iterable: types.IterAny) -> types.TupleAny:
    res_cb = CallbackGetResult()
    run_mp_qir(func, iterable, res_cb.callback)
    return res_cb.get()


def run_mp_star_qgr(
    func: types.CallableAny,
    iterable: types.IterIterAny,
) -> types.TupleAny:
    res_cb = CallbackGetResult()
    run_mp_star_qir(func, iterable, res_cb.callback)
    return res_cb.get()


def sanitize_text(s: str) -> str:
    """
    Sanitize input text.

    Reference: https://stackoverflow.com/a/93029

    Args:
    - s (`str`): Text to be sanitized.

    Returns:
    `str`: Sanitized text.
    """
    return unicodedata.normalize("NFKD", CCHARS_RE.sub("", s)).strip()


def squery(
    query: str,
    possibilities: list[str],
    cutoff: int | float = 0.6,
    *,
    processor: Callable[[Any], Any] = lambda x: x,
) -> Generator[tuple[None, str] | tuple[float, str], None, None]:
    """
    Custom search query.

    Args:
    - query (`str`): String to search for in the possibilities.
    - possibilities (`list[str]`): The possibilities to search from.
    - cutoff (`int | float`, optional): The minimum percentage of similarity from the given possibilities. Defaults to `0.6`.
    - processor (`Callable[[Any], Any]`, optional): Processes the possibilities before comparing it with the query. Defaults to `lambda x: x`.

    Returns:
    `Generator[tuple[None, str] | tuple[float, str], None, None]`: Generator object of mastching search quries.
    """

    sequence_matcher = difflib.SequenceMatcher()
    sequence_matcher.set_seq2(query)

    for search_value in possibilities:
        sequence_matcher.set_seq1(processor(search_value))
        if query.lower() in processor(search_value).lower():
            yield (None, search_value)
            continue
        if (
            sequence_matcher.real_quick_ratio() >= cutoff
            and sequence_matcher.quick_ratio() >= cutoff
            and sequence_matcher.ratio() >= cutoff
        ):
            yield (sequence_matcher.ratio(), search_value)


def str2int(num: int | str) -> Optional[int]:
    """
    If given number is int, return it. Else, if given number is string and is decimal, convert string to integer. Otherwise, return None.

    Args:
        s (int | str): int or string to convert to integer.

    Returns:
        Optional[int]: If given argument can be converted to integer, it will be returned. Otherwise, None will be.
    """
    if isinstance(num, int):
        return num
    if (len(num) != 0) and (num[0] in ("-", "+")) and (num[1:].isdecimal()):
        return int(num)
    if num.isdecimal():
        return int(num)
    return None


def vls_str(vls: list[str | int] | list[int] | list[str]) -> list[str]:
    """
    Given the list of version numbers, convert them to their string representation both in modified semver form and semver-compliant form.

    Args:
    - vls (`list[str | int]`): List of version numbers.

    Returns:
    `list[str]`: List of string representation of given list of version numbers, both in modified semver form and semver-compliant form.
    """
    pr = ""
    ivls = [int(i) for i in vls]
    if ivls[4] < 3:
        pr = f"-{PR[ivls[4]]}.{ivls[5]}"
    return [
        ".".join([str(i) for i in ivls[0:4]]) + pr,
        ".".join([str(i) for i in [*ivls[0:2], 3 ** ivls[2] * 2 ** ivls[3]]]) + pr,
    ]


def which_ls(
    cmd: str,
    mode: Optional[int] = None,
    path: Optional[str] = None,
) -> Optional[types.TupleStr]:
    """
    Given a command, mode, and a PATH string, return the path which conforms to the given mode on the PATH, or None if there is no such file. Yoinked from shutil.

    Args:
        mode (Optional[int], optional): File mode to look for. Defaults to `os.F_OK | os.X_OK`.
        path (Optional[str], optional): Path to search the command at. Defaults to the result of os.environ.get("PATH").

    Returns:
        Optional[types.TupleStr]: Tuple of commands that conforms to the given arguments as said above.
    """

    if mode is None:
        mode = os.F_OK | os.X_OK

    # If we're given a path with a directory part, look it up directly rather
    # than referring to PATH directories. This includes checking relative to the
    # current directory, e.g. ./script
    if os.path.dirname(cmd):
        if shutil._access_check(cmd, mode):
            return (cmd,)
        return None

    if path is None:
        path = os.environ.get("PATH", None)
        if path is None:
            try:
                path = os.confstr("CS_PATH")
            except (AttributeError, ValueError):
                # os.confstr() or CS_PATH is not available
                path = os.defpath
        # bpo-35755: Don't use os.defpath if the PATH environment variable is
        # set to an empty string

    # PATH='' doesn't match, whereas PATH=':' looks in the current directory
    if not path:
        return None

    path = os.fsdecode(path).split(os.pathsep)  # type: ignore[assignment]

    if PSH == "win":
        curdir = os.curdir
        if curdir not in path:
            path.insert(0, curdir)

        # PATHEXT is necessary to check on Windows.
        pathext_source = os.getenv("PATHEXT") or shutil._WIN_DEFAULT_PATHEXT
        pathext = [ext for ext in pathext_source.split(os.pathsep) if ext]

        # See if the given file matches any of the expected path extensions.
        # This will allow us to short circuit when given "python.exe".
        # If it does match, only test that one, otherwise we have to try
        # others.
        if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
            files = [cmd]
        else:
            files = [cmd + ext for ext in pathext]
    else:
        # On other platforms you don't have things like PATHEXT to tell you
        # what file suffixes are executable, so just pass on cmd as-is.
        files = [cmd]

    seen = set()
    op = set()
    for dir in path:
        normdir = os.path.normcase(dir)
        if normdir not in seen:
            seen.add(normdir)
            for thefile in files:
                name = os.path.join(dir, thefile)
                if shutil._access_check(name, mode):
                    op.add(name)
    return tuple(op)


def yaml_str_presenter(dumper, data):  # type: ignore[no-untyped-def]
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)
