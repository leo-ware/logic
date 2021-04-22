from src import *

x, y = variables("xy")
Leo = Term("Leo")
Declan = Term("Declan")
sibling = functor("sibling")

foo = LinearTable([
    sibling(Leo, Declan),
    sibling(Leo, Leo)
])


def test_Eq():
    assert list(Equals(x, Leo).test({x: Leo}))
    assert list(Equals(sibling(x, y), sibling(Leo, Declan)).test({}))
    assert not list(Equals(x, Leo).test({x: Declan}))
