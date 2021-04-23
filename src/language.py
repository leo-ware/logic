import typing
import abc
from dataclasses import dataclass, replace

_vid = 1000
"""used in variable renaming"""


def variables_in(x: "Logical"):
    vs = set()

    def _report_variables_in(thing):
        if isinstance(thing, Variable):
            vs.add(thing)
        return thing

    if isinstance(x, Logical):
        x.map(_report_variables_in)

    return vs


def standardize(x: typing.Union["Rule", "Logical"], reset: bool = False):
    """Renames all the variables in a term"""
    global _vid

    if reset:
        _id = None
    else:
        _id = _vid
        _vid += 1

    def _do_standardize(_x):
        if isinstance(_x, Variable):
            return replace(_x, _id=_id)
        return _x

    return x.map(_do_standardize)


def substitute(x: typing.Union["Rule", "Logical"], binding):
    """Substitutes provided bindings for variables in term"""
    def _do_substitute(_x):
        if _x in binding:
            return binding[_x]
        return _x
    return x.map(_do_substitute)


class Logical(abc.ABC):

    def __and__(self, other):
        return And((self, other))

    def __or__(self, other):
        return Or((self, other))

    def __neg__(self):
        return Not(self)

    def __invert__(self):
        return Not(self)

    @abc.abstractmethod
    def map(self, func):
        """Apply func to every non Logical child and map func onto every Logical one"""
        pass


class Join(Logical, abc.ABC):
    SYM = "JOIN"
    EMPTY = "JOIN"

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

    def map(self, func):
        return self.__class__(arg.map(func) if isinstance(arg, Logical) else func(arg) for arg in self.args)

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

    def __hash__(self):
        return hash(self.args)

    def __bool__(self):
        return bool(self.args)

    def __iter__(self):
        return iter(self.args)

    def __eq__(self, other):
        return (type(self) == type(other)) and (self.args == other.args)

    def __repr__(self):
        if len(self.args) > 1:
            return f" {self.__class__.SYM} ".join(i.__repr__() for i in self.args)
        elif self:
            return f"<And {self.first}>"
        else:
            return self.__class__.EMPTY


class And(Join):
    SYM = "&"
    EMPTY = "YES"


class Or(Join):
    SYM = "|"
    EMPTY = "NO"


YES = And([])
NO = Or([])


@dataclass(frozen=True)
class Keyword(Logical):
    name: str

    def __repr__(self):
        return self.name

    def map(self, func):
        return func(self)


CUT = Keyword("CUT")
FREE = Keyword("FREE")


@dataclass(frozen=True)
class Not(Logical):
    item: Logical

    def __repr__(self):
        return "~" + self.item.__repr__()

    def map(self, func):
        return Not(self.item.map(func))


@dataclass(frozen=True)
class Term(Logical):
    """The datatype for representing logical claims

    Terms have a name and (optionally) a list of arguments, and they are used for
    representing logical sentences. Example: you could represent the prolog
    sentence `sibling(leo, milo)` with `Term("sibling", ["leo", "milo"])`

    Attributes:
        op - the functor, a string
        args - tuple of arguments (terms or strings)
    """
    op: str
    args: tuple = ()

    def __repr__(self):
        if self.args:
            return self.op + "(" + ", ".join(str(arg) for arg in self.args) + ")"
        else:
            return self.op

    def __le__(self, other: Logical) -> "Rule":
        return Rule(self, other)

    def map(self, func):
        return Term(self.op, tuple(func(arg) for arg in self.args))


def functor(name: str, arity: typing.Optional[int] = None) -> typing.Callable:
    """Returns a function for making compounds

    A functor is an operation on terms, e.g. "sibling" or "father". It is a function
    mapping from arguments from arguments to compounds (sentences). This function
    creates functors with a given name and (optionally) arity.

    If arity is provided, it will be used to perform arity checks when the functor
    is called.
    """

    def make_term(*args: typing.Iterable[typing.Any]) -> Term:
        if (arity is not None) and (len(args) != arity):
            raise ValueError("wrong arity")
        return Term(name, args)

    return make_term


@dataclass(frozen=True)
class Variable(Logical):
    name: str
    _id: typing.Optional[int] = None

    def __pos__(self) -> "Tail":
        return Tail(self.name, self._id)

    def __repr__(self):
        if self._id:
            return f"{self.name}_{self._id}"
        else:
            return self.name

    def to_var(self):
        return Variable(self.name, self._id)

    def map(self, func):
        return func(self)


def variables(s):
    """takes an iterable of strings (inc. a string) and returns a tuple of variables created with them

    nice function to create a bunch of variables in one call
    """
    return tuple(Variable(c) for c in s)


class Tail(Variable):
    """Variable-like class used for tail unification

    These can be created using the unary "+" on variables. This is equivalent to the prolog "|".
    Best explained with an example: the prolog `X = [H | T]` and the python `unify(X, [H, +T])`
    represent the same thing.
    """
    def __repr__(self):
        return "+" + self.name


@dataclass(frozen=True)
class Rule:
    head: Term
    body: Logical = YES

    @property
    def op(self):
        return self.head.op

    @property
    def args(self):
        return self.head.args

    def map(self, func):
        return Rule(self.head.map(func), self.body.map(func))

    def __repr__(self) -> str:
        return f"{self.head} <= {self.body}"
