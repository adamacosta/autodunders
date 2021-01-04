"""
Attach common boilerplate code to classes automatically.

This module exports two primary functions, add_dunders and add_dunders_to_module.
The first is intended to be used as a class decorator in order to select
individual classes to have methods added. The second is passed a module
name and it will (provided that module has been imported) add methods to
all classes in the module, as well as any submodules that are already
imported.

A third function named 'register' is available to add boilerplate functions
to the built in registry, which includes reasonable default implementations
of __eq__ and __repr__. Note that defining __eq__ to override object.__eq__
has the beneficial secondary effect of causing Python to treat your object
as unhashable unless you have also overriden __hash__. This is likely what
you want unless your objects are actually immutable.
"""

import functools
import inspect
import logging
import sys
import types

__all__ = ('add_dunders', 'add_dunders_to_module', 'register')

logger = logging.getLogger(__name__)


def add_dunders(cls_=None, *, dunders=None, callbacks=None):
    """Add the specified methods to a class definition.

    >>> import autodunders
    >>> @autodunders.add_dunders
    ... class Foo:
    ...     def __init__(self):
    ...         self.a = 1
    ...         self.b = 2
    ...
    >>> bar = Foo()
    >>> repr(bar)
    'Foo(a=1, b=2)'
    >>> bar1 = Foo()
    >>> bar == bar1
    True
    """
    def dunder_decorator(cls):
        def add_dunders_to_class():
            nonlocal dunders, callbacks
            if dunders is None:
                dunders = ('__repr__', '__eq__')
            if callbacks is None:
                callbacks = _dunders_to_funcs
            for dunder in dunders:
                logger.info(f'Adding {dunder} to {cls.__name__}')
                setattr(cls, dunder, callbacks[dunder])
            return cls
        return add_dunders_to_class()
    if cls_ is None:
        return dunder_decorator
    else:
        return dunder_decorator(cls_)


@functools.singledispatch
def add_dunders_to_module(module, dunders=None, callbacks=None, recurse=False):
    """Add the specified methods to all classes in a module.

    >>> class Foo:
    ...     def __init__(self):
    ...         self.a = 1
    ...         self.b = 2
    ...
    >>> bar = Foo()
    >>> import autodunders
    >>> autodunders.add_dunders_to_module(__name__)
    >>> repr(bar)
    'Foo(a=1, b=2)'
    >>> bar1 = Foo()
    >>> bar == bar1
    True
    """
    raise TypeError(module)  # pragma: no cover


@add_dunders_to_module.register  # type: ignore
def _(module: str, dunders=None, callbacks=None, recurse=False):
    add_dunders_to_module(sys.modules[module], dunders=dunders, callbacks=callbacks, recurse=recurse)


@add_dunders_to_module.register  # type: ignore
def _(module: types.ModuleType, dunders=None, callbacks=None, recurse=False):
    if dunders is None:
        dunders = ('__repr__', '__eq__')
    if callbacks is None:
        callbacks = _dunders_to_funcs
    for dunder in dunders:
        _add_to_objects(module, dunder, callbacks, recurse)


def register(name, func):
    """Add callable func to internal registry and map it to name."""
    _dunders_to_funcs[name] = func


def _add_to_objects(module, dunder, callbacks, recurse):
    def pred(obj):
        return inspect.isclass(obj) and getattr(obj, dunder) is getattr(object, dunder)
    for cls in _module_attrs(module, pred, recurse):
        logger.info(f'Adding {dunder} to {cls.__name__}')
        setattr(cls, dunder, callbacks[dunder])


def _module_attrs(module, pred, recurse):
    for obj in module.__dict__.values():
        if pred(obj):
            yield obj
        if recurse and isinstance(obj, types.ModuleType) and obj.__package__ == module:
            yield from _module_attrs(obj, pred, recurse)


def _obj_attrs(obj):
    if hasattr(obj, '__slots__'):
        attrs = obj.__slots__
    else:
        attrs = tuple(obj.__dict__.keys())
    return attrs


def _obj_attr_vals(obj):
    attrs = _obj_attrs(obj)
    return tuple(getattr(obj, attr) for attr in attrs)


def _cls_attrs(obj):
    all_attrs = type(obj).__dict__.keys()
    return tuple((attr for attr in all_attrs if not (attr[:2] == '__' and attr[-2:] == '__')))


def _cls_attr_vals(obj):
    attrs = _cls_attrs(obj)
    return tuple(getattr(type(obj), attr) for attr in attrs)


def autoeq(self, other):
    if not isinstance(other, type(self)):
        return False
    for s, o in zip(_obj_attr_vals(self), _obj_attr_vals(other)):
        if s != o:
            return False
    return True


def autorepr(self):
    ret = type(self).__name__
    ret += '('
    cls_attrs, cls_vals = _cls_attrs(self), _cls_attr_vals(self)
    obj_attrs, obj_vals = _obj_attrs(self), _obj_attr_vals(self)
    combined_dict = dict(zip(cls_attrs, cls_vals))
    combined_dict.update(dict(zip(obj_attrs, obj_vals)))
    ret += ', '.join([f'{attr}={val}' for attr, val in combined_dict.items()])
    ret += ')'
    return ret


_dunders_to_funcs = {
    '__eq__': autoeq,
    '__repr__': autorepr
}
