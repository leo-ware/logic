from typing import Optional, Any, Union, Iterable
from src import types, language
from bidict import bidict


class Fail:
    pass


def occur_check(var: language.Variable, val: Union[tuple, language.Term]) -> bool:
    """whether var occurs in val, because if so we can't unify"""
    if isinstance(val, tuple):
        return any(occur_check(var, v) for v in val)

    try:
        return var in val
    except TypeError:
        return False


def unify_variable(var: language.Variable, val: Any, binding: bidict) -> types.Binding:
    if var in binding:
        return unify(binding[var], val, binding)
    elif val in binding.inverse:
        return unify(var, binding.inverse[val], binding)
    elif occur_check(var, val):
        return Fail
    else:
        binding[var] = val
        return binding


def unify_compound(x: language.Compound, y: language.Compound, binding: bidict) -> types.Binding:
    """
    Unifies two compounds, optionally subject to a binding, returning a binding
    """
    if not len(x.args) == len(y.args):
        return Fail
    else:
        return unify(x.args, y.args, unify(x.op, y.op, binding))


def tail(item: tuple) -> bool:
    """
    Figures out whether the tuple is length 1 and ends in a tail variable
    """
    try:
        return isinstance(item[0], language.Tail) and (len(item) == 1)
    except IndexError:
        return False


def unify_tuple(x: tuple, y: tuple, binding: types.Binding) -> types.Binding:
    """
    Unifies two tuples, optionally subject to a binding, returning a binding
    """
    if tail(x):
        return unify(x[0].to_var(), y, binding)
    elif tail(y):
        return unify(y[0].to_var(), x, binding)
    elif bool(x) != bool(y):
        return Fail
    else:
        return unify(x[1:], y[1:], unify(x[0], y[0], binding))


def unify(x: Any, y: Any, binding: Optional[types.Binding] = None) -> types.Binding:
    """
    Unifies two objects, optionally subject a binding, and returns the resulting binding
    """

    # Fails get passed up the callstack
    if binding == Fail:
        return Fail

    # we might get weird user input formats
    binding = bidict(binding)

    # we need stuff to be immutable
    x = tuple(x) if isinstance(x, Iterable) and not isinstance(x, str) else x
    y = tuple(y) if isinstance(y, Iterable) and not isinstance(x, str) else y

    # figure out what it is a dispatch the correct unifier function
    if x == y:
        return binding
    elif isinstance(x, language.Variable):
        return unify_variable(x, y, binding)
    elif isinstance(y, language.Variable):
        return unify_variable(y, x, binding)
    elif isinstance(x, language.Compound) and isinstance(y, language.Compound):
        return unify_compound(x, y, binding)
    elif isinstance(x, tuple) and isinstance(y, tuple):
        return unify_tuple(x, y, binding)
    else:
        return Fail
