from src.unification import *
from src.language import *


def test_occur_check():
    x, y = Variable("X"), Variable("Y")
    assert occur_check(x, x)
    assert occur_check(x, x & y)
    assert not occur_check(x, y)


def test_tuple():
    x, y, z = variables("xyz")
    assert unify((1, 2, 3), (x, y, z)) == {x: 1, y: 2, z: 3}
    assert unify((1, 2, 3), (1, x, 3)) == {x: 2}


def test_tail():
    x, y, z = variables("xyz")
    assert unify((1, 2, 3), (x, +y)) == {x: 1, y: (2, 3)}
    assert unify((1, 2), (x, 2, +y)) == {x: 1, y: ()}
    assert unify((1, +x, 3), (1, 2, 3)) == FAIL
    assert unify((+x, y), (1, 2)) == FAIL
