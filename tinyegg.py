# from Rudi
from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    f: str
    args: tuple["Id"]

    def __str__(self):
        if self.args == ():
            return self.f
        return self.f + "(" + ", ".join(map(str, self.args)) + ")"


# We use ptrs as Ids.
class Id:
    pass


class EGraph:
    def __init__(self):
        # combines hashcons & unionfind into one thing.
        # the hashcons_uf takes in a "thing" and returns a "more canonical thing".
        self.hashcons_uf = {}

    # combines find & lookup & add & add_expr into one thing.
    def find_add_expr(self, x) -> Id:
        # This part comes from add/lookup
        if isinstance(x, Node):
            x = Node(x.f, tuple([self.find_add_expr(a) for a in x.args]))

        # This part comes from find.
        if x in self.hashcons_uf:
            x = self.hashcons_uf[x]

        if isinstance(x, Node):
            # This comes from add
            i = Id()
            self.hashcons_uf[x] = i
            return i
        else:
            return x

    def union(self, x, y):
        x = self.find_add_expr(x)
        y = self.find_add_expr(y)
        if x == y:
            return

        self.hashcons_uf[x] = y
        self.rebuild_path_compress()

    # combines rebuilding & path compression
    def rebuild_path_compress(self):
        for k, v in list(self.hashcons_uf.items()):
            # comes from rebuild
            if isinstance(k, Node):
                k = Node(k.f, tuple([self.find_add_expr(a) for a in k.args]))
            vv = self.find_add_expr(v)
            if k in self.hashcons_uf:
                self.union(vv, self.hashcons_uf[k])
            else:
                self.hashcons_uf[k] = vv

    def is_equal(self, x, y):
        x = self.find_add_expr(x)
        y = self.find_add_expr(y)
        return x == y


a = Node("a", ())
b = Node("b", ())
f = lambda x, y: Node("f", (x, y))

eg = EGraph()

i1 = eg.find_add_expr(f(a, b))
i2 = eg.find_add_expr(f(b, a))

eg.union(a, b)

print(eg.is_equal(i1, i2))
