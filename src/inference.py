from src import language, unification, table


def take(n, search):
    """Get as many of the first n results from a search as exist"""
    thing = []
    for _ in range(n):
        try:
            thing.append(next(search))
        except StopIteration:
            break
    return thing


def relevant(query, binding):
    """reduce the binding to only the variables relevant to the query"""
    new = {}
    for var in binding:
        new[var] = binding[var]
        while new[var] in binding:
            new[var] = binding[new[var]]
    return {k: v for k, v in new.items() if k in language.variables_in(query)}


def _bc_and(tb, query, binding=None, patience=float("inf")):
    if binding is None:
        binding = {}

    if binding == language.NO:
        return []
    elif query == language.YES:
        yield dict(binding)
    else:
        query = language.And([query])
        for satisfies_me in _bc_or(tb, language.substitute(query.first, binding), binding, patience=patience):
            for satisfies_rest in _bc_and(tb, query.rest, satisfies_me, patience=patience):
                yield satisfies_rest


def _bc_or(tb, query, binding, patience):
    for rule in tb.fetch(query, conditional=bool(patience)):
        rule = language.standardize(rule)
        for ans in _bc_and(tb, rule.body, unification.unify(rule.head, query, binding), patience=patience-1):
            yield ans


def bc_ask(tb: table.AbstractTable, query: language.Term, patience=float("inf")):
    """Uses backward chaining to derive query from kb"""
    return (relevant(query, ans) for ans in _bc_or(tb, query, {}, patience=patience))


def fc_ask(tb: table.AbstractTable, query: language.Term) -> unification.TYPE_BINDINGS:
    """Uses forward chaining to derive query from kb"""

    for freebie in bc_ask(tb, query, patience=0):
        yield freebie

    new = True
    while new:
        new = set()
        for rule in tb.rules():
            for binding in _bc_and(tb, rule.body, patience=0):
                q = language.substitute(rule.head, binding)
                if not any(unification.unifiable(q, fact) for fact in tb.facts()):
                    new.add(q)

        for term in new:
            s = unification.unify(term, query)
            if s != language.NO:
                yield dict(s)
            tb.tell(language.Rule(term, language.YES))


def id_ask(tb: table.AbstractTable, query: language.Term, patience=float("inf")) -> unification.TYPE_BINDINGS:
    """Uses iterative deepening search to derive query, allowing it to solve more problems than backward chaining"""

    level = 0
    drop_first = 0

    while level <= patience:
        level += 1
        n_finds = 0

        for binding in bc_ask(tb, query, patience=level):
            n_finds += 1
            if n_finds > drop_first:  # so search results from each level don't get repeated every subsequent level
                yield binding

        drop_first = n_finds
