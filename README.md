# UwU Wat Dis?

This is an attempt at a language that lets users define type semantics and test out their programs.

Since it is supposed to be a PL playground, it is some janky typed lisp -- so there are parens and macros, but
also types.

The intent right now is to have an interpreter. Compiling this sort of thing seems really, really difficult (at
least where performance might be a bother) and it _is_ a playground, so people shouldn't really make things too
gigantic in this language.

There is no immediate intent to support IO, threading, or Python-interoperation.

# A broad overview of features

(Currently mostly hopes and dreams, see [the todos](#todo) for more.)

A lisp with types. Type annotations will look like `?(semantics):(type)`. Note that all types will live in some
semantics.
There will be some special forms to manipulate the types:

- `product-type!`
- `sum-type!`
- `record-type!`
- `forall-type!`

There will also be `defsemantics!` and `defsemantics-translator!` special forms to make the introduction and
translation to and from type semantics possible.

Naturally, otherwise, a few Clojure special forms will exist:

- `def!`
- `fn!`
- `if!`
- `defmacro!`
- `quote!`

The language will have a few builtin types in some system-F like semantics:

- `int` (really just python's `int`)
- `string` (python's `str`)
- a generic `list` type
- a generic `hashmap` type

# The Syntax Details

Here are some regexs (like python regexes) for the tokens:

- `delim := [\s\(\)]`
- `semantics := [^(\(\))]+` (parentheses might appear in the type to describe generics, but generic semantics so far make no sense).
- `token := [^(\s\(\)?:]+`

The BNF is as follows:

```
F := P | P P
P := S | S ? sematics : T
S := token | (P)
T := token | (token  TL)
TL := ?semantics : T | ?semantics : T TL
```

The intent is to play with semantics and perhaps syntax, so this is kept really, really minimal.

# TODO

- [x] make this a real python project with a `requirements.txt` and testing, linting, CI/CD.
- [ ] lex and parse properly
- [ ] interpret basic math (and type error as needed)
- [ ] support functions with type checking
- [ ] support type definitions
- [ ] support foralls
- [ ] support creating semantics
- [ ] support macros and quotes
