"""Day 1 shared build: a class with full comparison, equality, repr, and
set support — the "Money class" pattern (currency + amount) from the
program, adapted to the guild domain (an inventory item with a value and
a rarity tier).

Rarity and __init__ are given. Your job is the dunder methods below.
Remember the pairing rule: __eq__ and __hash__ must always be defined
together and stay consistent, or Item becomes unusable in sets/dicts.
"""
from __future__ import annotations

from functools import total_ordering
from enum import IntEnum


class Rarity(IntEnum):
    """IntEnum so rarities compare naturally (COMMON < RARE < LEGENDARY)
    without any extra work — this is used by Item.__lt__ below.
    """
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5


@total_ordering
class Item:
    """An inventory item, ordered first by rarity then by value.

    @total_ordering fills in the remaining comparison operators once you
    provide __eq__ and __lt__ — you don't need to implement __le__/__gt__/
    __ge__ yourself.
    """

    def __init__(self, name: str, rarity: Rarity, value: int):
        self.name = name
        self.rarity = rarity
        self.value = value

    def __repr__(self) -> str:
        return f"Item(name={self.name!r}, rarity={self.rarity.name}, value={self.value})"

    def __str__(self) -> str:
        return f"{self.name} ({self.rarity.name.capitalize()}, {self.value}g)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        return (self.name, self.rarity, self.value) == (other.name, other.rarity, other.value)

    def __hash__(self) -> int:
        """TODO (Day 1): must stay consistent with __eq__ above — equal
        Items must hash equal, or sets/dicts of Item will misbehave.
        """
        raise NotImplementedError("TODO (Day 1): implement __hash__")

    def __lt__(self, other: object) -> bool:
        """TODO (Day 1): order by rarity first, then value as a tiebreaker.
        Return NotImplemented if `other` isn't an Item.
        """
        raise NotImplementedError("TODO (Day 1): implement __lt__")

    def __bool__(self) -> bool:
        # Caveat: while this satisfy our current specs, this treats negative values as truthy too. 
        # If our domain wants “truthy only when value is positive,” then we would want self.value > 0 instead. 
        return self.value != 0
