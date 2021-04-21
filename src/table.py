import abc
import functools
import itertools
import typing
from collections import namedtuple, defaultdict

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
    """A table where complexity is linear"""
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
            if (rule_binding != language.NO) and ((rule.body is language.YES) or conditional):
                rule_binding.update(binding)  # pass on irrelevant constraints
                yield FetchResult(rule_binding, language.substitute(rule.body, rule_binding))


class TrieTable(AbstractTable):
    """Table implementing a trie-inspired search strategy"""
    def __init__(self, rules: TYPE_RULES = ()):
        self.conditional: typing.List[language.Logical] = []
        self.unconditional: bool = False
        self.trie: typing.Dict[str, TrieTable] = defaultdict(TrieTable)

        for rule in rules:
            self.tell(rule)

    def tell_destructured(self, head: tuple, body: language.Logical):
        if head:
            self.trie[head[0]].tell_destructured(head[1:], body)
        elif body == language.YES:
            self.unconditional = True
        else:
            self.conditional.append(body)

    def tell(self, rule: language.Rule):
        rule = language.standardize(rule)
        self.tell_destructured((rule.head.op, *rule.head.args), rule.body)

    def conditions(self, conditional: bool):
        if self.unconditional:
            yield language.YES
        if conditional:
            for condition in self.conditional:
                yield condition

    # noinspection PyStatementEffect
    def _fetch(self, query: tuple, conditional: bool, binding: TYPE_BINDING) -> typing.Iterator[FetchResult]:
        if query:
            if not isinstance(query[0], language.Variable):
                self.trie[query[0]]  # creates sub-trie
            for key in self.trie:
                this_binding = unification.unify(query[0], key, binding)
                if this_binding != language.NO:
                    for result in self.trie[key]._fetch(query[1:], conditional, this_binding):
                        yield result
        else:
            for c in self.conditions(conditional):
                yield FetchResult(dict(binding), c)

    def fetch(self, query: language.Term, conditional: bool = False, binding: typing.Optional[TYPE_BINDING] = None) \
            -> typing.Iterator[FetchResult]:
        return self._fetch((query.op, *query.args), conditional, binding or {})

    def rules(self, _op=None, _args=()):

        # base cases
        term = language.Term(_op, _args)
        if self.unconditional:
            yield language.Rule(term, language.YES)

        for condition in self.conditional:
            yield language.Rule(term, condition)

        # recursive calls
        for name, child in self.trie.items():
            if _op is None:
                kid_op, kid_args = name, ()
            else:
                kid_op, kid_args = _op, (*_args, name)

            for rule in child.rules(kid_op, kid_args):
                yield rule


class HeuristicIndex(AbstractTable):
    """Wraps a table, sorting fetch results by projected usefulness

    Arguments:
        table: a table to wrap
    """
    def __init__(self, table: AbstractTable):
        self.table = table

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

    def tell(self, rule: language.Rule) -> None:
        self.table.tell(rule)

    def fetch(self, query: language.Term, conditional: bool = False, binding: typing.Optional[TYPE_BINDING] = None) ->\
            typing.Iterator[FetchResult]:
        if not conditional:
            return self.table.fetch(query, conditional, binding)
        results = list(self.table.fetch(query, conditional=conditional, binding=binding))
        return iter(sorted(results, key=lambda r: self.score(r.condition)))

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

    def tell(self, rule: language.Rule) -> None:
        if rule.op not in self.predicates:
            self.predicates[rule.op] = self.factory()
        self.predicates[rule.op].tell(rule)

    def fetch(self, query: language.Term, conditional: bool = False, binding: typing.Optional[TYPE_BINDING] = None)\
            -> typing.Iterator[FetchResult]:
        return self.predicates[query.op].fetch(query, conditional=conditional, binding=binding)
