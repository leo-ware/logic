import typing
import abc
from dataclasses import dataclass

_vid = 1000
"""used in variable renaming"""


def standardize_variables(x: typing.Any, reset=False, _id: typing.Optional[int] = None):
    """Renames all the variables in a term"""
    global _vid

    if _id is None:
        _id = _vid
        _vid += 1

    if reset:
        _id = None

    try:
        return x.standardize(reset, _id)
    except AttributeError:
        return x


def substitute(x: typing.Any, binding):
    """Substitutes provided bindings for variables in term"""
    if binding is None:
        return x

    if isinstance(x, Term):
        return x.substitute(binding)
    elif isinstance(x, tuple):
        return tuple(substitute(y, binding) for y in x)
    else:
        return x


class Term(abc.ABC):
    def __contains__(self, var: "Variable"):
        if isinstance(self, Literal):
            return False

        return (
                (isinstance(self, Variable) and (var == self)) or
                (isinstance(self, Not) and (var in self.term)) or
                (isinstance(self, (Join, Compound)) and
                 (var in self.args or
                  any(var in arg for arg in self.args)))
        )

    def __and__(self, other):
        return And((self, other))

    def __or__(self, other):
        return Or((self, other))

    def __neg__(self):
        return Not(self)

    def __invert__(self):
        return Not(self)

    def __le__(self, body):
        return Rule(self, body)

    def standardize(self, *_, **__):
        return self

    def substitute(self, _):
        return self


class Join(Term, abc.ABC):
    SYM = "JOIN"

    def __init__(self, args: typing.Iterable):
        self.args = self._merge(args)

    def _merge(self, args: typing.Iterable) -> tuple:
        new = []
        for item in args:
            if isinstance(item, self.__class__):
                new.extend(item.args)
            else:
                new.append(item)
        return tuple(new)

    def standardize(self, reset: bool, _id: int):
        return self.__class__(standardize_variables(arg, reset, _id) for arg in self.args)

    def substitute(self, binding):
        return self.__class__(substitute(arg, binding) for arg in self.args)

    @property
    def first(self) -> typing.Any:
        """The first conjunct in the Join, under the assumption that it exists

        Raises:
            IndexError: if the Join is empty
        """
        return self.args[0]

    @property
    def rest(self) -> typing.Any:
        """Returns Join with all conjuncts except the first"""
        return self.__class__(self.args[1:])

    def __bool__(self):
        return bool(self.args)

    def __iter__(self):
        return iter(self.args)

    def __eq__(self, other):
        return (type(self) == type(other)) & (self.args == other.args)

    def __repr__(self):
        return f" {self.__class__.SYM} ".join(i.__repr__() for i in self.args)


class And(Join):
    SYM = "&"


class Or(Join):
    SYM = "|"


@dataclass(frozen=True)
class Not(Term):
    term: Term

    def __repr__(self):
        return "~" + self.term.__repr__()

    def standardize(self, *args, **kwargs):
        return self.term.standardize(*args, **kwargs)

    def substitute(self, binding):
        return self.term.substitute(binding)


@dataclass(frozen=True)
class Compound(Term):
    """Term used for representing logical sentences

    Compounds have a name and a list of arguments, and they are used for
    representing logical sentences. Example: you could represent the prolog
    sentence `sibling(leo, milo)` with `Compound("sibling", ["leo", "milo"])`
    """
    op: str
    args: tuple

    def __repr__(self):
        return self.op + "(" + ", ".join(str(arg) for arg in self.args) + ")"

    def standardize(self, reset: bool, _id: int) -> "Compound":
        return Compound(
            op=standardize_variables(self.op, reset, _id),
            args=tuple(standardize_variables(arg, reset, _id) for arg in self.args)
        )

    def substitute(self, binding) -> "Compound":
        return Compound(
            op=substitute(self.op, binding),
            args=tuple(substitute(arg, binding) for arg in self.args)
        )


def functor(name: str, arity: typing.Optional[int] = None) -> typing.Callable:
    """Returns a function for making compounds

    A functor is an operation on terms, e.g. "sibling" or "father". It is a function
    mapping from arguments from arguments to compounds (sentences). This function
    creates functors with a given name and (optionally) arity.

    If arity is provided, it will be used to perform arity checks when the functor
    is called.
    """

    def make_compound(*args: typing.Iterable[typing.Any]) -> Compound:
        if (arity is not None) and (len(args) != arity):
            raise ValueError("wrong arity")
        return Compound(name, args)

    return make_compound


@dataclass(frozen=True)
class Literal(Term):
    """Immutable class corresponding to prolog's Atom

    Using a Literal with some name is functionally equivalent to just straitup using
    the name (they are even `__eq__`ual), but these support infix operations
    """
    name: str

    # make it interchangeable with str
    def __eq__(self, other):
        return self.name == other

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name


@dataclass(frozen=True)
class Variable(Term):
    name: str
    _id: typing.Optional[int] = None

    def __pos__(self) -> "Tail":
        return Tail(self.name, self._id)

    def __repr__(self):
        if self._id:
            return f"{self.name}_{self._id}"
        else:
            return self.name

    def standardize(self, reset: bool, _id: int) -> "Variable":
        return Variable(self.name, _id if not reset else None)

    def substitute(self, binding) -> "Variable":
        if self in binding:
            return binding[self]
        else:
            return self


def variables(s):
    """takes an iterable of strings (inc. a string) and returns a tuple of variables created with them

    nice function to create a bunch of variables in one call
    """
    return tuple(Variable(c) for c in s)


@dataclass(frozen=True)
class Tail:
    """Variable-like class used for tail unification

    These can be created using the unary "+" on variables. This is equivalent to the prolog "|".
    Best explained with an example: the prolog `X = [H | T]` and the python `unify(X, [H, +T])`
    represent the same thing.
    """
    name: str
    _id: typing.Optional[int] = None

    def __repr__(self):
        return "+" + self.name

    def standardize(self, _id: int, reset: bool) -> "Tail":
        return Tail(self.name, _id if not reset else None)

    def to_var(self) -> Variable:
        return Variable(self.name, self._id)


class Rule:
    def __init__(self, head: Term, body: Term) -> None:
        if not isinstance(body, (tuple, And)):
            body = [body]

        self.head = head
        self.body = And(body)

    def standardize(self, reset: bool, _id: int) -> "Rule":
        return Rule(standardize_variables(self.head, reset=reset, _id=_id),
                    standardize_variables(self.body, reset=reset, _id=_id))

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return all([
            type(self) == type(other),
            self.head == other.head,
            self.body == other.body
        ])

    def __repr__(self) -> str:
        return f"{self.head} <= {self.body}"


@dataclass(frozen=True)
class Keyword:
    name: str

    def __repr__(self):
        return self.name


CUT = Keyword("CUT")
FAIL = Keyword("FAIL")
