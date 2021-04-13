from src.language import *


def test_term():
    term = Term()
    x = Variable("X")
    assert term & term == And([term, term])
    assert x in (x & 'foo')


def test_and():
    x, y, z = Variable("X"), Variable("Y"), Variable("Z")
    assert (x & (y & z)) == (x & y & z) == And([x, y, z])
    assert (x & y).first == x
    assert (x & y).rest == And([y])
    assert iter(x & y)


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
