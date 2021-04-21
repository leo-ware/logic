from abc import ABC, abstractmethod
from src import unification, language


class Constraint(language.Logical, ABC):
    """Constraints embed python code inside proof procedures

    Constraints provide a way to include arbitrary Python code in the resolution procedure. They have two methods,
    `.test()`, which takes a binding and returns a list of bindings under which the constraint holds. This can
    be used to cause side effects, perform tests not expressible in prolog, etc. The other is `.map()` which should
    return a new object created by applying the provided transformation to any Logical arguments.
    """

    @abstractmethod
    def test(self, binding: unification.TYPE_BINDING) -> unification.TYPE_BINDINGS:
        """Whether the binding makes the constraint true

        Args:
            binding: a binding, some kind of mapping from variables to values

        Returns:
            an iterable over bindings that satisfy the constraint
        """
        pass

    # potentially add later as an optimization
    # @abstractmethod
    # def always(self) -> bool:
    #     """whether the constraint is trivially true"""
    #     pass


class Comparison(Constraint, ABC):
    def __init__(self, x1, x2):
        self.x1 = x1
        self.x2 = x2

    def __repr__(self):
        return f"{self.__class__.__name__}({self.x1}, {self.x2})"

    def map(self, func):
        map1 = self.x1.map(func) if isinstance(self.x1, language.Logical) else func(self.x1)
        map2 = self.x2.map(func) if isinstance(self.x2, language.Logical) else func(self.x2)
        return self.__class__(map1, map2)


class Equals(Comparison):
    def test(self, binding: unification.TYPE_BINDING) -> unification.TYPE_BINDINGS:
        unf = unification.unify(self.x1, self.x2, binding)
        if unf != language.NO:
            return [unf]
        else:
            return []


class LE(Comparison):
    def test(self, binding: unification.TYPE_BINDING) -> unification.TYPE_BINDINGS:
        x1, x2 = unification.value(self.x1, binding), unification.value(self.x2, binding)
        if (language.FREE in [x1, x2]) or not (x1 <= x2):
            return []
        else:
            return [binding]


class GE(Comparison):
    def test(self, binding: unification.TYPE_BINDING) -> unification.TYPE_BINDINGS:
        x1, x2 = unification.value(self.x1, binding), unification.value(self.x2, binding)
        if (language.FREE in [x1, x2]) or not (x1 >= x2):
            return []
        else:
            return [binding]


class LT(Comparison):
    def test(self, binding: unification.TYPE_BINDING) -> unification.TYPE_BINDINGS:
        x1, x2 = unification.value(self.x1, binding), unification.value(self.x2, binding)
        if (language.FREE in [x1, x2]) or not (x1 < x2):
            return []
        else:
            return [binding]


class GT(Comparison):
    def test(self, binding: unification.TYPE_BINDING) -> unification.TYPE_BINDINGS:
        x1, x2 = unification.value(self.x1, binding), unification.value(self.x2, binding)
        if (language.FREE in [x1, x2]) or not (x1 > x2):
            return []
        else:
            return [binding]
