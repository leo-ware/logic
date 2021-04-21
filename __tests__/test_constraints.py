from src import *

x = Variable("x")
Leo = Term("Leo")
Declan = Term("Declan")
sibling = functor("sibling")

foo = KnowledgeBase(LinearTable(), [
    sibling(Leo, Declan),
    sibling(Leo, Leo)
])


def test_Eq():
    assert next(foo.fetch(sibling(Leo, x) & Not(Equals(Leo, x)))).binding == {x: Declan}


def test_LE():
    assert next(foo.fetch(LE(1, 2))).binding == {}
    assert list(foo.fetch(LE(2, 1))) == []
    assert list(foo.fetch(LE(x, 1))) == []
