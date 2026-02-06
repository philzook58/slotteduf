import uf
from slotted_egraph import *
import pprint


def test_slotted_uf():
    suf = uf.SlottedUF()
    x = suf.makeset(3)
    y = suf.makeset(4)
    assert suf.find(x) == x
    assert suf.find(y) != x
    R = uf.Renaming.of_list([(slot, uf.fresh_slot()) for slot in x.slots()])
    assert suf.find(R * x) != suf.find(x)
    suf.union(x, y)
    assert suf.find(x) == suf.find(y)

    # all slots are now redundant because x and y share no slots
    # so a random rename should not change the find result
    assert suf.find(R * x) == suf.find(x)

    suf = uf.SlottedUF()
    x = suf.makeset(3)
    slots = list(x.slots())
    flip = uf.Renaming.of_list(zip(slots, slots[::-1]))
    suf.union(flip * x, x)
    flip * x
    # They actually still differ by a permutation, but it is in suf.symettries, which is_eq checks
    assert suf.find(flip * x) != suf.find(x)
    assert suf.is_eq(flip * x, x)
    # we added a flip
    assert len(suf.symmetries[x.id]) == 2
    shift = uf.Renaming.of_list(zip(slots, slots[1:] + slots[:1]))
    assert not suf.is_eq(shift * x, x)
    suf.union(shift * x, x)
    assert suf.is_eq(shift * x, x)
    assert len(suf.symmetries[x.id]) == 6

    p = [(slot, uf.fresh_slot()) for slot in x.slots()]
    p[0] = (p[0][0], uf.fresh_slot())
    R = uf.Renaming.of_list(p)
    assert not suf.is_eq(R * x, x)
    suf.union(R * x, x)
    assert suf.is_eq(R * x, x)
    assert len(suf.find(x).slots()) == 0
    assert len(suf.symmetries[suf.find(x).id]) == 1

    suf = uf.SlottedUF()
    x = suf.makeset(5)
    slots = list(x.slots())
    flip = list(zip(slots, slots))
    flip[0] = (slots[0], slots[1])
    flip[1] = (slots[1], slots[0])
    flip = uf.Renaming.of_list(flip)
    suf.union(flip * x, x)
    flip * x
    # They actually still differ by a permutation, but it is in suf.symettries, which is_eq checks
    assert suf.find(flip * x) != suf.find(x)
    assert suf.is_eq(flip * x, x)
    # we added a flip
    assert len(suf.symmetries[x.id]) == 2
    shift = uf.Renaming.of_list(zip(slots, slots[1:] + slots[:1]))
    assert not suf.is_eq(shift * x, x)
    suf.union(shift * x, x)
    assert suf.is_eq(shift * x, x)
    assert len(suf.symmetry_group(x)) == 120

    p = [(slot, uf.fresh_slot()) for slot in x.slots()]
    p[0] = (p[0][0], uf.fresh_slot())
    R = uf.Renaming.of_list(p)
    assert not suf.is_eq(R * x, x)
    suf.union(R * x, x)
    assert suf.is_eq(R * x, x)
    assert len(suf.find(x).slots()) == 0
    assert len(suf.symmetries[suf.find(x).id]) == 1


def test_symmetry():
    uf = uf.SlottedUF()
    x = uf.makeset(2)
    slots = list(x.slots())
    perm = uf.Renaming.of_list([(slots[0], slots[1]), (slots[1], slots[0])])
    x1 = perm * x
    uf.union(x, x1)
    assert uf.is_eq(x, x1)
    assert len(uf.symmetries[x.id].perms) == 2


"""
TODO:
Check that redundancy propagate symmetries properly
Quickcheck something?
"""


def test_basic():
    uf = uf.SlottedUF()
    x, y = [uf.makeset(2) for _ in range(2)]
    r = uf.Renaming.of_list(zip(y.slots(), x.slots()))
    y1 = r * y
    uf.union(x, y1)
    assert uf.is_eq(x, y1)
    assert not uf.is_eq(y, y1)  # don't even ahve the same domain
    assert uf.find(x).slots() <= x.slots()
    assert uf.find(y1).slots() <= x.slots()
    assert uf.find(y).slots() <= y.slots()

    # z = uf.makeset(1)
    # should destroy all slots
    uf.union(x, y)
    assert uf.find(x).slots() == set()
    assert uf.find(y1).slots() == set()


def test_egraph():
    E = EGraph()
    a = E.add_enode(AppNode("a", ()))
    b = E.add_enode(AppNode("b", (a,)))
    E.union(a, b)
    assert E.is_eq(a, b)

    v1 = E.add_enode(Var(uf.fresh_slot()))
    v2 = E.add_enode(Var(uf.fresh_slot()))
    assert len(E.memo) == 3

    def plus(x, y):
        return E.add_enode(AppNode("+", (x, y)))

    assert not E.is_eq(plus(v1, v2), plus(v2, v1))
    # In an ordinrary egraph, each plus would be separate entry in memo before union
    # Not so in slotted for variable renamed enodes
    assert len(E.memo) == 4
    E.union(plus(v1, v2), plus(v2, v1))
    assert E.is_eq(plus(v1, v2), plus(v2, v1))

    E = EGraph()
    a = E.add_enode(AppNode("a", ()))
    fa = E.add_enode(AppNode("f", (a,)))
    ffa = E.add_enode(AppNode("f", (fa,)))
    b = E.add_enode(AppNode("b", ()))
    fb = E.add_enode(AppNode("f", (b,)))
    ffb = E.add_enode(AppNode("f", (fb,)))
    E.union(a, b)
    assert not E.is_eq(ffa, ffb)
    E.rebuild()
    assert E.is_eq(ffa, ffb)

    E = EGraph()
    v1 = E.add_enode(Var(uf.fresh_slot()))
    v2 = E.add_enode(Var(uf.fresh_slot()))
    lam1 = E.add_enode(AppNode("lam", (v1, v1)))
    lam2 = E.add_enode(AppNode("lam", (v2, v2)))

    id2 = E.add_enode(AppNode("id", ()))
    assert not E.is_eq(lam1, lam2)
    E.union(lam1, id2)
    assert E.is_eq(lam1, lam2)
