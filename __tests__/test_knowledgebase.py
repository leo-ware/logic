from src.knowledgebase import *
from src.language import *


def test_kb():
    x, y, z = variables("XYZ")
    kb = KnowledgeBase([
        x & y <= z,
        z
    ])
    kb.tell(x)
    assert list(kb.fetch(z))
    # assert not list(kb.fetch(x))[0]
