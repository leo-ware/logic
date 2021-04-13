import typing
from src import language, unification
from bidict import bidict


# types
TYPE_BINDING = typing.Union[typing.Mapping[language.Variable, typing.Any], bidict, typing.Literal[language.FAIL]]
TYPE_BINDINGS = typing.Iterable[TYPE_BINDING]


class KnowledgeBase:
    def __init__(self, known: typing.Iterable[typing.Union[language.Term, language.Rule]]):
        self.rules = set()
        for sentence in known:
            self.tell(sentence)

    def __repr__(self) -> str:
        return f"KnowledgeBase([\n    " + ",\n    ".join(map(str, self.rules)) + "\n])\n"

    def __eq__(self, other):
        return (type(self) == type(other)) and (self.rules == other.rules)

    def tell(self, sentence: typing.Union[language.Rule, language.Term]) -> None:
        """
        adds a fact (term or rule) to the kb
        """
        self.rules.add(language.standardize_variables(sentence, reset=True))

    def fetch(self, query: language.Term, binding: typing.Optional[TYPE_BINDING] = None) -> TYPE_BINDINGS:
        """
        Returns bindings under which the query can be derived from facts (not rules!) in the kb
        """
        if not query:
            return [binding] or [{}]
        elif isinstance(query, language.And):
            return self._fetch_and(query, binding)
        else:
            return self._fetch_sentence(query, binding)

    def _fetch_and(self, query: language.And, binding: typing.Optional[TYPE_BINDING] = None) -> TYPE_BINDINGS:
        for im_satisfied in self.fetch(query.first, binding):
            es = self.fetch(query.rest, im_satisfied)
            for everyone_satisfied in es:
                if everyone_satisfied != language.FAIL:
                    yield dict(everyone_satisfied)

    def _fetch_sentence(self, query: language.Term, binding: typing.Optional[TYPE_BINDING] = None) -> TYPE_BINDINGS:
        queue = list(self.rules)
        while queue:
            have = queue.pop()
            if isinstance(have, language.Rule):
                if have.body is True:
                    queue.append(have.head)
            elif isinstance(have, language.And):
                queue.extend(have)
            else:
                u = unification.unify(have, query, binding)
                if u != language.FAIL:
                    yield dict(u)
