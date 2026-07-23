"""Day 3, Dev A: a turn-based combat coroutine.

Usage sketch once implemented:

    log = []
    fight = battle(character, log)
    state = next(fight)                # prime the generator
    state = fight.send("attack")       # player acts, generator advances
    state = fight.throw(AmbushError()) # simulate an interrupt mid-battle
    fight.close()                      # abandon the fight cleanly
"""
from __future__ import annotations

from typing import Dict, Generator, List

from .exceptions import GuildError
from .models import Character


class AmbushError(GuildError):
    """Raised into the battle generator to simulate a mid-fight ambush —
    exercises Generator.throw() specifically.
    """


def battle(
    character: Character,
    combat_log: List[str],
    enemy_name: str = "Goblin",
    enemy_hp: int = 30,
    enemy_attack: int = 5,
) -> Generator[Dict, str, None]:
    """Simulates a turn-based combat encounter using a coroutine.

    This generator yields the current combat state to the caller and pauses.
    The caller must resume execution by sending an action command via `.send()`.
    It also handles external interruptions (like ambushes) injected via `.throw()`.

    Args:
        character: The player's Character instance.
        combat_log: A list updated in-place with the battle's narrative events.
        enemy_name: The name of the opponent. Defaults to "Goblin".
        enemy_hp: The opponent's starting hit points. Defaults to 30.
        enemy_attack: The damage the opponent deals on a counter-attack. Defaults to 5.

    Yields:
        Dict: A dictionary representing the current state of the battle, or
            the final outcome ("victory" or "defeat").

    Receives (via generator.send()):
        str: The action the character should take ("attack", "heal", "flee").
    """
    try:
        combat_log.append(f"{enemy_name} appears!")

        while character.hp > 0 and enemy_hp > 0:
            state = {
                "character_hp": character.hp,
                "enemy_hp": enemy_hp,
                "enemy_name": enemy_name,
            }

            try:
                action = yield state

                match action:
                    case "attack":
                        attack_power = getattr(character, "attack", 10)
                        enemy_hp -= attack_power
                        combat_log.append(
                            f"{character.name} hits {enemy_name} for {attack_power} damage!"
                        )
                        if enemy_hp > 0:
                            character.hp -= enemy_attack
                            combat_log.append(
                                f"{enemy_name} hits {character.name} for {enemy_attack} damage!"
                            )
                    case "heal":
                        max_hp = character.base_hp * character.level
                        heal_amount = min(max_hp - character.hp, 10)
                        character.hp += heal_amount
                        combat_log.append(f"{character.name} heals for {heal_amount} HP!")
                    case "flee":
                        combat_log.append(f"{character.name} flees from battle!")
                        return
                    case _:
                        combat_log.append(f"Unknown action: {action}")
            except AmbushError:
                ambush_damage = 15
                character.hp -= ambush_damage
                combat_log.append("Ambush!")
                combat_log.append(
                    f"{character.name} was ambushed and takes {ambush_damage} damage!"
                )
                yield state | {
                    "ambushed": True,
                    "character_hp": character.hp,
                }

        if character.hp <= 0:
            combat_log.append(f"{character.name} is defeated!")
            yield {"outcome": "defeat"}
        else:
            combat_log.append(f"{character.name} is victorious!")
            yield {"outcome": "victory"}
    finally:
        combat_log.append("Combat generator closed.")