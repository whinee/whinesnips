---
title: 'whinesnips.

  utils.cfg'
---

# **[whinesnips](../README.md).[utils](../utils.md).[cfg](cfg.md)**

<h3><b><a href="#func" id="func">Functions</a></b></h3>

    

    
<h3><b><i><a href="#func-dcfg" id="func-dcfg">dcfg</a></i></b></h3>

```python
(value: dict[str, typing.Any], ext: str) ‑> str
```

    
Dump the given value to a string with the given extension.

    
<h3><i><a href="#func-dcfg-args" id="func-dcfg-args">Args:</a></i></h3>

- value (`dict`): Value to dump to a string.
- ext (`str`): Extension to dump the value to.

    
<h3><i><a href="#func-dcfg-returns" id="func-dcfg-returns">Returns:</a></i></h3>

`str`: The dumped value.

    

    
<h3><b><i><a href="#func-pcfg" id="func-pcfg">pcfg</a></i></b></h3>

```python
(d: str, type: str) ‑> dict[typing.Any, typing.Any]
```

    
Parse the given string as the given type.

    
<h3><i><a href="#func-pcfg-args" id="func-pcfg-args">Args:</a></i></h3>

- d (`str`): String to parse.
- type (`str`): Type to parse the string as.

    
<h3><i><a href="#func-pcfg-returns" id="func-pcfg-returns">Returns:</a></i></h3>

`dict`: The parsed string.

    

    
<h3><b><i><a href="#func-rcfg" id="func-rcfg">rcfg</a></i></b></h3>

```python
(file: str) ‑> dict[typing.Any, typing.Any]
```

    
Read the contents of a file with the given file name.

    
<h3><i><a href="#func-rcfg-args" id="func-rcfg-args">Args:</a></i></h3>

- file (`str`): File name of the file to read the contents of.

    
<h3><i><a href="#func-rcfg-returns" id="func-rcfg-returns">Returns:</a></i></h3>

`dict`: The contents of the file.

    

    
<h3><b><i><a href="#func-wcfg" id="func-wcfg">wcfg</a></i></b></h3>

```python
(file: str, value: dict[typing.Any, typing.Any] | list[typing.Any]) ‑> None
```

    
Write the given value to a file with the given file name.

    
<h3><i><a href="#func-wcfg-args" id="func-wcfg-args">Args:</a></i></h3>

- file (`str`): File name of the file to write the value to.
- value (`dict[Any, Any] | list[Any])`: Value to write to the file.