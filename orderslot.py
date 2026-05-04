from dataclasses import dataclass, field

type SlotNum = int
type Id = int


@dataclass(frozen=True)
class AppliedId:
    id: Id
    slots: tuple[SlotNum]

    def __post_init__(self):
        assert len(set(self.slots)) == len(self.slots), "duplicate slots not allowed"
        assert sorted(self.slots) == list(self.slots), "slots must be sorted"
        assert isinstance(self.slots, tuple), "slots must be a tuple"

    def rename(self, new_slots: tuple[SlotNum]):
        assert len(new_slots) == len(self.slots), "arity must be preserved"
        assert sorted(new_slots) == list(new_slots), "slots must be sorted"
        assert len(set(new_slots)) == len(new_slots), "duplicate slots not allowed"
        assert isinstance(new_slots, tuple), "new_slots must be a tuple"
        return AppliedId(self.id, new_slots)


@dataclass(frozen=True)
class Node:
    f: str
    args: tuple[AppliedId]


@dataclass(frozen=True)
class Var:
    slot: SlotNum


"""
e1(0,1,2) -> e2(0,2) 
"""


@dataclass
class EGraph:
    memo: dict[Node, AppliedId] = field(default_factory=dict)
    # nodes = list[Node]
    uf: list[AppliedId] = field(default_factory=list)

    def __post_init__(self):
        self.memo[Var(0)] = self.makeset(1)

    def find(self, x: AppliedId) -> AppliedId:
        id = x.id
        slots = x.slots
        while True:
            y = self.uf[id]
            slots = tuple(slots[i] for i in y.slots)
            if y.id == id:
                return AppliedId(id, slots)

            id = y.id

    def makeset(self, arity: int) -> AppliedId:
        id = len(self.uf)
        aid = AppliedId(id, tuple(range(arity)))
        self.uf.append(aid)
        return aid

    def shrink(self, x: AppliedId, slots: tuple[SlotNum]) -> AppliedId:
        if x.slots == slots:
            return x
        else:
            newid = self.makeset(len(slots))
            self.uf[x.id] = newid.rename(tuple(x.slots.index(s) for s in slots))
            return self.find(x)

    def union(self, x: AppliedId, y: AppliedId):
        x = self.find(x)
        y = self.find(y)
        if x.slots != y.slots:
            common_slots = tuple(sorted(set(x.slots) & set(y.slots)))
            x = self.shrink(x, common_slots)
            y = self.shrink(y, common_slots)
        if x == y:
            return
        else:
            assert x.slots == y.slots
            self.uf[x.id] = AppliedId(y.id, tuple(range(len(x.slots))))

    def app(self, f: str, *args):
        args = [self.find(arg) for arg in args]
        all_slots = tuple(sorted(set().union(*[set(arg.slots) for arg in args])))
        norm_args = tuple(
            AppliedId(arg.id, tuple(all_slots.index(s) for s in arg.slots))
            for arg in args
        )
        node = Node(f, norm_args)
        id = self.memo.get(node)
        if id is None:
            id = self.makeset(len(all_slots))
            self.memo[node] = id
        return id.rename(all_slots)

    def var(self, slot: SlotNum):
        return self.memo[Var(0)].rename((slot,))


E = EGraph()
x = E.makeset(2)
y = E.makeset(2)
E.union(x, y)

x1 = x.rename((33, 44))
y1 = y.rename((33, 44))
assert E.find(x1) == E.find(y1)
# print(x1, y1, E.find(x1), E.find(y1))
# E.union(x, y)

E = EGraph()
v0 = E.var(0)
v1 = E.var(1)
v34 = E.var(34)
a = E.app("a")
b = E.app("b")


E = EGraph()
v0 = E.var(0)
v1 = E.var(1)
f1 = E.app("f", v0, v1)
f2 = E.app("f", v1, v0)
E.union(f1, f2)
assert E.find(f1) == E.find(f2)

f3 = E.app("f", v34, v1)
assert E.find(f1).rename((1, 34)) == E.find(f3)


E = EGraph()
v0 = E.var(0)
v20 = E.var(20)
a = E.app("a")
E.union(a, v0)
assert E.find(a) == E.find(v0)
assert E.find(v20).slots == ()

E = EGraph()
v0 = E.var(0)
v1 = E.var(1)
a = E.app("a")
f1 = E.app("f", v0, v1)
f2 = E.app("f", v1, a)
E.union(f1, f2)
assert E.find(f1) == E.find(f2)
assert E.find(f1).slots == (1,)
assert E.find(a) != E.find(v0)

"""

            res = []
            if len(y.slots) > 0:
                j = 0
                for i 
                for i, s in enumerate(slots):
                    if y.slots[j] == i:
                        j += 1 
                        res.append(s)
            slots = res
"""
