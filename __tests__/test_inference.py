from src.inference import *
from src.language import *
from src.knowledgebase import KnowledgeBase

sibling = functor("sibling", 2)
X, Y, Z = variables("XYZ")
Leo = Literal("Leo")
Milo = Literal("Milo")
Declan = Literal("Declan")
Axel = Literal("Axel")

KB = KnowledgeBase([
    sibling(X, Y) <= sibling(Y, X),
    sibling(X, Y) <= sibling(X, Z) & sibling(Z, Y),
    sibling(Milo, Leo),
    sibling(Leo, Declan)
])


def howto_test_inference(inf):
    assert {X: Leo} in list(inf(KB, sibling(X, Milo)))
    assert {X: Declan} in list(inf(KB, sibling(X, Milo)))
    assert list(inf(KB, sibling(Leo, Milo))) == [{}]
    assert list(inf(KB, sibling(Declan, Milo))) == [{}]
    assert list(inf(KB, sibling(Axel, Leo))) == []
    assert list(inf(KB, sibling(Axel, X))) == []


def test_fc():
    howto_test_inference(fc_ask)


def test_bc():
    howto_test_inference(bc_ask)
