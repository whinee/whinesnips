---
title: 'whinesnips.

  utils.base_exc'
---

# **[whinesnips](../README.md).[utils](../utils.md).[base_exc](base_exc.md)**

<h3><b><a href="#func" id="func">Functions</a></b></h3>

    

    
<h3><b><i><a href="#func-c_exc" id="func-c_exc">c_exc</a></i></b></h3>

```python
(cls: type[BaseException]) ‑> type[BaseException]
```

    
Decorator to raise a custom exception.

This function gives the class an __init__ function that raises the exception.
If the class does not inherit from any Exception, it will be automatically inherit from Exception.
This function also wraps the Exception with `c_exc_str` method, for adding the `__str__` method.

    
<h3><i><a href="#func-c_exc-args" id="func-c_exc-args">Args:</a></i></h3>

- cls (`BaseException | Object`): The exception to modify.

    
<h3><i><a href="#func-c_exc-returns" id="func-c_exc-returns">Returns:</a></i></h3>

`BaseException`: The exception to raise.

    

    
<h3><b><i><a href="#func-c_exc_str" id="func-c_exc_str">c_exc_str</a></i></b></h3>

```python
(cls: type[BaseException]) ‑> type[BaseException]
```

    
Decorator to add the __str__ method to an exception.

    
<h3><i><a href="#func-c_exc_str-args" id="func-c_exc_str-args">Args:</a></i></h3>

- cls (`BaseException`): The exception to add the __str__ method to.

    
<h3><i><a href="#func-c_exc_str-returns" id="func-c_exc_str-returns">Returns:</a></i></h3>

`BaseException`: The exception to raise.

    

    
<h3><b><i><a href="#func-custom_exception_hook" id="func-custom_exception_hook">custom_exception_hook</a></i></b></h3>

```python
(exctype: type[BaseException], value: BaseException, traceback: Optional[traceback]) ‑> None
```