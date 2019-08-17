#!/usr/bin/env python3

import os
import pprint
import random
import itertools

import spells
import enemies

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

class State:
    mana = generate_mana()
    used_mana = []
    open_mana = []
    hand = []
    hp = 50
    enemy = enemies.FlameTurtle()
    outgoing_effects = []
    incoming_effects = []
    spells = [spells.Invoke(), spells.DualInvoke(), spells.Strike(), spells.Blast(), spells.Explosion()]
    full_cast_spells = []
    turn_number = 0

def print_hand(hand):
    elements = " ".join(map(lambda e: e[0], hand))
    numbers = " ".join(map(lambda e: str(e[1]), hand))
    print(elements)
    print(numbers)

def wait():
    input("")

def run_turn(state):
    state.turn_number += 1
    state.enemy.run_turn(state)
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
    while len(state.hand) < 15:
        state.hand.append(state.mana.pop())
    state.hand = sorted_tiles(state.hand)
    while True:
        clear()
        print_battle_status(state)
        end_turn = main_menu(state)
        if end_turn:
            break
    resolve_effects(state)

def sorted_tiles(tiles):
    elemental_hand = sorted(filter(lambda t: t[0] in ("F", "W", "E"), tiles))
    star_hand = sorted(filter(lambda t: t[0] == "S", tiles))
    life_hand = sorted(filter(lambda t: t[0] == "L", tiles))
    return elemental_hand + star_hand + life_hand

def draw_menu(state):
    print("Open Discards:")
    print_hand(state.open_mana)
    print("")

    print("Hand:")
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
    for outgoing in state.outgoing_effects:
        damage = outgoing[1]
        shield = state.enemy.status["Shield"]
        if shield > 0:
            if shield >= damage:
                print("%s blocked %s damage!" % (state.enemy.name, damage))
                state.enemy.status["Shield"] -= damage
                damage = 0
            else:
                print("%s blocked %s damage!" % (state.enemy.name, shield))
                state.enemy.status["Shield"] = 0
                damage -= shield
        if damage > 0:
            state.enemy.hp -= damage
            print("%s takes %s %s damage!" % (state.enemy.name, damage, outgoing[0]))
            wait()
    state.outgoing_effects = []
    if state.enemy.hp <= 0:
        print("%s was defeated!" % state.enemy.name)
        exit(0)
    for incoming in state.incoming_effects:
        incoming[2] -= 1
        if incoming[2] == 0:
            state.hp -= incoming[1]
            print("You take %s %s damage!" % (incoming[1], incoming[0]))
            wait()
    state.incoming_effects = list(filter(lambda e: e[2] > 0, state.incoming_effects))
    if state.hp <= 0:
        print("You were defeated...")
        exit(0)

def main_menu(state):
    menu_options = {}
    index = 1
    for spell in state.spells:
        if not spell.tapped and len(spell.find_castable(state.hand)) > 0:
            option = str(index) + ": " + spell.name()
            menu_options[str(index)] = spell
            print(option)
            index += 1
    print("e: End Turn")
    while True:
        choice = input(">> ")
        if choice == "e":
            return True
        if choice in menu_options:
            spell = menu_options[choice]
            spell_menu(spell, state)
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
            if spell.repeatable:
                spell.repeatable_x -= 1
                if spell.repeatable_x == 0:
                    spell.tapped = True
            else:
                spell.tapped = True
            break

def print_battle_status(state):
    print(state.enemy.name)
    print("Enemy HP: " + str(state.enemy.hp))
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

    print("Hand:")
    print_hand(state.hand)
    print("")
    for spell in state.spells:
        if not spell.tapped and len(spell.find_castable(state.hand)) > 0:
            print("%s %s (Castable)" % (spell.name(), spell.tile_reqs()))
        else:
            print("%s %s" % (spell.name(), spell.tile_reqs()))
        print(spell.description())
        print("")

def main():
    clear()
    state = State()
    print("A %s approaches!" % state.enemy.name)
    while len(state.hand) < 15:
        state.hand.append(state.mana.pop())
    while len(state.open_mana) < 9:
        state.open_mana.append(state.mana.pop())
    state.enemy.status = {"Shield": 0}
    while True:
        run_turn(state)

main()
