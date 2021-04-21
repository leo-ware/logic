import itertools
import typing
from src import language, table as t, constraints
from src.unification import TYPE_BINDING

# TODO why do some unconditional queries return condition of empty And?


class KnowledgeBase(t.AbstractTable):
    """Nice, flexible frontend to a table"""
    def __init__(self, table: t.AbstractTable, rules: typing.Iterable[typing.Union[language.Term, language.Rule]] = ()):
        self.table = table
        for k in rules:
            self.tell(k)

    # TODO only return relevant bindings (hard b/c some bindings carry structure associated with variables not in query)

    def fetch(self, query: language.Logical, conditional: bool = False, binding: typing.Optional[TYPE_BINDING] = None) \
            -> typing.Iterator[t.FetchResult]:
        binding = binding or {}
        if binding == language.NO:
            return iter([t.FetchResult(language.NO, language.NO)])
        if isinstance(query, language.Keyword):  # must be first branch
            if query == language.YES:
                return iter([t.FetchResult(binding, language.YES)])
            elif query == language.NO:
                return iter([t.FetchResult(language.NO, language.NO)])
            else:
                raise ValueError(f"don't know what to do with {query}")
        elif isinstance(query, language.Not):
            try:
                next(self.fetch(query.item, conditional, binding))
                return [t.FetchResult(language.NO, language.NO)]
            except StopIteration:
                return [t.FetchResult(binding, language.YES)]
        elif isinstance(query, constraints.Constraint):
            return (t.FetchResult(b, language.YES) for b in query.test(binding))
        elif isinstance(query, language.Or):
            return itertools.chain(*(self.fetch(q, binding=binding) for q in query))
        elif isinstance(query, language.And):
            return self._fetch_and(query, conditional=conditional, binding=binding)
        elif isinstance(query, language.Term):
            return self.table.fetch(query, conditional=conditional, binding=binding)
        else:
            raise ValueError(f"can't fetch type {type(query)}")

    def _fetch_and(self, query: language.And, conditional: bool = False, binding: typing.Optional[TYPE_BINDING] = None)\
            -> typing.Iterator[t.FetchResult]:
        if not query:
            yield t.FetchResult(dict(binding), language.YES)
        else:
            for me_result in self.fetch(query.first, binding=binding, conditional=conditional):
                for them_result in self.fetch(query.rest, binding=me_result.binding, conditional=conditional):
                    if them_result.binding != language.NO:

                        # TODO figure out how to fail on contradictory conditions
                        yield t.FetchResult(them_result.binding, language.And([them_result.condition,
                                                                               me_result.condition]))

    def tell(self, rule: typing.Union[language.Rule, language.Logical]) -> None:
        if isinstance(rule, language.And):
            for sub_rule in rule:
                self.tell(sub_rule)
        elif isinstance(rule, language.Or):
            raise ValueError("bro horn clauses only")
        elif isinstance(rule, language.Term):
            self.tell(language.Rule(rule))
        else:
            self.table.tell(rule)

    def rules(self) -> typing.Iterable[language.Rule]:
        return self.table.rules()
