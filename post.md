---
title: Slotted Egraphs for the People (Demystified)
---


Egraphs are a useful technology for program optimization that instead of destrcutively optimizing terms/ programs, they keep all version around ocmpactly from which the best version can be extracted later. This avoids the so called 'phase ordering problem"

There are some perpetual booegeyman in the ergaph world

- Associativity and Commutativity show up everywhere but also make the egraph explode
- Binders and Lambda terms show up in many applications but are difficult or expensive to model using explicit first order equational reasoning

Slotted Egraphs are like aknight in shining armor at least for parts the latter, the alpha equivalence problem. It shows up in math classes when you do integrals or sums that these two expressions are the same thing via "dummy renaming" $\sum_i i = \sum_j j$. In computer science or logic, logical quantification and lambda terms have this same sort of property $\lambda x, x = \lambda y, y$ etc. It is very very common to mess up a homework assignment or a computer implementation by dealing with dummy indices incorrectly, causing a clash of naming where there shouldn't have been (accidental capture). There are a plethora of standard painful bookkeeping techniques, de bruijn indices or locally nameless style in particular, that do guarantee you do things correctly.

$\sum_i \sum_j a_{ij} = \sum_j \sum_i a{ij}$ This is commutativity and associativy but raised to big summation. It is very useful useful, itr describe interhacging loops. And it looks like a small move when I write it, but in de Bruijn, there is a massive shifting and de ashifting that needst o happeing in the body. The move is very nonlocal in the de bruijn representaiton, but local in the named representation. Locality is necesary in the egraph because of the massived sharing. Global/big moves require many administrative rewrites, or extracting to a term.

If you don't need shifting ever, maybe de bruijn is fine.

Phil: In the egraph, the de bruijn don't seem to work.
Rudi: Not so! It's a tradeoff.

`var(22) + 17 != var(17) + 17` and they can't ever be the saem thing. This is unneccessary duplication. Shifting de Bruijn `shift(0) = 0`  `0*x = 0`  
`shift(0*var(22)) = shift(0) = 0 = 0 * shift(var(22)) = 0 * var(23)` but this matches shift again and the equality saturation doesn't terminate. It also

Arbitrarily large terms can be described bty an egraph very easily `0 = 0*x = 0*0*x = 0*0*0*x = ...` Is actually a small egraph. But if `x` is a de bruijn thing, it can refer up through an arbitrarily large number of binders. These are equal, but there are an infinite number of different leaves. No it's not leaves. It's an infinite number of eclasses. We generate subterms that aren't covered or compressed by previously discovered the ground equations.

Phil: This is kind of confusing what really is the thing that goes wrong?

Associativity can also do this. (come up with example?) `a*(a*0) -> (a*a)*0` you can always generate all squares.
But then why does AC fix this? It adds enough equalities to

Phil: I consider myself somewhat well versed in egraph shit, but have found slotted egraphs pretty mystifying despite a string desire to solve the alpha equivalence problem

Phil: Actually I don't feel like this is that relevant anymore

# Explicit Names

If you used a regualr egraph, you could encode an alpha renaming system into rules.

There is a first order named system with explicit rename of variables

It would look roughly like this

A destructive renaming would look like this

```
rename(a,b,f(X,Y)) -> f(rename(a,b,X), rewrite(a,b,(Y)))
rename(a,b,a) -> b
rename(a,b,c) -> c
rename(a,b,lam(c,X)) -> lam(c, rename(a,b,X))
rename(a,b,lam(a,X)) -> lam(a, X)
rename(a,b,lam(a,X)) -> d = fresh(), lam(d, rename(a,d,X))
rename(a,b,lam(b,X)) -> d = fresh(), lam(d, rename(a,b,rename(b,d,X))) # hard case
rename(a,b,b) -> ? # substitution vs permutation perspective
```

You'd also occassionally need to generate fresh names and rename

There is also a style using swaps instead of destructive renaming

```
swap(a,b,f(X,Y)) -> f(swap(a,b,X), swap(a,b,Y))
swap(a,b,lam(a,X)) -> lam(b,swap(a,b,X)) # lam is just a normal constructor
swap(a,b,lam(b,X)) -> lam(a,swap(a,b,X)) # no special case
```

 <https://easychair.org/publications/paper/8LkF/download> look at table at the bottom of 158. The definition of applying $\pi$

It's kind of wild that swapping is so much simpler

Phil: So yeah, if you have a group it isn't a total disaster to just encode it rather than adding a special group union find. Is that the case in slotted?

A very simple group action is Z2

```
- group action style 
neg(neg(X)) -> X
id(X) -> X


mul(one, X) -> X
mul(negone, mul(negone, X)) -> X 
mul(mul(X,Y),Z) -> mul(X, mul(Y,Z))


smul(one, X) -> X
smul(negone, smul(negone, X)) -> X 
mulR(negone, negone) -> one
mulR(one, X) -> X
smul(one, X) -> X
smul(mulR(X,Y),Z) -> smul(X, smul(Y,Z))


```

{id, neg}    mul = compose
{1,-1}   multiplication is mutlipcation

AC is decidable its fine, but brute forcing it with rules explodes

```
mul(X,mul(Y,Z)) = mul(mul(X,Y), Z)
mul()
```

# De Bruijn

De Bruijn despite it's holy cow status, is a pretty complex topic and weird.

# Bits and Bobbles

<https://arxiv.org/pdf/2105.02856>

```
Taking CSE as an example, consider the following program
fragment

`(a + (v+7)) * (v+7)`

A standard CSE transformation can rewrite this to

`let w = v+7 in (a + w) * w`

which can be computed more efficiently. However, CSE is
not entirely straightforward. Consider

`(a + (let x = exp(z) in x+7)) * (let y = exp(z) in y+7)`

We might hope that CSE would spot that the two let-bound
terms are 𝛼-equivalent, and transform to

`let w = (let x = exp(z) in x+7) in (a + w) * w`

We would like to similarly spot the equivalence of the two
lambda terms in

`foo (\x.x+7) (\y.y+7)`

and transform to

`let h = \x.x+7 in foo h `
```

```
False negatives: sensitivity to arbitrary variable names.
Consider this expression:
`map (\y.y+1) (map (\x.x+1) vs)`

The two lambda-expressions are not syntactically identical, but they are 𝛼-equivalent, and perform the same
computation in the same way. Similarly, consider

`foo (let bar = x+1 in bar*y) (let pub = x+1 in pub*y)`

Here we would like to CSE the two arguments to foo,
even though they use different binders internally.

• False positives: name overloading. Consider the syntactically repeated subexpression x+2 in this example:

`foo (let x=bar in x+2) (let x=pub in x+2)`

The two subexpressions x+2 are unrelated, but they are
syntactically identical. If the goal is structure sharing
this is fine; indeed we might want to share the two
x+2 subexpressions, to save memory. However, sharing
the two would be wrong for tasks similar to CSE. For
example, it would be clearly wrong to transform the
above expression into

`let tmp = x+2 in foo (let x=bar in tmp) (let x=pub in tmp)`
```

var(17) + 1 != var(42) + 1  but they are kind of the same thing

`(\x. t x) t`  t might look the same in named, but if it contains x, they aren't really. In de bruijn, even if t are syntacticaly same (`var(17) + 1` for example), one is in a shifted context, sho they are referring to very different binding sites.

There's something "broken" about trying to take the idea of hash consing, which works in a context free situation and trying to to it in wildly varying contexts.

`Gamma |- t` and `Gamma' |- t` are almost radically incomparable things. If you make `Gamma` implicit, you can delude yourself into thinking they are sensisbly comparable. On the other hand, compression, algorthimic effficiency, memory usage reduction are always valid goals.

<https://www.philipzucker.com/slotted_hash_cons/>

slotted union find

slotted hash cons for slotted ground knuth bendix / nominal ground knuth bendix

weak rewrite for loops
ordered rewriting
