from src.inference import *
from src.language import *
from src.knowledgebase import KnowledgeBase

sibling = functor("sibling", 2)
X, Y, Z = variables("XYZ")
Leo = Literal("Leo")
Milo = Literal("Milo")
Declan = Literal("Declan")

KB = KnowledgeBase([
    sibling(X, Y) <= sibling(Y, X),
    sibling(X, Y) <= sibling(X, Z) & sibling(Z, Y),
    sibling(Milo, Leo),
    sibling(Leo, Declan)
])


def test_fc():
    assert list(fc_infer(KB, sibling(X, Milo))) == [{X: Leo}, {X: Declan}]
    assert list(fc_infer(KB, sibling(Leo, Milo))) == [{}]
    assert list(fc_infer(KB, sibling(Declan, Milo))) == [{}]
