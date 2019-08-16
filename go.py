#!/usr/bin/env python3

import random
import itertools

def generate_mana():
    elements = ["F", "W", "E"]
    numbers = range(1, 10)
    mana = list(itertools.product(elements, numbers))
    mana *= 4
    mana += [("P", 0)] * 32
    random.shuffle(mana)
    return mana

class State:
    mana = generate_mana()
    used_mana = []
    hand = []
    hp = 50
    enemy_hp = 30
    outgoing_effects = []
    incoming_effects = []
    spells = []
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
    state.enemy_hp = 0

def main():
    state = State()
    while True:
        run_turn(state)
        if state.enemy_hp <= 0:
            print("You win!")
            break

main()
