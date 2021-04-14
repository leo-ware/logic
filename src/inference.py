import typing
from copy import copy

from src import language, knowledgebase, unification
from src.unification import TYPE_BINDING, TYPE_BINDINGS


# forward chaining
def forward_chain(kb: knowledgebase.KnowledgeBase, inplace: bool = False) -> knowledgebase.KnowledgeBase:
    """deduce all deducible facts on kb

    Arguments:
        kb (KnowledgeBase): the knowledgebase to work on
        inplace (bool): whether to replace the current kb (as opposed to copying), default False

    Returns:
        the original kb is inplace=True, otherwise a new one with all possible deductions made
    """

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


def fc_ask(kb: knowledgebase.KnowledgeBase, query: language.Term, inplace: bool = False) -> TYPE_BINDINGS:
    """use forward chaining to attempt to infer the query, returning a (potentially empty) iterable of bindings"""
    if not inplace:
        kb = copy(kb)
    forward_chain(kb, inplace=True)
    return kb.fetch(query)


# backwards chaining
def bc_ask(kb: knowledgebase.KnowledgeBase, query: language.Term, binding: typing.Optional[TYPE_BINDING] = None)\
        -> TYPE_BINDINGS:
    """Use backward chaining (naive dfs) to attempt to infer the query from KB"""

    # default to empty binding
    binding = binding or {}

    # pass fails up the callstack
    if binding == language.FAIL:
        return language.FAIL

    #  maybe we don't need to use rules
    for free_binding in kb.fetch(query, binding):
        yield free_binding
        if free_binding == {}:
            return

    # special handling for Ands
    if isinstance(query, language.And):
        return _bc_and(kb, query, binding)

    # dfs
    for rule in kb.rules:
        if isinstance(rule, language.Rule):
            satisfies_head = unification.unify(rule.head, query, binding)
            if satisfies_head != language.FAIL:
                for result in bc_ask(kb, language.substitute(rule.body, satisfies_head)):
                    yield result


def _bc_and(kb: knowledgebase.KnowledgeBase, goals: language.And, binding: TYPE_BINDING) -> TYPE_BINDINGS:
    if not goals:
        return binding

    for satisfy_first in bc_ask(kb, language.substitute(goals.first, binding), binding):
        for satisfy_rest in _bc_and(kb, goals.rest, satisfy_first):
            yield satisfy_rest
