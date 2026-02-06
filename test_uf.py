import uf
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
