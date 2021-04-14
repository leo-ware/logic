from src import *

kb = prolog("""

wizard(X) :-
    guy(X),
    magical(X).

witch(X) :-
    girl(X),
    magical(X).

has_wand(X) :- magical(X).

girl(hermione).
guy(harry).
guy(ron).
guy(dudley).

magical(hermione).
magical(harry).
magical(ron).

""")

X = Variable("X")
wizard = functor("wizard")
witch = functor("witch")
guy = functor("guy")
hermione = Literal("hermione")


def test_queries_bc():
    assert set(str(i) for i in bc_ask(kb, wizard(X))) == {"{X: harry}", "{X: ron}"}
    assert set(str(i) for i in bc_ask(kb, guy(X))) == {"{X: harry}", "{X: ron}", "{X: dudley}"}
    assert list(bc_ask(kb, witch(X))) == [{X: hermione}]


def test_queries_fc():
    assert set(str(i) for i in fc_ask(kb, wizard(X))) == {"{X: harry}", "{X: ron}"}
    assert set(str(i) for i in fc_ask(kb, guy(X))) == {"{X: harry}", "{X: ron}", "{X: dudley}"}
    assert list(fc_ask(kb, witch(X))) == [{X: hermione}]
