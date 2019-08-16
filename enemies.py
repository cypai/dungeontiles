#!/usr/bin/env python3

import itertools
import random

class Enemy:
    name = ""
    hp = 0
    hp_max = 0
    status = {}

    def run_turn(self, state):
        pass

class FlameTurtle(Enemy):
    name = "Flame Turtle"
    hp = 30
    hp_max = 30

    status = {"Shield": 0}

    def run_turn(self, state):
        if state.turn_number % 2 == 0:
            print("Flame Turtle defended itself.")
            self.status["Shield"] += 5
            ai_open_discard("L", state)
        else:
            ai_attack(self.name, "F", 9, 2, state)
            ai_open_discard("F", state)

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
    tile = random.choice(pool)
    state.open_mana.append(tile)
    print("%s %s was Open Discarded." % tile)
    input("")
