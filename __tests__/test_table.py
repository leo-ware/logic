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
    sibling(Leo, Milo) <= language.TRUE
])


def test_linear_table():
    assert tuple(foo.rules()) == (sibling(Leo, Anything) <= sibling(Declan, Anything),
                                  sibling(Leo, Milo) <= language.TRUE)
    assert len(list(foo.fetch(sibling(Leo, Milo)))) == 1
    assert list(foo.fetch(sibling(Leo, Milo)))[0].binding == {}
    assert list(foo.fetch(sibling(Leo, Milo)))[0].condition == language.TRUE


def test_predicate_index():
    bar = PredicateIndex(foo.rules())
    assert tuple(bar.rules()) == (sibling(Leo, Anything) <= sibling(Declan, Anything),
                                  sibling(Leo, Milo) <= language.TRUE)
    assert len(list(bar.fetch(sibling(Leo, Milo)))) == 1
    assert list(bar.fetch(sibling(Leo, Milo)))[0].binding == {}
    assert list(bar.fetch(sibling(Leo, Milo)))[0].condition == language.TRUE

    assert len(bar.predicates) == 1
    bar.tell(father(Leo, Henry) <= language.TRUE)
    assert len(bar.predicates) == 2


def test_heuristic_index():
    baz = HeuristicIndex(foo)
    assert tuple(baz.rules()) in [((sibling(Leo, Milo) <= language.TRUE,
                                    sibling(Leo, Anything) <= sibling(Declan, Anything))),
                                  ((sibling(Leo, Anything) <= sibling(Declan, Anything)),
                                   sibling(Leo, Milo) <= language.TRUE)]
    assert len(list(baz.fetch(sibling(Leo, Milo)))) == 1
    assert list(baz.fetch(sibling(Leo, Milo)))[0].binding == {}
    assert list(baz.fetch(sibling(Leo, Milo)))[0].condition == language.TRUE


def test_trie_table():
    trie = TrieTable(foo.rules())
    assert tuple(trie.rules()) in [((sibling(Leo, Milo) <= language.TRUE,
                                    sibling(Leo, Anything) <= sibling(Declan, Anything))),
                                  ((sibling(Leo, Anything) <= sibling(Declan, Anything)),
                                   sibling(Leo, Milo) <= language.TRUE)]
    assert len(list(trie.fetch(sibling(Leo, Milo)))) == 1
    assert list(trie.fetch(sibling(Leo, Milo)))[0].binding == {}
    assert list(trie.fetch(sibling(Leo, Milo)))[0].condition == language.TRUE
