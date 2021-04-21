from typing import Any, Union, Iterable
from src import language
from bidict import bidict
import typing

# types
TYPE_BINDING = typing.Union[typing.Mapping[language.Variable, typing.Any], bidict, language.Keyword]
TYPE_BINDING_OPTIONAL = typing.Optional[typing.Union[typing.Mapping[language.Variable, typing.Any], bidict,
                                                     language.Keyword]]
TYPE_BINDINGS = typing.Iterable[typing.Union[typing.Mapping[language.Variable, typing.Any], bidict, language.Keyword]]


def value(var, binding):
    """finds the value of variable in binding, returning FREE if none exists"""
    if not isinstance(var, language.Variable):
        return var
    elif var not in binding:
        return language.FREE

    if isinstance(binding[var], language.Variable):
        return value(binding[var], binding)
    else:
        return binding[var]


# TODO fix occur check
def occur_check(var: language.Variable, val: Union[tuple, language.Logical]) -> bool:
    """whether var occurs in val, because if so we can't unify"""
    return False  # fix later


def unify_variable(var: language.Variable, val: Any, binding: TYPE_BINDING) -> TYPE_BINDING:
    if var in binding:
        return unify(binding[var], val, binding)
    elif val in binding.inverse:
        return unify(var, binding.inverse[val], binding)
    elif occur_check(var, val):
        return language.NO
    else:
        binding[var] = val
        return binding


def unify_term(x: language.Term, y: language.Term, binding: TYPE_BINDING) -> TYPE_BINDING:
    """
    Unifies two compounds, optionally subject to a binding, returning a binding
    """
    if not len(x.args) == len(y.args):
        return language.NO
    else:
        return unify(x.args, y.args, unify(x.op, y.op, binding))


# TODO fix tail unification
def tail(item: tuple) -> bool:
    """
    Figures out whether the tuple is length 1 and ends in a tail variable
    """
    try:
        return isinstance(item[0], language.Tail) and (len(item) == 1)
    except IndexError:
        return False


def unify_tuple(x: tuple, y: tuple, binding: TYPE_BINDING) -> TYPE_BINDING:
    """
    Unifies two tuples, optionally subject to a binding, returning a binding
    """
    if tail(x):
        return unify(x[0].to_var(), y, binding)
    elif tail(y):
        return unify(y[0].to_var(), x, binding)
    elif bool(x) != bool(y):
        return language.NO
    else:
        return unify(x[1:], y[1:], unify(x[0], y[0], binding))


def unify(x: Any, y: Any, binding: TYPE_BINDING_OPTIONAL = None) -> TYPE_BINDING:
    """
    Unifies two objects, optionally subject a binding, and returns the resulting binding
    """

    # language.FAILs get passed up the callstack
    if binding == language.NO:
        return language.NO

    # we might get weird user input formats
    binding = bidict(binding)

    # # we need stuff to be immutable
    x = tuple(x) if isinstance(x, Iterable) and not isinstance(x, str) else x
    y = tuple(y) if isinstance(y, Iterable) and not isinstance(x, str) else y

    # figure out what it is a dispatch the correct unifier function
    if x == y:
        return binding
    elif isinstance(x, language.Variable):
        return unify_variable(x, y, binding)
    elif isinstance(y, language.Variable):
        return unify_variable(y, x, binding)
    elif isinstance(x, language.Term) and isinstance(y, language.Term):
        return unify_term(x, y, binding)
    elif isinstance(x, tuple) and isinstance(y, tuple):
        return unify_tuple(x, y, binding)
    else:
        return language.NO
