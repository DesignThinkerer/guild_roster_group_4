"""Day 2 workshop targets, one per developer:

    Dev A -> OrderedSet      (custom unique-item structure)
    Dev B -> StatCalculator  (memoized callable, state held between calls)
    Dev C -> Roster          (full container protocol + iterator protocol
                              from scratch, i.e. __iter__ returning a real
                              iterator object with __next__, not a generator)

Constructors that just store their arguments are given; the actual
protocol methods are TODOs.
"""
from __future__ import annotations

from html.parser import charref
from typing import Any, Dict, Iterator, List

import select

from .models import Character


# --- Dev A: OrderedSet ------------------------------------------------------

class OrderedSet:
    """A set that remembers insertion order. Backed by a dict (Python 3.7+
    dicts are insertion-ordered) purely for its keys — this is what gives
    O(1) membership instead of the O(n) a list would need. Use only the
    keys of self._data; never store meaningful values in them.
    """

    def __init__(self, items: Iterator[Any] = ()):
        self._data: Dict[Any, None] = {}
        for item in items:
            self.add(item)

    def add(self, item: Any) -> None:
        if item not in self._data:
            self._data[item] = None
            
    def discard(self, item: Any) -> None:
        if item in self._data:
            del self._data[item]
        else:
            pass

    def __contains__(self, item: Any) -> bool:
        return item in self._data

    def __iter__(self) -> Iterator[Any]:
        for item in self._data:
            yield item

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"OrderedSet({list(self._data.keys())})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OrderedSet):
            # if the other object is not an OrderedSet,
            # let python try the other object's __eq__ method instead
            return NotImplemented
        return list(self._data.keys()) == list(other._data.keys())


# --- Dev B: memoized callable ------------------------------------------------

class StatCalculator:
    """A callable object that caches results by argument, for an
    expensive/derived stat computation.
    """

    def __init__(self):
        self._cache: Dict[tuple, int] = {}
        self.calls = 0
        self.cache_hits = 0

    def __call__(self, character: Character, difficulty: int) -> int:
        if not isinstance(character, Character):
            raise TypeError("StatCalculator only accepts Character instances")
        if not isinstance(difficulty, int):
            raise TypeError("StatCalculator only accepts int difficulty values")

        self.calls += 1
        key = (character.__class__.__name__, character.level, difficulty)

        if key in self._cache:
            self.cache_hits += 1
            return self._cache[key]

        result = (character.level * 7 + difficulty * 13) % 100
        self._cache[key] = result
        return result


# --- Dev C: full container protocol + iterator protocol from scratch -------

class RosterIterator:
    """A standalone iterator object for Roster, built from scratch rather
    than via a generator function — this is what Day 2's "__iter__ and
    __next__ from scratch" specifically asks for.
    """

    def __init__(self, characters: List[Character]):
        self._characters = characters
        self._index = 0

    def __iter__(self) -> RosterIterator:
        """ an iterator must be iterable (return itself)."""
        self._index = 0
        return self

    def __next__(self) -> Character:
        """ (Day 2): return the next character, advance the index,
        raise StopIteration once you've gone past the end.
        """
        try:
            c = self._characters[self._index]
            self._index += 1
            return c
        except IndexError:
            raise StopIteration


class Roster:
    """A guild's roster of characters, supporting the full container
    protocol: indexing, assignment, deletion, membership, length, and
    iteration.
    """

    def __init__(self, characters: Iterator[Character] = ()):
        self._characters: List[Character] = list(characters)

    def __getitem__(self, index: int) -> Character:
        return self._characters[index]

    def __setitem__(self, index: int, value: Character) -> None:
        """ Note: Rejects non-Character values with a TypeError. """
        if not isinstance(value, Character):
            raise TypeError()
        self._characters[index] = value

    def __delitem__(self, index: int) -> None:
        self._characters.pop(index)

    def __contains__(self, item: Character) -> bool:
        return item in self._characters

    def __len__(self) -> int:
        return len(self._characters)

    def __iter__(self) -> RosterIterator:
        """ Return a RosterIterator over this roster's
        characters — this is the connection between the container
        protocol and the from-scratch iterator class above.
        """
        return RosterIterator(self._characters)

    def __repr__(self) -> str:
        return f"Roster<Character>:{self._characters}"

    def add(self, character: Character) -> None:
        self._characters.append(character)

    def alive_characters(self) -> Iterator[Character]:
        """ A generator (use `yield`) that yields only the
        characters that are currently "truthy" (relies on Character's
        __bool__ from Day 1). Compare, once done, how much shorter this
        is than RosterIterator above — same protocol, very different
        amount of code.
        """
        for c in self._characters:
            if c:
                yield c

    def sorted_by_level(self) -> List[Character]:
        """ Return characters sorted by level. Should need
        no key= argument at all if Character.__lt__ (Day 1) is correct.
        """
        return sorted(self._characters)
