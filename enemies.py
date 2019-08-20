#!/usr/bin/env python3

import itertools
import random

class Enemy:
    def __init__(self):
        name = ""
        hp = 0
        hp_max = 0

    def run_turn(self, state, self_status):
        pass

class FlameTurtle(Enemy):
    name = "Flame Turtle"
    hp = 30
    hp_max = 30

    def run_turn(self, state, self_status):
        if state.turn_number % 2 == 0:
            self_status.shield += 5
            print("Flame Turtle defended itself. +5 Shield.")
            print("Flame Turtle has %s Shield." % self_status.shield)
            ai_open_discard("L", state)
        else:
            ai_attack(self.name, "F", 9, 2, state)
            ai_open_discard("F", state)

class Slime(Enemy):
    name = "Slime"
    hp = random.randrange(9, 13)
    hp_max = hp
    begin = random.randrange(0, 3)

    def run_turn(self, state, self_status):
        self.begin += 1
        if self.begin + state.turn_number % 3 == 0:
            ai_attack(self.name, "W", 2, 2, state)
            ai_open_discard("W", state)
        else:
            ai_attack(self.name, "L", 3, 1, state)
            ai_open_discard("A", state)

def ai_attack(name, element, damage, countdown, state):
    print("%s casts for %s %s damage in %s turn(s)!" % (name, damage, element, countdown))
    print("")
    state.incoming_effects.append(["F", 9, 2])

def ai_open_discard(element, state):
    if element in ["F", "W", "E"]:
        pool = list(itertools.product([element], range(1, 10)))
    if element == "S":
        pool = list(itertools.product(["S"], range(0, 10, 3)))
    if element == "L":
        pool = list(itertools.product(["L"], range(1, 10, 4)))
    if element == "A":
        pool = list(itertools.product(["S"], range(0, 10, 3)))
        pool += list(itertools.product(["L"], range(1, 10, 4)))
    tile = random.choice(pool)
    state.open_mana.append(tile)
    print("%s %s was Open Discarded." % tile)
    input("")
