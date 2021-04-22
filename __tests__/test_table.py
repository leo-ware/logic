from src import *
from anything import Anything

x, y = variables("xy")
Leo = Term("Leo")
Declan = Term("Declan")
Milo = Term("Milo")
Henry = Term("Henry")

sibling = functor("sibling")
father = functor("father")

foo = LinearTable([
    sibling(Leo, x) <= sibling(Declan, x),
    sibling(Leo, Milo) <= language.YES
])


def howto_test(tb):
    def test():
        assert tuple(tb.rules()) in [((sibling(Leo, Milo) <= language.YES,
                                        sibling(Leo, Anything) <= sibling(Declan, Anything))),
                                     ((sibling(Leo, Anything) <= sibling(Declan, Anything)),
                                       sibling(Leo, Milo) <= language.YES)]
        assert len(list(tb.fetch(sibling(Leo, Milo)))) == 2
        assert list(tb.fetch(sibling(Leo, Declan))) == [sibling(Leo, Anything) <= sibling(Declan, Anything)]
    return test


test_linear = howto_test(foo)
test_predicate = howto_test(PredicateIndex(foo.rules()))
test_heuristic = howto_test(HeuristicIndex(foo))
test_trie = howto_test(TrieTable(foo.rules()))

t = TrieTable
print(list(
    TrieTable(foo.rules()).rules()
))
