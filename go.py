#!/usr/bin/env python3

import pprint
import random
import itertools

pp = pprint.PrettyPrinter(indent=2)

def generate_mana():
    elements = ["F", "W", "E"]
    numbers = range(1, 10)
    mana = list(itertools.product(elements, numbers))
    mana *= 4
    mana += [("P", 0)] * 32
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
        return "Casts 3u (Elemental). (Tap)."

    def tile_reqs(self):
        return [(1, "I")]

    def find_castable(self, hand):
        if self.tapped:
            return []
        else:
            return list(map(lambda t: [t], hand))

    def cast(self, tiles, state):
        element = tiles[0][0]
        state.outgoing_effects.append((element, 3, False))
        self.tapped = True

    def new_turn(self):
        self.tapped = False

class DualInvoke(Spell):
    def name(self):
        return "Dual Invoke"

    def description(self):
        return "Casts 6u (Elemental). (Tap)."

    def tile_reqs(self):
        return [(2, "I")]

    def find_castable(self, hand):
        return find_identical(2, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        state.outgoing_effects.append((element, 6, False))

class ElementalBlast(Spell):
    def name(self):
        return "Elemental Blast"

    def description(self):
        return "Casts 10u (Elemental) (AOE)."

    def tile_reqs(self):
        return [(3, "I")]

    def find_castable(self, hand):
        return find_identical(3, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        state.outgoing_effects.append((element, 10, True))

class ElementalStrike(Spell):
    def name(self):
        return "Elemental Strike"

    def description(self):
        return "Casts 10u (Elemental)."

    def tile_reqs(self):
        return [(3, "S")]

    def find_castable(self, hand):
        return find_sequences(3, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        state.outgoing_effects.append((element, 10, False))

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

def cast_spell(spell, tiles, state):
    for tile in tiles:
        state.hand.remove(tile)
        state.used_mana.append(tile)
    spell.cast(tiles, state)

def run_turn(state):
    for spell in state.spells:
        spell.new_turn()
    if len(state.incoming_effects) == 0:
        print("%s casts for %su %s damage in %s turn(s)!" % (state.enemy_name, 9, "F", 2))
        print("")
        state.incoming_effects.append(("F", 9, 2))
    print("Enemy HP: " + str(state.enemy_hp))
    print("HP: " + str(state.hp))
    print("")
    print("Incoming:")
    for incoming in state.incoming_effects:
        print("%s: %s (%s turns)" % incoming)
    print("")
    print("Outgoing:")
    for outgoing in state.outgoing_effects:
        print("%s: %s %s" % (outgoing[0], outgoing[1], "AOE" if outgoing[2] else ""))
    print("")

    while len(state.hand) < 15:
        state.hand.append(state.mana.pop())
    state.hand = sorted(state.hand)
    print_hand(state.hand)
    print("")
    for spell in state.spells:
        if len(spell.find_castable(state.hand)) > 0:
            print(spell.name() + " (Castable)")
        else:
            print(spell.name())
        print(spell.description())
        print("")
    state.enemy_hp = 0

def main():
    state = State()
    while True:
        run_turn(state)
        if state.enemy_hp <= 0:
            print("You win!")
            break

main()
