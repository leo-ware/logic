import itertools
import typing

from src import language, unification, table, constraints


def take(n, search):
    """Get as many of the first n results from a search as exist"""
    thing = []
    for _ in range(n):
        try:
            thing.append(next(search))
        except StopIteration:
            break
    return thing


def bc_ask_and(tb, query: language.And, binding: typing.Optional[unification.TYPE_BINDING] = None, conditional: bool = True) -> unification.TYPE_BINDINGS:
    """Finds bindings that satisfy query in tb"""
    binding = binding or {}
    if binding == language.NO:
        return
    elif query == language.YES:
        yield binding
    else:
        for binding_head in bc_ask(tb, language.substitute(query.first, binding), binding, conditional=conditional):
            for binding_rest in bc_ask_and(tb, query.rest, binding_head, conditional=conditional):
                yield binding_rest


def bc_ask(tb: table.AbstractTable, query: language.Term, binding: typing.Optional[unification.TYPE_BINDING] = None, conditional: bool = True) -> unification.TYPE_BINDINGS:
    """Finds bindings that satisfy query in tb"""
    binding = binding or {}
    for rule in tb.fetch(query, conditional=conditional):
        rule = language.standardize(rule)
        for body_binding in bc_ask_and(tb, language.And([rule.body]), unification.unify(rule.head, query, binding), conditional=conditional):
            yield dict(body_binding)


def fetch(tb: table.AbstractTable, query: language.Logical, binding: typing.Optional[unification.TYPE_BINDING] = None) -> unification.TYPE_BINDINGS:
    """Finds bindings for which query can be derived from facts in tb"""
    binding = binding or {}
    if language.NO in [query, binding]:
        return []
    elif query == language.YES:
        return [binding]
    elif isinstance(query, language.Not):
        try:
            next(fetch(tb, query.item, binding))
            return []
        except StopIteration:
            return [binding]
    elif isinstance(query, constraints.Constraint):
        return query.test(binding)
    elif isinstance(query, language.Or):
        return itertools.chain(*(fetch(tb, q, binding=binding) for q in query))
    elif isinstance(query, language.And):
        return bc_ask_and(tb, query, binding=binding, conditional=False)
    elif isinstance(query, language.Term):
        return bc_ask(tb, query, binding=binding, conditional=False)
    else:
        raise ValueError(f"can't fetch type {type(query)}")


def forward_chain(tb: table.AbstractTable) -> None:
    """deduce all deducible facts on kb

    Arguments:
        tb: the knowledgebase to work on

    Returns:
        the original kb is inplace=True, otherwise a new one with all possible deductions made
    """
    new = True
    while new:
        new = set()
        for rule in tb.rules():
            for binding in fetch(tb, rule.body):
                q = language.substitute(rule.head, binding)
                try:
                    next(tb.fetch(q, conditional=False))
                except StopIteration:
                    new.add(q)

        for term in new:
            tb.tell(language.Rule(term, language.YES))


def fc_ask(kb: table.AbstractTable, query: language.Logical) -> unification.TYPE_BINDINGS:
    """use forward chaining (~bfs) to infer the query"""
    forward_chain(kb)
    return fetch(kb, query)


# def id_ask(kb: knowledgebase.KnowledgeBase, query: language.Logical, patience=float("inf")) -> TYPE_BINDINGS:
#     """Use iterative deepening dfs to infer the query from KB
#
#     Arguments:
#         kb: the knowledgebase or table to consult with
#         query: the statement to prove
#         patience: maximum depth to search (defaults to infinity)
#     """
#     level = 0
#     new = True
#     while (level <= patience) and new:
#         new = False
#         for binding in bc_ask(kb, query, level):
#             if binding.depth >= level:
#                 new = True
#                 yield dict(binding)
#         level += 1
