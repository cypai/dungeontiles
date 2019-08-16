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

    def invoke(self, tiles):
        return None

class Invoke(Spell):
    def name(self):
        return "Invoke"

    def description(self):
        return "Casts 3u (Elemental). (Tap)."

    def tile_reqs(self):
        return [(1, "I")]

    def find_castable(self, hand):
        return list(map(lambda t: [t], hand))

    def invoke(self, tiles):
        return 3, tiles[0][0], False

class DualInvoke(Spell):
    def name(self):
        return "DualInvoke"

    def description(self):
        return "Casts 6u (Elemental). (Tap)."

    def tile_reqs(self):
        return [(2, "I")]

    def find_castable(self, hand):
        return find_identical(2, hand)

    def invoke(self, tiles):
        return 6, tiles[0][0], False

class ElementalBlast(Spell):
    def name(self):
        return "Elemental Blast"

    def description(self):
        return "Casts 10u (Elemental) (AOE)."

    def tile_reqs(self):
        return [(3, "I")]

    def find_castable(self, hand):
        return find_identical(3, hand)

    def invoke(self, tiles):
        return 10, tiles[0][0], True

class ElementalStrike(Spell):
    def name(self):
        return "Elemental Strike"

    def description(self):
        return "Casts 10u (Elemental)."

    def tile_reqs(self):
        return [(3, "S")]

    def find_castable(self, hand):
        return find_sequences(3, hand)

    def invoke(self, tiles):
        return 10, tiles[0][0], False

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

def run_turn(state):
    print("Enemy HP: " + str(state.enemy_hp))
    print("HP: " + str(state.hp))
    print("")
    while len(state.hand) < 15:
        state.hand.append(state.mana.pop())
    state.hand = sorted(state.hand)
    print_hand(state.hand)
    for spell in state.spells:
        print(spell.name())
        print(spell.description())
        print(spell.find_castable(state.hand))
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
