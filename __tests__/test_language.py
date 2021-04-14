from src.language import *


def test_and():
    x, y, z = Variable("X"), Variable("Y"), Variable("Z")
    assert (x & (y & z)) == (x & y & z) == And([x, y, z])
    assert (x & y).first == x
    assert (x & y).rest == And([y])
    assert iter(x & y)


def test_or():
    x, y, z = Variable("X"), Variable("Y"), Variable("Z")
    assert (x | (y | z)) == (x | y | z) == Or([x, y, z])
    assert (x | y).first == x
    assert (x | y).rest == Or([y])
    assert iter(x & y)


def test_neg():
    x, y = variables("XY")
    assert ~x == -x == Not(x)
    assert ~(x & y) == Not(And([x, y]))


def test_oops():
    x, y, z = Variable("X"), Variable("Y"), Variable("Z")
    assert x & y | z in [
        Or([And([x, y]), z]),
        Or([And([y, x]), z]),
        Or([z, And([x, y])]),
        Or([z, And([y, x])])
    ]
    assert isinstance(x & y | z <= y, Rule)
    assert isinstance(-x & y, And)
    assert isinstance(~(x & y) | z, Or)


def test_compound():
    x, y, z = Variable("X"), Variable("Y"), Variable("Z")
    foo = Compound("bigger", (x, 1))
    assert foo.op == 'bigger'
    assert foo.args == (x, 1)


def test_substitute():
    x, y, z = Variable("X"), Variable("Y"), Variable("Z")
    foo = Compound("bigger", (x, 1))
    a, b = foo.substitute({x: 'foo'}), Compound("bigger", ('foo', 1))

    assert a.op == b.op
    assert a.args == b.args
    assert (x & y).substitute({x: 'foo'}) == And(['foo', y])
    assert (x & ((x & z) & y) & z).substitute({z: 'foo'}) == (x & ((x & 'foo') & y) & 'foo')


def test_standardize():
    x, y, z = Variable("X"), Variable("Y"), Variable("Z")
    assert standardize_variables(x, _id=10) == Variable("X", 10)
