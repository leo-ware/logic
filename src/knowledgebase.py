import typing

from src import types, language
from src.unification import unify, Fail


class KnowledgeBase:
    def __init__(self, known: typing.Iterable[language.Term]):
        self.rules = set()
        for sentence in known:
            self.tell(sentence)

    def __repr__(self) -> str:
        return f"KnowledgeBase([\n    " + ",\n    ".join(map(str, self.rules)) + "\n])\n"

    def tell(self, sentence: typing.Union[language.Rule, language.Term]) -> None:
        """
        adds a fact (term or rule) to the kb
        """
        self.rules.add(language.standardize_variables(sentence, reset=True))

    def fetch(self, query: language.Term, binding: typing.Optional[types.Binding] = None) -> types.Bindings:
        """
        Returns bindings under which the query can be derived from facts (not rules!) in the kb
        """
        if not query:
            return [binding] or [{}]
        elif isinstance(query, language.And):
            return self._fetch_and(query, binding)
        else:
            return self._fetch_sentence(query, binding)

    def _fetch_and(self, query: language.And, binding: typing.Optional[types.Binding] = None) -> types.Bindings:
        for im_satisfied in self.fetch(query.head, binding):
            es = self.fetch(query.rest, im_satisfied)
            for everyone_satisfied in es:
                if everyone_satisfied != Fail:
                    yield dict(everyone_satisfied)

    def _fetch_sentence(self, query: language.Term, binding: typing.Optional[types.Binding] = None) -> types.Bindings:
        queue = list(self.rules)
        while queue:
            have = queue.pop()
            if isinstance(have, language.Rule):
                if have.body is True:
                    queue.append(have.head)
            elif isinstance(have, language.And):
                queue.extend(have)
            else:
                u = unify(have, query, binding)
                if u != Fail:
                    yield dict(u)
