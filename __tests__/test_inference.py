from src import *

sibling = functor("sibling", 2)
friend = functor("friend", 2)
X, Y, Z = variables("XYZ")
Leo = Term("Leo")
Milo = Term("Milo")
Declan = Term("Declan")
Axel = Term("Axel")

KB = LinearTable([
    sibling(Milo, Leo),
    sibling(Leo, Declan),
    sibling(X, Y) <= sibling(Y, X),
    sibling(X, Y) <= sibling(X, Z) & sibling(Z, Y),
    friend(X, Y) <= friend(X, Z) & sibling(Y, Z),
])

obvious_reality = Term("obvious reality")
trap = LinearTable([
    obvious_reality <= obvious_reality,
    obvious_reality
])


def test_fc():
    assert {X: Leo} in list(fc_ask(KB, sibling(X, Milo)))
    assert {X: Declan} in list(fc_ask(KB, sibling(X, Milo)))
    assert list(fc_ask(KB, sibling(Leo, Milo))) == [{}]
    assert list(fc_ask(KB, sibling(Declan, Milo))) == [{}]
    assert list(fc_ask(KB, sibling(Axel, Leo))) == []
    assert list(fc_ask(KB, sibling(Axel, X))) == []


def test_bc():
    assert next(bc_ask(KB, sibling(Leo, Milo))) == {}
    assert {X: Leo, Y: Milo} in take(10, bc_ask(KB, sibling(X, Y)))


def test_id():
    assert next(id_ask(KB, sibling(Leo, Milo))) == {}
    assert {X: Leo, Y: Milo} in take(10, id_ask(KB, sibling(X, Y)))
    assert next(id_ask(trap, obvious_reality)) == {}
