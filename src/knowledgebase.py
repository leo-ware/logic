import itertools
import typing
from src import language, table as t
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
        if isinstance(query, language.Keyword):
            if query == language.TRUE:
                return iter([t.FetchResult(binding or {}, language.TRUE)])
            elif query == language.FAIL:
                return iter([t.FetchResult(language.FAIL, language.FAIL)])
            else:
                raise ValueError(f"don't know what to do with {query}")
        elif isinstance(query, language.Or):
            return itertools.chain(*(self.fetch(q, binding=binding) for q in query))
        elif isinstance(query, language.Term):
            return self.table.fetch(query, conditional=conditional, binding=binding)
        elif isinstance(query, language.And):
            return self._fetch_and(query, conditional=conditional, binding=binding or {})
        else:
            raise ValueError(f"can't fetch type {type(query)}")

    def _fetch_and(self, query: language.And, conditional: bool = False, binding: typing.Optional[TYPE_BINDING] = None)\
            -> typing.Iterable[t.FetchResult]:

        if not query:
            yield t.FetchResult(dict(binding), language.TRUE)
        else:
            for me_result in self.fetch(query.first, binding=binding, conditional=conditional):
                for them_result in self._fetch_and(query.rest, binding=me_result.binding, conditional=conditional):

                    # TODO more satisfactory recombination of conditions than And
                    yield t.FetchResult(them_result.binding, language.And([them_result.condition, me_result.condition]))

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
