import typing
from pathlib import Path
from lark import Lark, Transformer

from src import language, knowledgebase

# get the right file regardless of working directory
filename = Path(__file__).parent / "prolog.lark"

# the file prolog.lark has ebnf for prolog
with open(filename) as f:
    parser = Lark(f)


class PrologTransformer(Transformer):

    def start(self, tree):
        return tree[0]

    def program(self, tree):
        return knowledgebase.KnowledgeBase(tree)

    def atom(self, tree):
        return language.Literal(tree[0])

    def var(self, tree):
        return language.Variable(str(tree[0]))

    def list(self, tree):
        return tuple(tree)

    def functor(self, tree):
        return tree[0]

    def compound(self, tree):
        return language.Compound(str(tree[0]), tuple(tree[1:]))

    def conj(self, tree):
        return language.And(tree)

    def disj(self, tree):
        return language.Or(tree)

    def neg(self, tree):
        return language.Not(tree[0])

    def rule(self, tree):
        return language.Rule(
            head=tree[0].children[0],
            body=tree[1].children[0]
        )

    # keywords
    def cuts(self, _):
        return language.CUT

    def true(self, _):
        return True

    def false(self, _):
        return False

    def fail(self, _):
        return language.FAIL


def prolog(pg: typing.Union[str, typing.IO]):
    """Parse a prolog program"""
    try:
        pg = pg.read()
    except AttributeError:
        pass

    parse_tree = parser.parse(pg)
    return PrologTransformer().transform(parse_tree)
