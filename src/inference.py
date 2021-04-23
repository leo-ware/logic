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


def _bc_and(tb, query, binding=None, use_rules=True):
    if binding is None:
        binding = {}

    if binding == language.NO:
        return []
    elif query == language.YES:
        yield dict(binding)
    else:
        query = language.And([query])
        for satisfies_me in _bc_or(tb, language.substitute(query.first, binding), binding, use_rules=use_rules):
            for satisfies_rest in _bc_and(tb, query.rest, satisfies_me, use_rules=use_rules):
                yield satisfies_rest


def _bc_or(tb, query, binding, use_rules=True):
    for rule in tb.fetch(query, conditional=use_rules):
        print(rule)
        rule = language.standardize(rule)
        for ans in _bc_and(tb, rule.body, unification.unify(rule.head, query, binding)):
            yield ans


def bc_ask(tb: table.AbstractTable, query: language.Term, use_rules=True):
    return (relevant(query, ans) for ans in _bc_or(tb, query, {}, use_rules=use_rules))


def fc_ask(tb: table.AbstractTable, query: language.Term) -> unification.TYPE_BINDINGS:

    for freebie in bc_ask(tb, query, use_rules=False):
        yield freebie

    new = True
    while new:
        new = set()
        for rule in tb.rules():
            for binding in _bc_and(tb, rule.body, use_rules=False):
                q = language.substitute(rule.head, binding)
                if not any(unification.unifiable(q, fact) for fact in tb.facts()):
                    new.add(q)

        for term in new:
            s = unification.unify(term, query)
            if s != language.NO:
                yield dict(s)
            tb.tell(language.Rule(term, language.YES))
