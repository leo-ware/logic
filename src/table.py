import abc
import itertools
import typing
from collections import namedtuple

from src import language, unification
from src.unification import TYPE_BINDING


TYPE_RULES = typing.Optional[typing.Iterable[language.Rule]]

FetchResult = namedtuple("FetchResult", ["binding", "condition"])


class AbstractTable(abc.ABC):

    @abc.abstractmethod
    def fetch(self, query: language.Term, conditional: bool = False, binding: typing.Optional[TYPE_BINDING] = None)\
            -> typing.Iterator[FetchResult]:
        """returns all rules which unify with the query

        Arguments:
            query: attempt to unify with this
            conditional: whether to return results which are only conditionally true, default False
            binding: only return matches subject to this constraint

        Returns:
            an iterable of named tuples carrying a "binding" and a "condition"
        """
        pass

    @abc.abstractmethod
    def tell(self, rule: language.Rule) -> None:
        """Adds the rule to the table"""
        pass

    @abc.abstractmethod
    def rules(self) -> typing.Iterable[language.Rule]:
        """An iterable over the rules in the table"""
        pass


class LinearTable(AbstractTable):
    """A table where search complexity is linear"""
    def __init__(self, rules: TYPE_RULES = ()):
        self._rules = []
        for rule in rules:
            self.tell(rule)

    def tell(self, rule: language.Rule) -> None:
        self._rules.append(language.standardize(rule))

    def rules(self) -> typing.Iterable[language.Rule]:
        return tuple(self._rules)

    def fetch(self, query: language.Term, conditional: bool = False, binding: typing.Optional[TYPE_BINDING] = None)\
            -> typing.Iterator[FetchResult]:
        for rule in self.rules():
            rule_binding = unification.unify(rule.head, query, binding or {})
            if (rule_binding != language.FAIL) and ((rule.body is language.TRUE) or conditional):
                rule_binding.update(binding)  # pass on irrelevant constraints
                yield FetchResult(rule_binding, language.substitute(rule.body, rule_binding))


class PredicateIndex(AbstractTable):
    """Table implementing a predicate based indexing scheme to sub tables"""
    def __init__(self, rules: TYPE_RULES = (), factory: typing.Type[AbstractTable] = LinearTable):
        self.predicates: typing.Dict[str, AbstractTable] = {}
        self.factory: typing.Type[AbstractTable] = factory
        for rule in rules:
            self.tell(rule)

    def rules(self) -> typing.Iterable[language.Rule]:
        return itertools.chain(*(t.rules() for t in self.predicates.values()))

    def tell(self, rule: language.Rule) -> None:
        if rule.op not in self.predicates:
            self.predicates[rule.op] = self.factory()
        self.predicates[rule.op].tell(rule)

    def fetch(self, query: language.Term, conditional: bool = False, binding: typing.Optional[TYPE_BINDING] = None)\
            -> typing.Iterator[FetchResult]:
        return self.predicates[query.op].fetch(query, conditional=conditional, binding=binding)
