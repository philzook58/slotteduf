from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UF:
    """
    Basic union find without slots
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


@dataclass(frozen=True, order=True)
class Slot:
    """
    Slot = Variable
    Slotted = has holes you can fill with slots = parametrized

    Slots

    Free variables sometimes
    BVar(int) - a de bruijn variable
    FVar(int) - might be just a fresh counter or it might be a de beuijn level or (string, int) for fresh counter + name
    FVar(string)
    https://leanprover-community.github.io/mathlib4_docs/Lean/Expr.html#Lean.Expr

    Shape (numeric) slot != fvar. Where shape slots are normalized lexicographically in enodes. Maybe a bit more like a bvar https://www.swi-prolog.org/pldoc/man?predicate=numbervars/3
    fresh slots
    named slots

    ~bvar(int) in the sense that the integers refer to variables in a structurally defined way
    fresh_fvar(int)
    named_fvar(string)
    """

    name: int

    def __repr__(self):
        return f"${self.name}"


counter = 0


def fresh_slot():
    global counter
    counter += 1
    return Slot(counter)


# class Symmettry / Perm:? for self renames


@dataclass(frozen=True)
class Renaming:
    """
    A renaming is a mapping from slots to slots
    It is a bijective map (except in the case of redundancy mappings)
    The domain and codomain may not be the same set

    The main use case where they may be the same set is a symmetry.
    """

    map: frozenset[tuple[Slot, Slot]]

    @classmethod
    def of_list(cls, lst: list[tuple[Slot, Slot]]):
        return cls(frozenset(lst))

    def rev(self):
        return Renaming.of_list([(b, a) for (a, b) in self.map])

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
            if a == key:
                return b
        raise KeyError(key)

    def compose(self, q):
        """
        self : X -> Y
        q : Y -> Z
        self @ q : X -> Z
        """

        return Renaming.of_list([(a, q[b]) for (a, b) in self])

    def compose_partial(self, q):
        return Renaming.of_list([(a, q[b]) for (a, b) in self if b in q.keys()])

    def __matmul__(self, q):
        # self is renaming X -> Y
        # q is renaming Y -> Z
        # returns renaming X -> Z
        return self.compose(q)

    def __mul__(self, eid):
        # renaming * eid
        # takes eid : Y
        # self : Y -> Z
        # returns Z
        if isinstance(eid, int):
            return RenamedId(eid, self)
        elif isinstance(eid, RenamedId):
            # eid.id : X
            # eid.renaming : X -> Y
            # eid : Y
            # self : Y -> Z
            return RenamedId(eid.id, eid.renaming.compose(self))
        else:
            raise TypeError(eid)

    def __iter__(self):
        return iter(self.map)


def rename_to_fresh(slots: list[Slot]) -> tuple[list[Slot], Renaming]:
    freshs = [fresh_slot() for _ in slots]
    return freshs, Renaming.of_list(list(zip(slots, freshs)))


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

# rudi and michel hate these ^

type Id = int

"""
Conceptually
e3 =   {f(slot42, g(slot8)), }

Ids are handles to _actual_ sets of terms with slots at leaves.

e3 =   {f($42, a, g($8)), f() }

"""


@dataclass(frozen=True)
class RenamedId:
    # gid : AppliedEId
    id: Id
    renaming: Renaming

    def __repr__(self):
        return f"{self.renaming} * id{self.id}"

    def __getitem__(self, idx: int) -> Slot:
        return sorted(self.renaming.values())[idx]

    def slots(self):
        return set(self.renaming.values())


# A perm is a renaming, where keys = values.
type Perm = Renaming


class Group:
    perms: set[Renaming]

    def __init__(self, elems: set[Slot]):
        identity = Renaming.of_list(list(zip(elems, elems)))
        self.perms = {identity}

    def contains(self, p: Perm):
        return p in self.perms

    def add(self, p: Perm):
        self.perms.add(p)
        self.complete()

    def complete(self):
        while True:
            cnt = len(self.perms)
            newperms = []
            for p in self.perms:
                newperms.append(p.rev())
            for p1 in self.perms:
                for p2 in self.perms:
                    newperms.append(p1.compose(p2))
            self.perms.update(newperms)
            if cnt == len(self.perms):
                break

    def orbit(self, slot: Slot) -> set[Slot]:
        return {p.get(slot) for p in self.perms}


def test_group():
    s1 = fresh_slot()
    s2 = fresh_slot()
    s3 = fresh_slot()
    g = Group({s1, s2, s3})
    p12 = Renaming.of_list([(s1, s2), (s2, s1), (s3, s3)])
    p23 = Renaming.of_list([(s2, s3), (s3, s2), (s1, s1)])
    g.add(p12)
    g.add(p23)
    assert g.contains(p12.compose(p23))


"""
Conceptually a renamed slot is the same set as the id, but with the slots renamed

(e3, [$42 -> $7, $8 -> $14]) =   {f($7, a, g($14)), ... }


id: Id # :: X
renaming: Renaming # :: X -> Y

where X is a set of slots like {$42, $8} and Y is a set of slots like {$7, $14}

So things kind of need to "type check" to make any sense at all.

"""

# rename @ {f(slots[0], g(slots[1])), ...} = {f(renaming(slots[0]), g(renaming(slots[1])), ...}

"""
3 main interpretations of what eids might mean (even ignoring slots):
1. eid is exactly one syntactic term, like in a hashcons
2. eid is a set of terms considered to be equivalent for some purposes {1 + 2, 2 + 1, 3} A set of meaningless structural terms
3. eid refers to exactly one semantic entity, which is somehow a quotient of a term by it's equivalent terms  (1 + 2) == (2 + 1) == 3. Different syntaxtic terms but they "are" the same things interpreted in the Naturals.

Another distinction: 
a. Do eids refer to one term
b. do they refer to exactly one set at the time of creation (aegraph style)
c. do they desctrively refer to the current understanding of that equivalence class, which grows with unions. This is a conceptual choice.

In 3, a identity rename is TRULY equal to the eids itself. In this sense, RenamedId can equal an Id.


Interpreting eids as sets of terms
1a. The mapping term -> term. Can be interpreted as ground rewrite rule. The mapping is convergent.
1b. 
1c.
2b. find turns a set into a bigger set
2c. `find` is a an identity function
3. `find` is an identity function


slotted:
1. e14 = f($42, $17)
2. e14 = {f($42, $17), f($17, $42)}
3. Rudi lives in here.

All interpretations still exists but note slots are SERIOUS. They really refer to _exactly_ those slot numbers.

In unification variables, not slots: f(X,Y) I don't mean "just" f(X,Y) that's what I mean by serious. I often kind of mean {f(X,Y), f(Y,X), f(A,B), ...} (what?)"unserious". `fun (X,Y) => f(X,Y)` sometimes.  or do I mean `fun {X,Y} => f(X,Y)` or  `fun {x=_,y=_} => f(x,y)` keyword arguments

Are shape slots for serious?

"""

"""

Rudi kind of wants everything to always have been a RenamedId. Id is an implementation detail. Id has a meaningless choice of what slots ended being slot set of the terms that correspond to that Id.

User never gets access to Id.

"""

"""
Shoudl Keyword Id be a idfferent type from slot? and then split Renaming into keywrod -> slot mappings, and perm = slot -> slot, keyword -> keyword mapping

"""


@dataclass
class SlottedUF:
    # These are implementation details.
    # Look at API
    uf: list[RenamedId] = field(
        default_factory=list
    )  # Id -> RenamedId. Really wanted RenamedId -> RenamedId conceptually. But doing it this way is deduplicating in exactly the way we want to be deduplicating.
    public_slots: dict[Id, set[Slot]] = field(default_factory=dict)
    symmetries: dict[Id, Group] = field(default_factory=dict)
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
        eid = RenamedId(n, Renaming.of_list([(a, a) for a in slots]))
        self.uf.append(eid)
        self.public_slots[n] = set(slots)
        self.symmetries[n] = Group(set(slots))
        return eid

    def find(self, ma: RenamedId) -> RenamedId:
        # U[m*a] = m*U[id*a] = m*(m'*b)
        # find[m*a] = m*find[id*a] = m*uf[a] = m*(m'*b) = (m o m')*b
        assert isinstance(ma, RenamedId)
        rename = ma.renaming
        a = ma.id  # This is kind of a canonization step. Turning a renamed thing into a "canonical" named version of it
        while True:
            mb = self.uf[a]
            rename = mb.renaming @ rename
            if mb.id == a:
                return RenamedId(id=a, renaming=rename)
            a = mb.id

    """
    {f($42)} Union {f($31)}---> discover redundancy ---> {f($0}, f($1), f($2), ...} which is a _big_ semantic move, but a small implementation move.

    public_slots({f($42)}) = {$42}
    NO!!!: public_slots({f($0}, f($1), f($2), ...}) = {$0, $1, $2, ...}
    slots(f($42, $13)) = {$42, $13}
    public_slots({t1, t2, t3, ...}) = intersection({slots(t1), slots(t2), slots(t3), ...})
    
    
    union($x - $x, $y - $y)
    2 choices: mutatate old public slots or make new eclass e, with less slots and union to it. This is like style b above ie. aegraphs.


    Ok. Now let's consider symmettrices

    {f($42, $13} -perm-> {f($13, $42)} 

    {f($42, $13, f($13, $42)} 

    """

    def shrink_slots(self, a: RenamedId, remaining_slots: set[Slot]):
        pslots = self.public_slots[a.id]
        assert pslots >= remaining_slots
        if pslots == remaining_slots:
            return  # nothing to do
        """
        We need to lose all the the slots related to the losing slots by symmettry
        """
        G = self.symmetries[a.id]
        losing_slots = {slot for s in pslots - remaining_slots for slot in G.orbit(s)}
        remaining_slots = remaining_slots - losing_slots
        b = self.makeset(len(remaining_slots))

        # a.id : X
        # a.m : X -> Y
        # a : Y
        # remaining_slots : Y
        # pslots : Y
        # b : Z
        # need renaming : Z -> X
        r = Renaming.of_list(list(zip(b.renaming.values(), remaining_slots)))  # Z -> Y
        renaming = r @ a.renaming.rev()  # Z -> X
        self.uf[a.id] = RenamedId(renaming=renaming, id=b.id)
        for perm in self.symmetries[a.id].perms:
            self.symmetries[b.id].add(
                renaming.compose_partial(perm.compose_partial(renaming.rev()))
            )

    def union(self, a: RenamedId, b: RenamedId) -> bool:
        # union(self, m1*a1, m2*a2)
        # union(self, U[m1*a1], U[m2*a2])
        # union(self, m3 * a3, m4 * a4)
        # union(self, id * a3, (m3^-1 o m4) * a4)
        # ufunion(self, a3, (m3^-1 o m4) * a4)
        #
        while True:
            a, b = self.find(a), self.find(b)
            aslots = set(a.renaming.values())
            bslots = set(b.renaming.values())
            if aslots != bslots:
                self.shrink_slots(a, aslots & bslots)
                self.shrink_slots(b, aslots & bslots)
                # redundant slots
            else:
                break
            #    a.rev()[]
        a, b = self.find(a), self.find(b)
        if a.id != b.id:
            # TODO: merge symmettries
            m = b.renaming.compose(a.renaming.rev())
            # a : Z
            # a.id : X
            # b.id : Y
            # a.renaming : X -> Z
            # b.renaming : Y -> Z
            # m = b.renaming @ a.renaming.rev : Y -> X
            # b : Z
            # perm : X -> X
            # m @ perm @ m.rev : Y -> Y
            for perm in self.symmetries[a.id].perms:
                self.symmetries[b.id].add(m @ perm @ m.rev())
            self.uf[a.id] = RenamedId(id=b.id, renaming=m)
            return True
        else:
            self.symmetries[a.id].add(a.renaming.rev() @ b.renaming)
            return False

    def is_eq(self, a: RenamedId, b: RenamedId) -> bool:
        a = self.find(a)
        b = self.find(b)
        if set(a.renaming.values()) != set(b.renaming.values()):
            return False
        # but actually symmettries
        # a.id : X
        # a.renaming : X -> Y
        # b.id : X
        # b.renaming : X -> Y
        # a.renaming @ b.renaming.rev() : X -> X
        return (
            a.id == b.id
            and a.renaming @ b.renaming.rev() in self.symmetries[a.id].perms
        )
        # all(
        #    a.renaming.get(s) == b.renaming.get(s) for s in a.renaming.keys()
        # )


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


def test_symmettry():
    uf = SlottedUF()
    x = uf.makeset(2)
    perm = Renaming.of_list([(x[0], x[1]), (x[1], x[0])])
    x1 = perm * x
    uf.union(x, x1)
    assert uf.is_eq(x, x1)
    assert len(uf.symmetries[x.id].perms) == 2


"""
TODO:
Check that redundancy propagate symmettries properly
Quickcheck something?
"""


def test_basic():
    uf = SlottedUF()
    x, y = [uf.makeset(2) for _ in range(2)]
    slotsy = list(uf.public_slots[y.id])
    slotsx = list(uf.public_slots[x.id])

    # y1 = RenamedId(y.id, Renaming([(slotsy[0], slotsx[1]), (slotsy[1], slotsx[0])]))
    r = Renaming.of_list([(x[0], y[0]), (x[1], y[1])]).rev()
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


"""
Example showing that redundancy + symmetry causes new redundancy (i.e. orbit wide redundancies)

i1(x, y) = i1(y, x)
i1(x, y) = i2(y)

i1(x, y) = i2(y)
->
i1(x, y) = i1(a, b)

i1(x, y)
= i2(y)
= i1(b, y)
= i1(y, b)
= i2(b)
= i1(a, b)

i(x, y, z) = i(z, y, x)
i(x, y, z) = j(y, z)
|
x redundant
=> z redundant

=> second arg of j is redundant.

Thus symmetries might cause redundancies to propagate new redundancies.

"""
