import abc
import functools
import itertools
import typing
from collections import defaultdict

from src import language, unification


TYPE_RULES = typing.Optional[typing.Iterable[language.Rule]]


class AbstractTable(abc.ABC):

    @abc.abstractmethod
    def fetch(self, query: language.Term, conditional: bool = True) -> typing.Iterator[language.Rule]:
        """returns all rules which unify with the query

        Arguments:
            query: attempt to unify with this
            conditional: whether to return results which are only conditionally true, default False

        Returns:
            an iterable of named tuples carrying a "binding" and a "condition"
        """
        pass

    @abc.abstractmethod
    def tell(self, rule: typing.Union[language.Term, language.Rule]) -> None:
        """Adds the rule to the table"""
        pass

    @abc.abstractmethod
    def rules(self) -> typing.Iterable[language.Rule]:
        """An iterable over the rules in the table"""
        pass

    def facts(self):
        return (rule.head for rule in self.rules() if rule.body == language.YES)


class LinearTable(AbstractTable):
    """A table where complexity is linear"""
    def __init__(self, rules: TYPE_RULES = ()):
        self._rules = []
        for rule in rules:
            self.tell(rule)

    def tell(self, rule: typing.Union[language.Term, language.Rule]) -> None:
        if isinstance(rule, language.Term):
            rule = language.Rule(rule, language.YES)
        self._rules.append(language.standardize(rule))

    def rules(self) -> typing.Iterable[language.Rule]:
        return tuple(self._rules)

    def fetch(self, query: language.Term, conditional: bool = True) -> typing.Iterator[language.Rule]:
        for rule in self.rules():
            if (unification.unify(rule.head, query) != language.NO) and\
                    ((rule.body == language.YES) or conditional):
                yield rule


class TrieTable(AbstractTable):
    """Table implementing a trie-inspired search strategy"""
    def __init__(self, rules: TYPE_RULES = ()):
        self._rules: typing.List[language.Rule] = []
        self.trie: typing.Dict[str, TrieTable] = defaultdict(TrieTable)

        for rule in rules:
            self.tell(rule)

    def tell_destructured(self, head: tuple, rule: language.Rule):
        if head:
            self.trie[head[0]].tell_destructured(head[1:], rule)
        else:
            self._rules.append(rule)

    def tell(self, rule: typing.Union[language.Term, language.Rule]) -> None:
        if isinstance(rule, language.Term):
            rule = language.Rule(rule, language.YES)
        rule = language.standardize(rule)
        self.tell_destructured((rule.head.op, *rule.head.args), rule)

    # noinspection PyStatementEffect
    def _fetch(self, query: tuple, conditional: bool) -> typing.Iterator[language.Rule]:
        if query:
            if not isinstance(query[0], language.Variable):
                self.trie[query[0]]  # creates sub-trie
            for key in self.trie:
                this_binding = unification.unify(query[0], key)
                if this_binding != language.NO:
                    for result in self.trie[key]._fetch(query[1:], conditional):
                        yield result
        else:
            for rule in self._rules:
                yield rule

    def fetch(self, query: language.Term, conditional: bool = True) -> typing.Iterator[language.Rule]:
        return self._fetch((query.op, *query.args), conditional)

    def rules(self):
        for rule in self._rules:
            yield rule

        for trie in self.trie.values():
            for rule in trie.rules():
                yield rule


class HeuristicIndex(AbstractTable):
    """Wraps a table, sorting fetch results by projected usefulness

    Arguments:
        table: a table to wrap
    """
    def __init__(self, table: AbstractTable):
        self.table: AbstractTable = table

    @functools.lru_cache(maxsize=2000)
    def score(self, condition: language.Logical):  # lower is faster
        if condition == language.YES:
            return 0
        elif isinstance(condition, language.Term):
            return 1
        elif isinstance(condition, language.Or):
            return 2
        elif isinstance(condition, language.And):
            return len(condition.args)
        else:
            return float("inf")

    def tell(self, rule: typing.Union[language.Term, language.Rule]) -> None:
        if isinstance(rule, language.Term):
            rule = language.Rule(rule, language.YES)
        self.table.tell(rule)

    def fetch(self, query: language.Term, conditional: bool = True) -> typing.Iterator[language.Rule]:
        if not conditional:
            return self.table.fetch(query, conditional)
        results = list(self.table.fetch(query, conditional=conditional))
        return iter(sorted(results, key=lambda r: self.score(r.body)))

    def rules(self) -> typing.Iterable[language.Rule]:
        return self.table.rules()


class PredicateIndex(AbstractTable):
    """Table implementing a predicate based indexing scheme to sub tables

    Arguments:
        factory: a type of abstract table, used to construct the tables used for each predicate
    """
    def __init__(self, rules: TYPE_RULES = (), factory: typing.Type[AbstractTable] = LinearTable):
        self.predicates: typing.Dict[str, AbstractTable] = {}
        self.factory: typing.Type[AbstractTable] = factory
        for rule in rules:
            self.tell(rule)

    def rules(self) -> typing.Iterable[language.Rule]:
        return itertools.chain(*(t.rules() for t in self.predicates.values()))

    def tell(self, rule: typing.Union[language.Term, language.Rule]) -> None:
        if isinstance(rule, language.Term):
            rule = language.Rule(rule, language.YES)
        if rule.op not in self.predicates:
            self.predicates[rule.op] = self.factory()
        self.predicates[rule.op].tell(rule)

    def fetch(self, query: language.Term, conditional: bool = True) -> typing.Iterator[language.Rule]:
        return self.predicates[query.op].fetch(query, conditional=conditional)
