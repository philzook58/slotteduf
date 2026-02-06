from uf import SlottedUF, Renaming, Slot, RenamedId, fresh_slot
from dataclasses import dataclass, field

"""
class SlotApp():
    rid : uf.RenamedId # Id?
    args : list[uf.RenamedId]
"""

@dataclass(frozen=True)
class App():
    op: str
    args: tuple["Term", ...]

@dataclass(frozen=True)
class TermBinder():
    bvar: str
    body: "Term"

# sum(bind x. x + 1)

@dataclass(frozen=True)
class TermVar():
    name: str

type Term = App | TermBinder | TermVar




@dataclass(frozen=True)
class AppNode():
    op: str
    children: tuple[RenamedId, ...]

    @property
    def slots(self) -> set[Slot]:
        return set.union(*[child.slots() for child in self.children])
    
    def apply_rename(self, R: Renaming) -> "AppNode":
        return AppNode(
            self.op,
            tuple(R * child for child in self.children)
        )

@dataclass(frozen=True)
class BNode():
    # binder node
    bvar : Slot # tuple[Slot] # multi binder can be nice
    child : RenamedId

@dataclass(frozen=True)
class Var(): # kind of "RenamedVar"
    name : Slot
    
    @classmethod
    def fresh(cls) -> "Var":
        return Var(fresh_slot())


type ENode = AppNode | BNode | Var

"""
Variable not having a slot. all variables are the same kind of
This is the distinction  between Id and RenamedId all over again.
@dataclass(frozen=True)
class Var():
    pass


"""

"""
f(e1[$1 -> $2],

\x. x ==== \x. eid0[$0 -> x]

eid0 = (name) -> { Var(name), Var(name) + 0, ... }

"""

"""
Shapes are normalized enodes in two sense
We rename to slots 0..n-1 in a lexicographic minimal fashion
And ids are canonicalize (but this also is an aspect of the regular enodes in regular egraph)
"""
type Shape = ENode

@dataclass
class EGraph():
    uf : SlottedUF = field(default_factory=SlottedUF)
    memo : dict[Shape, RenamedId] = field(default_factory=dict)
    # _should_ have classes, parents, etc for performance, but not strictly necessary

    def add_term(self, t : Term) -> RenamedId: ...
    def shape_of_enode(self, n : ENode) -> tuple[Renaming, Shape]:
        # normalize enode to shape
        # n = m*s
        match n:
            case AppNode(op, children):                        
                eids = [self.find(c) for c in n.children]
                renaming = {}
                for eid in eids:
                    for s in eid.slots():
                        if s not in renaming:
                            renaming[s] = Slot(len(renaming))
                R = Renaming.of_list(renaming.items())
                return R.rev(), n.apply_rename(R)
            case Var(name):
                R = Renaming.of_list([(name, Slot(0))])
                return R.rev(), Var(Slot(0))
            case _:
                raise NotImplementedError()
            #case Binder():
            #    # make autically redundnant

    def add_enode(self, n : ENode) -> RenamedId:
        renaming, shape = self.shape_of_enode(n)
        id = self.memo.get(shape)
        if id is not None:
            return renaming.partial_apply(self.find(id)) # TODO: implement partial_apply
        else:
            id = self.uf.makeset_slots(renaming.slots())
            self.memo[shape] = id
            return id
    def find(self, id : RenamedId) -> RenamedId:
        return self.uf.find(id)
    def union(self, a : RenamedId, b : RenamedId) -> None:
        # update memo here?
        return self.uf.union(a, b)
    def is_eq(self, a : RenamedId, b : RenamedId) -> bool:
        return self.uf.is_eq(a, b)
    def rebuild(self):
        done = False
        while not done:
            done = True
            new_memo : dict[Shape, RenamedId] = {}
            for shape, eid in self.memo.items():
                rep = self.find(eid)
                r2, shape2 = self.shape_of_enode(shape)
                if shape2 in new_memo:
                    existing = new_memo[shape2]
                    done = False
                    self.uf.union(r2 * rep, existing) # r2.rev() ?
                else:
                    new_memo[shape2] = r2 * rep # r2.rev()?
            self.memo = new_memo







