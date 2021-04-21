from src import language, knowledgebase
from src.unification import TYPE_BINDINGS

# TODO inference functions return proof trees


def take(n, search):
    """Get as many of the first n results from a search as exist"""
    thing = []
    for _ in range(n):
        try:
            thing.append(next(search))
        except StopIteration:
            return thing


def forward_chain(kb: knowledgebase.KnowledgeBase) -> knowledgebase.KnowledgeBase:
    """deduce all deducible facts on kb

    Arguments:
        kb: the knowledgebase to work on

    Returns:
        the original kb is inplace=True, otherwise a new one with all possible deductions made
    """
    new = True
    while new:
        new = set()
        for rule in kb.rules():
            if isinstance(rule, language.Rule):
                for result in kb.fetch(rule.body):
                    q = language.substitute(rule.head, result.binding)
                    if not list(kb.fetch(q)):
                        new.add(q)

        for term in new:
            kb.tell(term)

    return kb


def fc_ask(kb: knowledgebase.KnowledgeBase, query: language.Logical) -> TYPE_BINDINGS:
    """use forward chaining (~bfs) to infer the query"""
    return [dict(r.binding) for r in forward_chain(kb).fetch(query)]


def bc_ask(kb: knowledgebase.KnowledgeBase, query: language.Logical, patience=float("inf"), min_depth=0, _depth=0) ->\
        TYPE_BINDINGS:
    """Use backward chaining (naive dfs) to attempt to infer the query, optionally with a search depth limit

    Note: the top call is said to have depth 0

    Arguments:
        kb: the knowledgebase or table to consult with
        query: the statement to prove
        patience: only search to this depth, not farther
        min_depth: only report findings from this depth or lower
        _depth
    """
    for result in kb.fetch(query, conditional=True):
        if result.condition in [language.YES, language.And([])]:
            if _depth >= min_depth:
                yield dict(result.binding)
        elif patience > _depth:
            search = bc_ask(kb, language.substitute(result.condition, result.binding), patience=patience,
                            min_depth=min_depth, _depth=_depth + 1)
            for sub_goal_binding in search:
                yield dict(sub_goal_binding)


# def id_ask(kb: knowledgebase.KnowledgeBase, query: language.Logical, patience=float("inf")) -> TYPE_BINDINGS:
#     level = 0
#     while level <= patience:
#         for binding in bc_ask(kb, query, patience=level, min_depth=level):
#             yield dict(binding)
#         level += 1
