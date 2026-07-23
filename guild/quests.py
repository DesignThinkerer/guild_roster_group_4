"""Day 3, Dev B: a quest pipeline built almost entirely from itertools.

The three quest-source generators below are given (they're just static
data). Everything that actually combines/filters/groups them using
itertools is a TODO.
"""
from __future__ import annotations

import itertools
from typing import Dict, Iterable, Iterator, List

from .models import Character

Quest = Dict[str, object]


# --- Static quest sources, given -------------------------------------------

def daily_quests() -> Iterator[Quest]:
    yield {"name": "Clear the Rat Cellar", "reward_gold": 20, "min_level": 1}
    yield {"name": "Escort the Merchant", "reward_gold": 35, "min_level": 2}


def guild_quests() -> Iterator[Quest]:
    yield {"name": "Retrieve the Lost Banner", "reward_gold": 60, "min_level": 3}
    yield {"name": "Defend the Outpost", "reward_gold": 90, "min_level": 5}


def event_quests() -> Iterator[Quest]:
    yield {"name": "Harvest Festival Errand", "reward_gold": 15, "min_level": 1}


# --- TODO (Day 3): combine sources with itertools.chain ---------------------

def combined_quest_feed() -> Iterator[Quest]:
    """ Use itertools.chain to treat the three quest sources above as
    one continuous stream, without materializing any of them into a
    combined list first.
    """
    return itertools.chain(daily_quests(), guild_quests(), event_quests())


# --- TODO (Day 3): an infinite source + itertools.islice --------------------

def endless_bounty_quests() -> Iterator[Quest]:
    """ an intentionally infinite generator (use itertools.count) —
    bounty postings that never stop being generated, with a slowly
    increasing reward, e.g. reward_gold = 10 + i * 5 and
    min_level = 1 + i // 3 for i starting at 1.
    """
    for i in itertools.count(start=1):
        yield {
            "name": f"Bounty Contract #{i}",
            "reward_gold": 10 + i * 5,
            "min_level": 1 + i // 3
        }


def first_n_bounties(n: int) -> List[Quest]:
    """ use itertools.islice to pull exactly n items from
    endless_bounty_quests() without ever asking it to produce more than
    that.
    """
    return list(itertools.islice(endless_bounty_quests(), n))


# --- TODO (Day 3): itertools.takewhile ---------------------------------------

def quests_under_budget(quests: Iterable[Quest], budget: int) -> List[Quest]:
    """ Sort `quests` by reward_gold ascending, then use
    itertools.takewhile to collect quests while reward_gold < budget.

    Think carefully about why the sort has to happen first: takewhile
    stops at the *first* item that fails the predicate, unlike filter()
    which checks every item. Skipping the sort would silently produce a
    wrong (too-short) result rather than an error — worth testing that
    failure mode yourself once, deliberately, before moving on.
    """
    sorted_quests = sorted(quests, key=lambda q: q["reward_gold"])
    return list(itertools.takewhile(
                    lambda quest: quest["reward_gold"] < budget,
                    sorted_quests
                    ))


# --- TODO (Day 3): itertools.groupby -----------------------------------------

def group_roster_by_role(characters: Iterable[Character]) -> Dict[str, List[Character]]:
    """ sort `characters` by describe_role(), then use
    itertools.groupby (also keyed by describe_role()) to build a dict of
    role -> list of characters.

    itertools.groupby only groups *consecutive* runs of the same key —
    without the sort first, characters of the same role that aren't
    adjacent in the input would end up in separate groups.
    """
    fn = lambda character: character.describe_role()
    return {k:list(group_iterator) for k,group_iterator in itertools.groupby(sorted(characters, key=fn), key=fn)}


# --- TODO (Day 3): itertools.product -----------------------------------------

def eligible_assignments(
    characters: Iterable[Character], quests: Iterable[Quest]
) -> List[tuple]:
    """ use itertools.product to build every (character, quest) pair,
    then filter down to pairs where character.level >= quest["min_level"].
    """
    return list(filter(lambda cr_qt: cr_qt[0].level >=  cr_qt[1]["min_level"],
                       itertools.product(characters, quests)))