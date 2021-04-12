from src.parser import *
from src.language import *
from src.knowledgebase import KnowledgeBase


def test_program_parser():
    x = Variable("X")
    foo = functor('foo')
    bar = functor('bar')
    bang = functor('bang')

    assert prolog("X") == x
    assert prolog("leo") == Literal("leo")
    assert prolog("foo(X)") == foo(x)
    assert prolog("foo(X) :- bar(X)") == (foo(x) <= bar(x))
    assert prolog("foo(X) :- bar(X), bang(X)") == (foo(x) <= bar(x) & bang(x))
    assert prolog("foo(X) :- bar(X).") == KnowledgeBase([foo(x) <= bar(x)])
