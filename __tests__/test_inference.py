from src import *
from pytest import raises

sibling = functor("sibling", 2)
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


# def test_id():
#     assert {X: Leo} in list(id_ask(KB, sibling(X, Milo)))
#     assert {X: Declan} in list(id_ask(KB, sibling(X, Milo)))
#     assert list(id_ask(KB, sibling(Leo, Milo))) == [{}]
#     assert list(id_ask(KB, sibling(Declan, Milo))) == [{}]
#     assert list(id_ask(KB, sibling(Axel, Leo))) == []
#     assert list(id_ask(KB, sibling(Axel, X))) == []
