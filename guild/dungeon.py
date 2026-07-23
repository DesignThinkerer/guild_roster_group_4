"""Day 3, Dev C: two pieces, both TODOs.

1. An infinite dungeon generator built from yield-from delegation to a
   per-floor sub-generator.
2. A contextlib.contextmanager-style transaction. Look at
   exceptions.batch_validation (in exceptions.py) first — it's a complete,
   working example of exactly this pattern (a generator wrapped in
   @contextmanager) — before writing this one from scratch.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Dict, Generator, Iterator, List


# --- TODO (Day 3): yield-from delegation + lazy infinite sequence ----------

def floor_encounters(
      floor_number: int,
      dungeon_log: List[str]
    ) -> Generator[Dict, None, str]:
    dungeon_log.append(f"Entering floor {floor_number}")
    encounters = [
        {"type": "monster", "name": f"Monster {floor_number}"},
        {"type": "loot", "name": f"Loot Chest {floor_number}"},
    ]
    if floor_number % 3 == 0:
        encounters.append({"type": "trap", "name": f"Trap {floor_number}"})
    try:
        for encounter in encounters:
            action = yield encounter
            if action == "retreat":
                dungeon_log.append(f"Retreating from floor {floor_number}")
                return "retreated"
        dungeon_log.append(f"Cleared floor {floor_number}")
        return "cleared"
    finally:
        dungeon_log.append(f"Leaving floor {floor_number}")


def dungeon_floors(dungeon_log: List[str]) -> Iterator[Dict]:
    floor_number = 1
    
    # The try/finally wraps the ENTIRE loop
    try:
        while True:
            # yield from opens a direct tunnel to floor_encounters
            result = yield from floor_encounters(floor_number, dungeon_log)
            
            if result == "retreated":
                dungeon_log.append("Returns to town")
                return  # This ends the generator, triggering the finally block
                
            # If we didn't retreat, increment and go to the next floor
            floor_number += 1
            
    finally:
        dungeon_log.append("Dungeon generator closed.")


# --- TODO (Day 3): guild treasury transaction --------------------------------

@contextmanager
def guild_transaction(treasury: Dict[str, int]) -> Iterator[Dict[str, int]]:
    """
    Suppressing the exception would be the wrong choice here:
    the with block would simply finishes silently, and execution would continue 
    to the next line of the main program. 
    
    The caller would have absolutely no idea that their transaction failed
    and was rolled back. They would assume the purchase/trade succeeded,
    potentially leading to logical bugs later in the game 
    (e.g., handing over an item to a player even though they didn't 
    actually pay for it). 
    
    Re-raising forces the caller to acknowledge that the transaction blew up.
    """
    # Take a snapshot of the treasury
    snapshot = treasury.copy()
    try:
        yield treasury  # Allow the caller to mutate the treasury
    except BaseException:
        treasury.clear()
        treasury.update(snapshot)
        raise 