"""The core Character model.

Three separate TODOs live in this file, for three different days — read
the notes at each one carefully, they're not all unlocked at the same time:

  - Day 1: Character's dunder methods (__repr__, __eq__, __hash__, __lt__,
    __bool__) — same idea as Item in items.py, applied to a class other
    exercises will already be using.
  - Day 4: HealerMixin / TankMixin / LoggableMixin — the mixin & MRO
    workshop.
  - Day 5: GuildMeta — the registry metaclass. Character does NOT use it
    yet (see the class statement below) — wiring it in is literally your
    last Day 5 step, once GuildMeta itself works.

fields.py (StringField/IntField) is already working, so Character's
fields below will validate correctly from Day 1 onward regardless of
which of the above TODOs you've reached.
"""
from __future__ import annotations

from typing import Dict, Type

from .fields import IntField, StringField


class GuildMeta(type):
    """Metaclass that automatically registers concrete Character subclasses.

    Similar to an ORM's model registry, this collects playable character
    classes at definition time rather than instantiation time. It populates
    the `GuildMeta.registry` dictionary with the class name as the key and 
    the class object as the value.

    Behaviors:
      - Skips registration for the base class itself.
      - Validates that every concrete subclass defines an integer `base_hp`
        attribute, raising a TypeError if it is missing or invalid.
    """

    registry: Dict[str, Type["Character"]] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        # create the class first
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        
        # skip registration for the base Character class
        if not bases:
           return cls
        # validate and register concrete subclasses
        if not isinstance(getattr(cls, 'base_hp', None), int):
            raise TypeError(f"{name} must have an int base_hp attribute")
        
        mcs.registry[name] = cls
        
        return cls


class Character(metaclass=GuildMeta):
    """Base class for every playable character."""

    name = StringField(max_length=50)
    hp = IntField(minimum=0)
    level = IntField(minimum=1, maximum=100)

    base_hp: int = 10  # overridden by every concrete subclass

    def __init__(self, name: str, level: int = 1):
        self.name = name
        self.level = level
        self.hp = self.base_hp * level

    def describe_role(self) -> str:
        return "Adventurer"

    # --- Day 1 dunder set -------------------------------------------------

    def __repr__(self) -> str:
        """ should look like
        Warrior(name='Grom', level=2, hp=30)
        """
        return f"{self.describe_role()}(name='{self.name}', level={self.level}, hp={self.hp})"

    def __str__(self) -> str:
        """should look like
        Grom the Warrior (Lv.2, 30 HP)
        """
        return f"{self.name} the {self.describe_role()} (Lv.{self.level}, {self.hp} HP)"

    def __eq__(self, other: Character) -> bool:
        """two Characters are equal when they're the same
        concrete type, AND have the same name AND the same level.
        """
        return type(self) == type(other) and self.name == other.name and self.level == other.level

    def __hash__(self) -> int:
        """must stay consistent with __eq__ above."""
        return hash((type(self), self.name, self.level))

    def __lt__(self, other: Character) -> bool:
        """TODO (Day 1): order by level — this is what lets a Roster
        (Day 2) be sorted() directly with no key= needed.
        """
        return self.level < other.level

    def __bool__(self) -> bool:
        """TODO (Day 1): a character is "truthy" while alive (hp > 0)."""
        return self.hp > 0


class Warrior(Character):
    base_hp = 15

    def describe_role(self) -> str:
        return "Warrior"


class Mage(Character):
    base_hp = 8

    def describe_role(self) -> str:
        return "Mage"


class Rogue(Character):
    base_hp = 10

    def describe_role(self) -> str:
        return "Rogue"


# --- Day 4 mixins: horizontal reuse without deep inheritance ---------------

class HealerMixin:
    """TODO (Day 4, Dev A/whoever owns this): adds healing behavior.

    describe_role() must call super().describe_role() and append
    " + Healer" to whatever it returns — this is deliberate: it's one
    half of the cooperative MRO chain exercised by Paladin below. Do not
    hard-code a return value; the whole point breaks if you do.

    heal(target, amount=None): heals `target` by `amount` (or by
    self.heal_power if amount is None), capped at target's max HP
    (target.base_hp * target.level). Returns the target's new hp.
    """

    heal_power: int = 5

    def describe_role(self) -> str:
        raise NotImplementedError("TODO (Day 4): implement HealerMixin.describe_role")

    def heal(self, target: "Character", amount: int = None) -> int:
        raise NotImplementedError("TODO (Day 4): implement HealerMixin.heal")


class TankMixin:
    """TODO (Day 4): adds taunt/aggro behavior.

    describe_role() must call super().describe_role() and append
    " + Tank" — same cooperative-chain requirement as HealerMixin above.

    taunt(enemies): for this exercise, a simplified placeholder is fine —
    e.g. just return list(enemies). The mechanism (MRO), not combat
    balance, is the point.
    """

    taunt_radius: int = 3

    def describe_role(self) -> str:
        raise NotImplementedError("TODO (Day 4): implement TankMixin.describe_role")

    def taunt(self, enemies) -> list:
        raise NotImplementedError("TODO (Day 4): implement TankMixin.taunt")


class Paladin(HealerMixin, TankMixin, Warrior):
    """The deliberate mixin conflict. Once HealerMixin and TankMixin are
    implemented above, run Paladin.__mro__ and Paladin("x").describe_role()
    and be ready to explain, step by step, why the result is what it is —
    and what would change if TankMixin were listed before HealerMixin in
    the class statement above.
    """

    base_hp = 20


# --- Day 4 (independent mixin, not part of the conflict above) ------------

class LoggableMixin:
    """TODO (Day 4, other dev): logs every attribute assignment on the
    instance into self._log (a list of strings).

    Two things to get right:
      1. __init__ needs to set up self._log = [] BEFORE calling
         super().__init__(...), and must do so via self.__dict__ directly
         (not `self._log = []`) to avoid triggering your own __setattr__
         override recursively before _log exists.
      2. __setattr__ should append an entry (e.g. f"{name} = {value!r}")
         for every assignment except to _log itself, then still actually
         perform the assignment via super().__setattr__(...).

    `log` should be a read-only property returning a copy of the list
    (not the live list itself).
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("TODO (Day 4): implement LoggableMixin.__init__")

    def __setattr__(self, name: str, value) -> None:
        raise NotImplementedError("TODO (Day 4): implement LoggableMixin.__setattr__")

    @property
    def log(self) -> list:
        raise NotImplementedError("TODO (Day 4): implement LoggableMixin.log")


class LoggedMage(LoggableMixin, Mage):
    """Demo combination used by the test suite / workshop walkthrough."""
