---
title: whinesnips.cd
---

# **[whinesnips](README.md).[cd](cd.md)**

## Rationale

Well... I kinda' do some web scraping here and there, and this thing's real useful.

## Disclaimer

Let it be known that to this day, I am still trying to document the shittiness of this module.

Good Lord, have mercy on me huhuuuuu

## Usage

### Initialization

- Import the module.

    ```python
    from ${project_name}.cd import CustomDict
    ```

- Initialize empty dictionary...

    ```python
    test = cd.CustomDict()
    ```

    ```python
    print(test) # {}
    ```

    or from an existing dictionary

    ```python
    test = cd.CustomDict({"a": 1, "b": 2})
    ```

    ```python
    print(test) # {"a": 1, "b": 2}
    ```

### Insertion

- You can do it the old-fashioned way...

    ```python
    test = cd.CustomDict({"a": 1, "b": 2})
    ```

    ```python
    test["c"] = 3
    ```

    Or you can use the `insert` method

    ```python
    test.insert("c", 3)
    ```

    Both methods yield the same results

    ```python
    print(test["c"]) # 3
    ```

- You can also use a path-like string to insert a value.

    ```python
    test = cd.CustomDict({"a": {}})
    test.insert("a/b/c", 3)
    ```

    ```python
    print(test) # {"a": {"b": {"c": 3}}}
    ```

    Yes, it created the keys when they are non-existent. You probably would not want this, but I certainly do. Adding a flag to disable this behavior will only add complexity to it. And, this is my library of snippets to begin with, so just deal with it.

    No one would even probably read this, other than the author itself.

- When the path's value is a list, it will append the given value to the list.

    ```python
    test = cd.CustomDict({"a": [1, 2, 3]})
    test.insert("a/b/c", 4)
    ```

    ```python
    print(test) # {"a": [1, 2, 3, 4]}
    ```

### Getting Values

- You can do it the old-fashioned way...

    ```python
    test = cd.CustomDict({"a": 1, "b": 2})
    ```

    ```python
    print(test["a"]) # 1
    ```

    Or you can use the `dir` method

    ```python
    print(test.dir("a")) # 1
    ```

- You can also use a path-like string to get a value.

    ```python
    test = cd.CustomDict({"a": {"b": {"c": 3}}})
    ```

    ```python
    print(test.dir("a/b/c")) # 3
    ```

- The `dir` method will also return a `CustomDict` object if the value is a dictionary.

Well, that's a really rudimentary way to document it, but it works for me, and that is all that matters.

## How It Works

Hereunder mermaid graphs that explains how the logic of each functions in the class `CustomDict` works.

## traverse

```mermaid
%% id_tag
flowchart LR
    q[[A]] --> n
    args[/path, value/] --> d["elem = self"] --> n["key = path[0]<br>ls_idx = int(key)"] --> a{elem isDict?}
        a --> |no| g{elem is Sized?}
                g ------> |no| l(["CDEA.TypeError.CurrentElementNotDictListOrTuple"]):::error
                g --> |yes| h{"key not empty?"}
                    h ------> |no| m(["CDEA.IndexError.EmptyString"]):::error
                    h --> |yes| o{key is int?}
                        o ------> |no| p(["CDEA.IndexError.NotInteger"]):::error
                        o --> |yes| i{key in range?}
                        i -----> |no| w["(2, {'idx': idx, 'ls_idx': ls_idx, 'len_iter': len_iter})"]:::success
                        i --> |yes| c
        a --> |yes| e{"(key not in elem)<br>and<br>(ls_idx is valid)?"}
            e --> |no| b
                b --> |yes| c{path fully<br>traversed?}
                    c --> |no| y["elem = elem[key]<br>path = path[1:]"]:::success --> j[[A]]
                    c --> |yes| x["(0, {'value': typed_elem[key], ...})"]:::success
                b -----> |no| f["(1, {'idx': idx})"]:::success
            e --> |yes| k[key = ls_idx] --> b{key in<br>elem}

subgraph Sized
h;o;i
end

subgraph dict
e;k;b
end

subgraph returns
w;x;f
end

subgraph raises
l;m;p
end

    classDef success color:#83ce9e,stroke:#6fc890
    classDef error color:#f3626b,stroke:#f14652
```

## dir

```mermaid
flowchart LR
    args[/path, de/] --> a{path is None?}
        a --> |yes| b[/self/]:::success
        a --> |no| c{path == '' ?}
            c --> |yes| d{'' in self?}
                d -----> |no| b
                d -----> |yes| e[/"self['']"/]:::success
            c --> |no| f[["state, op = traverse(path)"]]

    f --> g{state == 0?}
        g ----> |yes| h[/"op[value]"/]:::success

    g --> |no| i{state == 1?}
        i --> |yes| j{de is not None?}
            j --> |yes| k[/"de"/]:::success
            j --> |no| l(["CDEA.KeyError.NotInElement"]):::error

    i --> |no| m{state == 2?}
        m --> |yes| n(["CDEA.IndexError.OutOfRange"]):::error

    m --> |no| o(["CDEI.StateUnexpected"]):::error

subgraph returns
b;e;h;k
end

subgraph raises
l;n;o
end

classDef success color:#83ce9e,stroke:#6fc890
classDef error color:#f3626b,stroke:#f14652
```

## modify

```mermaid
flowchart LR
    args[/path, value/] --> a{path is None?}
        a --> |yes| b[self]:::success
        a --> |no| c{value is None?}
            c --> |yes| b
            c --> |no| d[["state, op = traverse(path)"]]

    d --> e{state == 0?}
        e --> |yes| f["last_key = path.pop()<br>idx = 0<br>current = self"] -->
        j{path fully<br>traversed?}
        j --> |yes| l["current[last_key] = value"] --> b
        j -->
        |no| h["idx += 1<br>key = path[idx]<br>current = current[key]"] --> j

    e --> |no| m{state == 1?}
        m ----> |yes| n(["CDEA.KeyError.NotInElement"]):::error

    m --> |no| o{state == 2?}
        o ---> |yes| p(["CDEA.IndexError.OutOfRange"]):::error

    o ---> |no| q(["CDEI.StateUnexpected"]):::error


subgraph returns
b
end

subgraph raises
n;p;q
end

classDef success color:#83ce9e,stroke:#6fc890
classDef error color:#f3626b,stroke:#f14652
```

## insert

```mermaid
%% id_tag
flowchart TD
    args[/path, value/]
    args --> a["*path, last_key = path.split(sep)<br>lk_ls_idx = whsn.utils.utils.str2int(last_key)"]
    a --> b{"path_ls not empty?"}
        b --> |yes| c["path = sep.join(path_ls)<br>state, op = self.traverse(path)<br>keys = op['key_type_kv'].keys()<br>second_last_key = keys.pop()"]
            l --> |yes| m([CDEA.TypeError.CurrentElementNotListOrTuple]):::error
            d --> |no| ad{state == 1?}
                ad --------> |yes| ae([CDEA.KeyError.NotInElement]):::error
                ad --> |no| af{state == 2?}
                    af -------> |yes| ag([CDEA.IndexError.OutOfRange]):::error
                    af -------> |no| ai([CDEI.StateUnexpected]):::error
            c --> d{state == 0?}
                d --> |yes| i["iter_idx=0"]
                    i --> j{keys fully iterated?}
                        j --> |yes| r{"is the second<br>last item a dict?"}
                        j --> |no| k["current = current[iter_idx]<br>iter_idx += 1"] --> j
                            r --> |no| w{"is the second last<br>item a Sized iterable?"}
                                w --> |yes| x{"is last_key empty?"}
                                    x ----> |yes| y([CDEA.IndexError.EmptyString]):::error
                                    x --> |no| z{"is last_key None?"}
                                        z ---> |yes| aa([CDEA.IndexError.NotInteger]):::error
                                        z --> |no| ab["current[second_last_key] = value"] --> q
                            r --> |yes| s{strict?}
                                s --> |yes| m
                                s --> |no| t{"is (last_key not in current)<br>and<br>(lk_ls_idx is not None)"}
                                    t --> |yes| u["last_key = lk_ls_idx"] --> v
                                    t --> |no| v["current[second_last_key][last_key] = value"] --> q
        b --> |no| l{strict?}
            l --> |no| n{"is (last_key not in current)<br>and<br>(lk_ls_idx is not None)"}
                n --> |yes| o[last_key = lk_ls_idx] --> p
                n --> |no| p["current[last_key] = value"]
                    p --> q[self]:::success

subgraph returns
    q
end

subgraph raises
    m;y;aa;ae;ag;ai
end

    classDef success color:#83ce9e,stroke:#6fc890
    classDef error color:#f3626b,stroke:#f14652
```


<h3><b><a href="#func" id="func">Functions</a></b></h3>

    

    
<h3><b><i><a href="#func-flatten_element" id="func-flatten_element">flatten_element</a></i></b></h3>

```python
(elem: dict[int, typing.Any] | dict[str, typing.Any] | dict[int | str, typing.Any] | list[tuple[int | str, typing.Any]], sep: str = '/') ‑> whinesnips.cd.CustomDict
```

    

    
<h3><b><a href="#class" id="class">Classes</a></b></h3>

    
<h3><b><i><a href="#class-BEHAVIOR" id="class-BEHAVIOR">BEHAVIOR</a></i></b></h3>

```python
(*args, **kwds)
```

    
Create a collection of name/value pairs.

Example enumeration:

>>> class Color(Enum):
...     RED = 1
...     BLUE = 2
...     GREEN = 3

Access them by:

- attribute access::

>>> Color.RED
<Color.RED: 1>

- value lookup:

>>> Color(1)
<Color.RED: 1>

- name lookup:

>>> Color['RED']
<Color.RED: 1>

Enumerations can be iterated over, and know how many members they have:

>>> len(Color)
3

>>> list(Color)
[<Color.RED: 1>, <Color.BLUE: 2>, <Color.GREEN: 3>]

Methods can be added to enumerations, and members can have their own
attributes -- see the documentation for details.

    
<h3><a href="#class-BEHAVIOR-mro" id="class-BEHAVIOR-mro">Ancestors (in MRO)</a></h3>

* enum.Enum

    
<h3><a href="#class-BEHAVIOR-cvar" id="class-BEHAVIOR-cvar">Class variables</a></h3>

    
`append`

    
`insert`

    
`modify`

    
<h3><b><i><a href="#class-CustomDict" id="class-CustomDict">CustomDict</a></i></b></h3>

```python
(*args: dict[int, typing.Any] | dict[str, typing.Any] | dict[int | str, typing.Any] | list[tuple[int | str, typing.Any]], **kwargs: dict[str, typing.Any])
```

    
Custom dictionary.

    
<h3><a href="#class-CustomDict-mro" id="class-CustomDict-mro">Ancestors (in MRO)</a></h3>

* builtins.dict

    
<h3><a href="#class-CustomDict-func" id="class-CustomDict-func">Methods</a></h3>

    

    
<h3><i><a href="#class-CustomDict-func-append" id="class-CustomDict-func-append">append</a></i></h3>

```python
(self, path: str = 'c0VjUmVUX2NPZEUgYnkgd2hpX25l', value: Any = 'c0VjUmVUX2NPZEUgYnkgd2hpX25l', sep: str = '/') ‑> whinesnips.cd.CustomDict
```

    

    

    
<h3><i><a href="#class-CustomDict-func-dir" id="class-CustomDict-func-dir">dir</a></i></h3>

```python
(self, path: str = 'c0VjUmVUX2NPZEUgYnkgd2hpX25l', de: Any = 'c0VjUmVUX2NPZEUgYnkgd2hpX25l', sep: str = '/') ‑> Any
```

    

    

    
<h3><i><a href="#class-CustomDict-func-flatten" id="class-CustomDict-func-flatten">flatten</a></i></h3>

```python
(self, path: str = 'c0VjUmVUX2NPZEUgYnkgd2hpX25l', sep: str = '/', flat_sep: str = '/') ‑> whinesnips.cd.CustomDict
```

    

    

    
<h3><i><a href="#class-CustomDict-func-insert" id="class-CustomDict-func-insert">insert</a></i></h3>

```python
(self, path: str = 'c0VjUmVUX2NPZEUgYnkgd2hpX25l', value: Any = 'c0VjUmVUX2NPZEUgYnkgd2hpX25l', sep: str = '/', strict: bool = True) ‑> whinesnips.cd.CustomDict
```

    

    

    
<h3><i><a href="#class-CustomDict-func-modify" id="class-CustomDict-func-modify">modify</a></i></h3>

```python
(self, path: str = 'c0VjUmVUX2NPZEUgYnkgd2hpX25l', value: Any = 'c0VjUmVUX2NPZEUgYnkgd2hpX25l', sep: str = '/') ‑> whinesnips.cd.CustomDict
```

    

    

    
<h3><i><a href="#class-CustomDict-func-traverse" id="class-CustomDict-func-traverse">traverse</a></i></h3>

```python
(self, path: str, sep: str) ‑> tuple[int, dict[str, typing.Any]]
```

    
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

    
<h8><b><a href="#class-CustomDict-func-traverse-args" id="class-CustomDict-func-traverse-args">Args:</a></b></h8>

    path (str): Path to traverse.
    sep (str): Seperator of the path for individual indexes.

    
<h8><b><a href="#class-CustomDict-func-traverse-raises" id="class-CustomDict-func-traverse-raises">Raises:</a></b></h8>

    CDExceptions.API.IndexError.EmptyString:
    Raised when the currently traversed element is a list or tuple,
    and the current key is an empty string.
    CDExceptions.API.IndexError.NotInteger:
    Raised when the currently traversed element is a list or tuple,
    and the current key is not a valid integer.
    CDExceptions.API.TypeError.CurrentElementNotDictListOrTuple:
    Raised when the currently traversed element is not the last element
    to index and is not a dict, list, or tuple.

    
<h8><b><a href="#class-CustomDict-func-traverse-returns" id="class-CustomDict-func-traverse-returns">Returns:</a></b></h8>

    tuple[int, dict[str, int]]: _description_