#!/usr/bin/env python3

import os
import pprint
import random
import itertools

import spells
import enemies
import fullcast
import encounters

pp = pprint.PrettyPrinter(indent=2)

keywords = {
        "Elemental": "Element of the Components. Star or Life-types use the Absolute element.",
        "Components": "The tiles used to cast the spell.",
        "AOE": "Targets all enemies or all incoming effects.",
        "Repeatable": "Can be casted up to X additional times per turn.",
        "Replace": "Draws another X tiles for use.",
        "Open Discard": "Discard into the open draw pool.",
        "Numeric": "The highest numeric value of the tile.",
        "Rune": "Effect stays while the rune is not dispelled. Can be dispelled voluntarily.",
        "Exhaust": "Can only be casted once per combat."
        }

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def generate_mana():
    elements = ["F", "W", "E"]
    numbers = range(1, 10)
    mana = list(itertools.product(elements, numbers))
    mana *= 4
    mana += [("S", 0)] * 4 # Earth
    mana += [("S", 3)] * 4 # Moon
    mana += [("S", 6)] * 4 # Sun
    mana += [("S", 9)] * 4 # Star
    mana += [("L", 1)] * 4 # Mind
    mana += [("L", 5)] * 4 # Life
    mana += [("L", 9)] * 4 # Soul
    random.shuffle(mana)
    return mana

class Character:
    name = "Elementalist"
    hp = 80
    hp_max = 80
    spells = [spells.Invoke(), spells.Strike(), spells.Break()]
    full_cast_spells = [fullcast.ClearIncoming(), fullcast.BasicFullCast(), fullcast.SequencePower(), fullcast.TriplePower()]

class Status:
    strength = 0
    shield = 0
    elem_break = {"F": 0, "W": 0, "E": 0, "A": 0}

class State:
    def __init__(self, character, enemies):
        self.mana = generate_mana()
        self.used_mana = []
        self.open_mana = []
        self.hand = []
        self.hp = character.hp
        self.hp_max = character.hp_max
        self.status = Status()
        self.outgoing_effects = []
        self.incoming_effects = []
        self.spells = character.spells
        self.full_cast_spells = character.full_cast_spells
        self.full_cast_damage = 0
        self.turn_number = 0
        self.spells_casted = 0
        self.enemies = [(e, Status()) for e in enemies]

def print_hand(hand):
    elements = " ".join(map(lambda e: e[0], hand))
    numbers = " ".join(map(lambda e: str(e[1]), hand))
    print(elements)
    print(numbers)

def wait():
    input("")

def run_turn(state):
    state.turn_number += 1
    state.spells_casted = 0
    for enemy in state.enemies:
        enemy[0].run_turn(state, enemy[1])
    state.open_mana = sorted_tiles(state.open_mana)
    for spell in state.spells:
        spell.tapped = False
        spell.repeatable_x = spell.repeatable_max
        spell.new_turn()
    while len(state.hand) < 15 and len(state.open_mana) > 0:
        clear()
        state.hand = sorted_tiles(state.hand)
        finish = draw_menu(state)
        if finish:
            break
    first_elemental = False
    while len(state.hand) < 15:
        tile = state.mana.pop()
        if not first_elemental and tile[0] in ["F", "W", "E"]:
            first_elemental = True
            state.hand.append((tile[0], int(input("Set number for tile %s %s: " % tile))))
        else:
            state.hand.append(tile)
    state.hand = sorted_tiles(state.hand)
    while True:
        clear()
        print_battle_status(state)
        end_turn = main_menu(state)
        if end_turn:
            break
    return resolve_effects(state)

def sorted_tiles(tiles):
    elemental_hand = sorted(filter(lambda t: t[0] in ("F", "W", "E"), tiles))
    star_hand = sorted(filter(lambda t: t[0] == "S", tiles))
    life_hand = sorted(filter(lambda t: t[0] == "L", tiles))
    return elemental_hand + star_hand + life_hand

def draw_menu(state):
    print("Open Discards:")
    print_hand(state.open_mana)
    print("")

    print("Hand (%s):" % len(state.hand))
    print_hand(state.hand)
    print("")
    print("Draw from Open Discard set?")
    print("")
    menu_options = {}
    index = 1
    for tile in state.open_mana:
        menu_options[str(index)] = tile
        print("%s: %s %s" % (index, tile[0], tile[1]))
        index += 1
    print("s: Skip")
    while True:
        choice = input(">> ")
        if choice in ["s", "n"]:
            return True
        if choice in menu_options:
            tile = menu_options[choice]
            state.open_mana.remove(tile)
            state.hand.append(tile)
            return False

def resolve_effects(state):
    state.outgoing_effects = []
    for incoming in state.incoming_effects:
        incoming[2] -= 1
        if incoming[2] == 0:
            state.hp -= incoming[1]
            print("You take %s %s damage!" % (incoming[1], incoming[0]))
            wait()
    state.incoming_effects = list(filter(lambda e: e[2] > 0, state.incoming_effects))
    if state.hp <= 0:
        print("You were defeated...")
        return True
    return False

def main_menu(state):
    menu_options = {}
    index = 1
    for spell in state.spells:
        if not spell.tapped and len(spell.find_castable(state.hand)) > 0:
            option = str(index) + ": " + spell.name()
            menu_options[str(index)] = spell
            print(option)
            index += 1
    fc = can_full_cast(state.hand)
    if fc:
        print("f: Full Cast")
    print("e: End Turn")
    while True:
        choice = input(">> ")
        if choice == "e":
            return True
        if fc and choice == "f":
            state.full_cast_damage = 0
            for fc_spell in state.full_cast_spells:
                fc_spell.cast(state.hand, state)
            state.outgoing_effects.append(["A", state.full_cast_damage, True])
            state.used_mana += state.hand
            state.hand = []
            return True
        if choice in menu_options:
            spell = menu_options[choice]
            return spell_menu(spell, state)

def can_full_cast(hand):
    if len(hand) % 3 != 0:
        return False
    sets = [hand[x:x+3] for x in range(0, len(hand), 3)]
    for s in sets:
        if not is_set(s):
            return False
    return True

def is_set(tiles):
    if tiles[0] == tiles[1] and tiles[0] == tiles[2]:
        return True
    if tiles[1][1] == tiles[0][1] + 1 and tiles[2][1] == tiles[0][1] + 2:
        if tiles[0][0] == tiles[1][0] and tiles[0][0] == tiles[2][0]:
            return True
    return False

def spell_menu(spell, state):
    menu_options = {}
    index = 1
    options = spell.find_castable(state.hand)
    for option in options:
        menu_options[str(index)] = option
        print(str(index) + ": " + str(option))
        index += 1
    print("c: Cancel")
    while True:
        choice = input(">> ")
        if choice == "c":
            break
        if choice in menu_options:
            for tile in menu_options[choice]:
                state.hand.remove(tile)
                state.used_mana.append(tile)
            spell.cast(menu_options[choice], state)
            if len(state.enemies) == 0:
                return True
            state.hand = sorted_tiles(state.hand)
            state.spells_casted += 1
            if spell.repeatable:
                spell.repeatable_x -= 1
                if spell.repeatable_x == 0:
                    spell.tapped = True
            else:
                spell.tapped = True
            break
    return False

def print_battle_status(state):
    for enemy in state.enemies:
        print(enemy[0].name)
        print("Enemy HP: " + str(enemy[0].hp))
        print("")
    print("HP: " + str(state.hp))
    print("")
    print("Incoming:")
    for incoming in state.incoming_effects:
        print("%s: %s (%s turns)" % tuple(incoming))
    print("")
    print("Outgoing:")
    for outgoing in state.outgoing_effects:
        print("%s: %s %s" % (outgoing[0], outgoing[1], "AOE" if outgoing[2] else ""))
    print("")

    print("Open Discards:")
    print_hand(state.open_mana)
    print("")

    print("Hand (%s):" % len(state.hand))
    print_hand(state.hand)
    print("")
    for spell in state.spells:
        if not spell.tapped and len(spell.find_castable(state.hand)) > 0:
            print("%s %s (Castable)" % (spell.name(), spell.tile_reqs()))
        else:
            print("%s %s" % (spell.name(), spell.tile_reqs()))
        print(spell.description())
        print("")

def generate_rewards(character):
    potential_rewards = spells.elementalist_rewards()
    rewards = []
    for i in range(0, 3):
        choice = random.choice(potential_rewards)
        rewards.append(choice)
        potential_rewards.remove(choice)
    return rewards

def rewards_menu(character):
    print("Choose your reward!")
    rewards = generate_rewards(character)
    menu_options = {}
    index = 1
    for reward in rewards:
        menu_options[str(index)] = reward
        print("%s: %s %s : %s" % (index, reward.name(), reward.tile_reqs(), reward.description()))
        index += 1
    print("s: Skip")
    while True:
        choice = input(">> ")
        if choice in ["s", "n"]:
            return
        if choice in menu_options:
            reward = menu_options[choice]
            character.spells.append(reward)
            return

def main():
    clear()
    character = Character()
    battles_cleared = 0
    while True:
        if battles_cleared > 9:
            print("You defeated the boss! Congratulations!")
            break
        elif battles_cleared == 9:
            encounter = [enemies.KingSlime()]
        elif battles_cleared < 4:
            encounter = encounters.generate_encounter()
        else:
            encounter = encounters.generate_hard_encounter()
        state = State(character, encounter)
        print("Battle " + str(battles_cleared + 1))
        input("")
        while len(state.hand) < 15:
            state.hand.append(state.mana.pop())
        while len(state.open_mana) < 9:
            state.open_mana.append(state.mana.pop())
        combat_finished = False
        while not combat_finished:
            combat_finished = run_turn(state)
        character.hp = state.hp
        if character.hp <= 0:
            break
        battles_cleared += 1
        rewards_menu(character)
        clear()

main()
