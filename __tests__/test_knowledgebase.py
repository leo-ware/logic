from src import *

from pytest import raises

x, y, z = variables("xyz")
harry = Term("harry")
hermione = Term("hermione")
ron = Term("ron")
dumbledore = Term("dumbledore")
friends = functor("friends")

foo = KnowledgeBase(LinearTable(), [
    friends(harry, ron) & friends(dumbledore, harry),
    friends(x, y) <= friends(y, x)
])


def test_kb_tell():
    with raises(ValueError):
        foo.tell(friends(ron, dumbledore) | friends(dumbledore, ron))


def test_kb_fetch():
    thing = list(foo.fetch(friends(harry, x)))
    assert len(thing) == 1
    assert thing[0].binding == {x: ron}
    assert [r.binding for r in foo.fetch(friends(x, y))] in [
        [{x: harry, y: ron}, {x: dumbledore, y: harry}],
        [{x: dumbledore, y: harry}, {x: harry, y: ron}]
    ]
    assert list(foo.fetch(friends(harry, hermione), conditional=True))


def test_kb_fetch_bindings():
    assert list(foo.fetch(friends(x, y), binding={x: harry}))[0].binding == {x: harry, y: ron}
    assert list(foo.fetch(friends(x, y), binding={x: ron})) == []


def test_kb_fetch_join():
    assert {x: dumbledore, y: harry, z: ron} in [r.binding for r in foo.fetch(friends(x, y) & friends(y, z))]
    or_result = [r.binding for r in list(foo.fetch(friends(x, harry) | friends(harry, x)))]
    assert len(or_result) == 2
    assert {x: ron} in or_result
    assert {x: dumbledore} in or_result
