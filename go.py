#!/usr/bin/env python3

import os
import pprint
import random
import itertools

pp = pprint.PrettyPrinter(indent=2)

keywords = {
        "Elemental": "Element of the Components. Star or Life-types use the Absolute element.",
        "Components": "The tiles used to cast the spell.",
        "AOE": "Targets all enemies or all incoming effects.",
        "Tap": "Can only be casted X times per turn.",
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

class Spell:
    def name(self):
        return ""

    def description(self):
        return ""

    def tile_reqs(self):
        """
        (tile amount, I/S (identical/sequential))
        """
        return []

    def find_castable(self, hand):
        return []

    def cast(self, tiles, state):
        pass

    def new_turn(self):
        pass

class Invoke(Spell):
    tapped = False

    def name(self):
        return "Invoke"

    def description(self):
        return "Casts 3 (Elemental). (Tap)."

    def tile_reqs(self):
        return [(1, "I")]

    def find_castable(self, hand):
        if self.tapped:
            return []
        else:
            return list(map(lambda t: [t], hand))

    def cast(self, tiles, state):
        element = tiles[0][0]
        state.outgoing_effects.append([element, 3, False])
        self.tapped = True

    def new_turn(self):
        self.tapped = False

class DualInvoke(Spell):
    tapped = False

    def name(self):
        return "Dual Invoke"

    def description(self):
        return "Casts 6 (Elemental). (Tap)."

    def tile_reqs(self):
        return [(2, "I")]

    def find_castable(self, hand):
        return find_identical(2, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        state.outgoing_effects.append([element, 6, False])

    def new_turn(self):
        self.tapped = False

class ElementalBlast(Spell):
    def name(self):
        return "Elemental Blast"

    def description(self):
        return "Casts 10 (Elemental) (AOE)."

    def tile_reqs(self):
        return [(3, "I")]

    def find_castable(self, hand):
        return find_identical(3, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        state.outgoing_effects.append([element, 10, True])

class ElementalStrike(Spell):
    def name(self):
        return "Elemental Strike"

    def description(self):
        return "Casts 10 (Elemental)."

    def tile_reqs(self):
        return [(3, "S")]

    def find_castable(self, hand):
        return find_sequences(3, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        state.outgoing_effects.append([element, 10, False])

def find_identical(amount, hand):
    count = {}
    for tile in hand:
        if tile in count:
            count[tile] += 1
        else:
            count[tile] = 1
    return list(map(lambda j: [j[0]] * amount, filter(lambda i: i[1] >= amount, count.items())))

def find_sequences(amount, hand):
    unique_hand = sorted(list(set(hand)))
    sequences = {}
    for i in range(len(unique_hand)):
        tile = unique_hand[i]
        sequences[tile] = [tile]
        current_amount = 1
        j = i + 1
        k = 1
        while current_amount < amount and j < len(unique_hand):
            current_tile = unique_hand[j]
            if current_tile == (tile[0], tile[1] + k):
                sequences[tile].append(current_tile)
            else:
                break
            j += 1
            k += 1
    return list(map(lambda j: j[1], filter(lambda i: len(i[1]) == amount, sequences.items())))

class State:
    mana = generate_mana()
    used_mana = []
    hand = []
    hp = 50
    enemy_name = "Flame Turtle"
    enemy_hp = 30
    outgoing_effects = []
    incoming_effects = []
    spells = [Invoke(), DualInvoke(), ElementalStrike(), ElementalBlast()]
    full_cast_spells = []

def print_hand(hand):
    elements = " ".join(map(lambda e: e[0], hand))
    numbers = " ".join(map(lambda e: str(e[1]), hand))
    print(elements)
    print(numbers)

def wait():
    input("")

def run_turn(state):
    for spell in state.spells:
        spell.new_turn()
    while len(state.hand) < 15:
        state.hand.append(state.mana.pop())
    if len(state.incoming_effects) == 0:
        print("%s casts for %s %s damage in %s turn(s)!" % (state.enemy_name, 9, "F", 2))
        print("")
        state.incoming_effects.append(["F", 9, 2])
        wait()
    while True:
        clear()
        print_battle_status(state)
        end_turn = main_menu(state)
        if end_turn:
            break
    resolve_effects(state)

def resolve_effects(state):
    for outgoing in state.outgoing_effects:
        state.enemy_hp -= outgoing[1]
        print("%s takes %s %s damage!" % (state.enemy_name, outgoing[1], outgoing[0]))
        wait()
    state.outgoing_effects = []
    if state.enemy_hp <= 0:
        print("%s was defeated!" % state.enemy_name)
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
        if len(spell.find_castable(state.hand)) > 0:
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
            break

def print_battle_status(state):
    print(state.enemy_name)
    print("Enemy HP: " + str(state.enemy_hp))
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

    print("Hand:")
    elemental_hand = sorted(filter(lambda t: t[0] in ("F", "W", "E"), state.hand))
    star_hand = sorted(filter(lambda t: t[0] == "S", state.hand))
    life_hand = sorted(filter(lambda t: t[0] == "L", state.hand))
    state.hand = elemental_hand + star_hand + life_hand
    print_hand(state.hand)
    print("")
    for spell in state.spells:
        if len(spell.find_castable(state.hand)) > 0:
            print(spell.name() + " (Castable)")
        else:
            print(spell.name())
        print(spell.description())
        print("")

def main():
    clear()
    state = State()
    print("A %s approaches!" % state.enemy_name)
    while True:
        run_turn(state)

main()
