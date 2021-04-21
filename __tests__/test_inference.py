from src import *
from pytest import raises

sibling = functor("sibling", 2)
X, Y, Z = variables("XYZ")
Leo = Term("Leo")
Milo = Term("Milo")
Declan = Term("Declan")
Axel = Term("Axel")

KB = KnowledgeBase(LinearTable(), [
    sibling(Milo, Leo),
    sibling(Leo, Declan),
    sibling(X, Y) <= sibling(Y, X),
    sibling(X, Y) <= sibling(X, Z) & sibling(Z, Y),
])


def test_fc():
    assert {X: Leo} in list(fc_ask(KB, sibling(X, Milo)))
    assert {X: Declan} in list(fc_ask(KB, sibling(X, Milo)))
    assert list(fc_ask(KB, sibling(Leo, Milo))) == [{}]
    assert list(fc_ask(KB, sibling(Declan, Milo))) == [{}]
    assert list(fc_ask(KB, sibling(Axel, Leo))) == []
    assert list(fc_ask(KB, sibling(Axel, X))) == []


def test_bc():
    assert {X: Leo} == next(bc_ask(KB, sibling(X, Milo)))
    assert next(bc_ask(KB, sibling(Leo, Milo))) == {}
    with raises(RecursionError):
        next(bc_ask(KB, sibling(Axel, Leo)))
