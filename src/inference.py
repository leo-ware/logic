from src import language, knowledgebase, types

from copy import copy


def forward_chain(kb: knowledgebase.KnowledgeBase, inplace: bool = False) -> knowledgebase.KnowledgeBase:
    """deduce all deducible facts inplace on kb"""

    if inplace:
        kb = copy(kb)

    new = True
    while new:
        new = set()
        for rule in kb.rules:
            if isinstance(rule, language.Rule):
                rule = language.standardize_variables(rule)
                for binding in kb.fetch(rule.body):
                    q = language.substitute(rule.head, binding)
                    if not list(kb.fetch(q)):
                        new.add(q)

        for term in new:
            kb.tell(term)

    return kb


def fc_infer(kb: knowledgebase.KnowledgeBase, query: language.Term, inplace: bool = False) -> types.Bindings:
    """use forward chaining to attempt to infer the query, returning a (potentially empty) iterable of bindings"""
    if not inplace:
        kb = copy(kb)
    forward_chain(kb, inplace=True)
    return kb.fetch(query)
