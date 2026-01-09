from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UF:
    """
    Basic unuion find without slots
    >>> uf = UF()
    >>> x,y,z = [uf.makeset() for _ in range(3)]
    >>> uf.union(x,y)
    >>> uf
    """

    parents: list[int] = field(default_factory=list)

    def makeset(self):
        n = len(self.parents)
        self.parents.append(n)
        return n

    def find(self, a):
        while self.parents[a] != a:
            a = self.parents[a]
        return a

    def union(self, a, b):
        a = self.find(a)
        b = self.find(b)
        if a != b:
            self.parents[a] = b
        return b

    def is_eq(self, x, y):
        return self.find(x) == self.find(y)


@dataclass(frozen=True)
class Slot:
    name: int

    def __repr__(self):
        return f"${self.name}"


counter = 0


def fresh_slot():
    global counter
    counter += 1
    return Slot(counter)


@dataclass(frozen=True)
class Renaming:
    """
    A renaming is a mapping from slots to slots
    It is a bijective map.
    The domain and codomain may not be the same set
    """

    map: list[tuple[Slot, Slot]]

    def rev(self):
        return Renaming([(b, a) for (a, b) in self.map])

    def keys(self):
        return [a for (a, b) in self.map]

    def values(self):
        return [b for (a, b) in self.map]

    def get(self, key: Slot):
        for a, b in self.map:
            if a == key:
                return b
        return key

    def __getitem__(self, key: Slot):
        for a, b in self.map:
            print((a, b, key))
            if a == key:
                return b
        raise KeyError(key)

    def compose(self, q):
        return Renaming([(a, q[b]) for (a, b) in self])

    def __iter__(self):
        return iter(self.map)


"""
@dataclass(frozen=True)
class UnAppliedEId:
    id: int
    arity: int


# semsntically, function from names to a set of named terms
# fun name1 name2 => {f(name1, g(name2)), ...}


@dataclass(frozen=True)
class AppliedEId:
    fid: UnAppliedEId
    slots: list[Slot]

    @property
    def public_slots(self):
        return set(self.slots)
"""

# rudi and mhicel hate these ^

type Id = int


@dataclass(frozen=True)
class RenamedId:
    # gid : AppliedEId
    id: Id
    renaming: Renaming

    def __repr__(self):
        return f"{self.id} @ {self.renaming}"


# rename @ {f(slots[0], g(slots[1])), ...} = {f(renaming(slots[0]), g(renaming(slots[1])), ...}


@dataclass
class SlottedUF:
    uf: list[RenamedId] = field(default_factory=list)
    public_slots: dict[Id, set[Slot]] = field(default_factory=dict)
    # uf table is conceptually identity function. Yeaaaa?
    # uf : list[tuple[Renaming, Id]]

    """
    def makeset(
        self, slots: list[Slot]
    ) -> RenamedId:  # it will be an identity tranformation
        " should makeset takes slots of just an arity. Rudi says fresh slots are less error prone"
        n = len(self.uf)
        eid = RenamedId(n, Renaming([(a, a) for a in slots]))
        self.uf.append(eid)
        self.public_slots[n] = set(slots)
        return eid
    """

    def makeset(self, arity: int) -> RenamedId:  # it will be an identity tranformation
        """
        Make a renamed id with identity trasnformatio
        """
        slots = [fresh_slot() for _ in range(arity)]
        n = len(self.uf)
        eid = RenamedId(n, Renaming([(a, a) for a in slots]))
        self.uf.append(eid)
        self.public_slots[n] = set(slots)
        return eid

    def find(self, ma: RenamedId) -> RenamedId:
        rename = ma.renaming
        a = ma.id
        while True:
            mb = self.uf[a]
            print(rename)
            rename = mb.renaming.compose(rename)
            print(rename)
            if mb.id == a:
                return RenamedId(id=a, renaming=rename)
            a = mb.id

    def union(self, a: RenamedId, b: RenamedId) -> bool:
        set(a.renaming.values()) != set(b.renaming.values())
        # if :
        #    # redundant slots
        #    a.rev()[]
        a, b = self.find(a), self.find(b)
        print(a, b)
        if a.id != b.id:
            self.uf[a.id] = RenamedId(b.id, b.renaming.compose(a.renaming.rev()))
            return True
        else:
            # symmettries
            return False

    def is_eq(self, a: RenamedId, b: RenamedId) -> bool:
        a = self.find(a)
        b = self.find(b)
        # but actually symmettries
        return a.id == b.id and all(
            a.renaming.get(s) == b.renaming.get(s) for s in a.renaming.keys()
        )


"""
uf = SlottedUF()
slots1 = [fresh_slot() for _ in range(2)]
x = uf.makeset(slots1)
slots2 = [fresh_slot() for _ in range(2)]
y = uf.makeset(slots2)


y = RenamedId(id=y.id, renaming=Renaming([(slots2[1], slots1[0]), (slots2[0], slots1[1])]))
uf.union(x,y)
uf
x,y
uf
"""
uf = SlottedUF()
x, y, z = [uf.makeset(2) for _ in range(3)]
slotsy = list(uf.public_slots[y.id])
slotsx = list(uf.public_slots[x.id])

y1 = RenamedId(y.id, Renaming([(slotsy[0], slotsx[1]), (slotsy[1], slotsx[0])]))

uf.union(x, y1)
uf, x, y
