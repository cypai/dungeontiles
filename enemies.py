#!/usr/bin/env python3

import itertools
import random

class Enemy:
    def __init__(self):
        self.name = ""
        self.hp = 0
        self.hp_max = 0

    def run_turn(self, state, self_status):
        pass

class FlameTurtle(Enemy):
    def __init__(self):
        self.name = "Flame Turtle"
        self.hp = 30
        self.hp_max = 30

    def run_turn(self, state, self_status):
        if state.turn_number % 2 == 0:
            self_status.shield += 5
            print("Flame Turtle defended itself. +5 Shield.")
            print("Flame Turtle has %s Shield." % self_status.shield)
            ai_open_discard("L", state)
        else:
            ai_attack(self, self_status, "F", 9, 2, state)
            ai_open_discard("F", state)

class Cow(Enemy):
    def __init__(self):
        self.name = "Cow"
        self.hp = 50
        self.hp_max = 50
        self.rollout = 0

    def run_turn(self, state, self_status):
        if state.turn_number % 6 == 1:
            print("Cow is preparing itself!")
            self.rollout = 0
            ai_open_discard("L", state)
        else:
            print("Cow uses Rollout!")
            ai_attack(self, self_status, "L", 8 + self.rollout, 1, state)
            ai_open_discard("L", state)
            rollout += 3

class Bull(Enemy):
    def __init__(self):
        self.name = "Bull"
        self.hp = 60
        self.hp_max = 60

    def run_turn(self, state, self_status):
        if state.turn_number % 6 == 1:
            print("Bull uses Stampede!")
            ai_attack(self, self_status, "L", 50, 9, state)
            ai_open_discard("L", state)
        else:
            if len(state.incoming_effects) > 0:
                print("The Stampede is coming closer!")
            else:
                print("The Bull is exhausted.")
            ai_open_discard("L", state)

class KillerRabbit(Enemy):
    def __init__(self):
        self.name = "Killer Rabbit"
        self.hp = 25
        self.hp_max = 25

    def run_turn(self, state, self_status):
        if state.turn_number % 3 > 0:
            print("Killer Rabbit is preparing itself.")
            ai_open_discard("L", state)
        else:
            print("Killer Rabbit uses Super Fang!")
            ai_attack(self, self_status, "L", self.hp, 1, state)
            ai_open_discard("L", state)

class Wolf(Enemy):
    def __init__(self):
        self.name = "Wolf"
        self.hp = random.randrange(20, 25)
        self.hp_max = self.hp
        self.begin = random.randrange(0, 2)

    def run_turn(self, state, self_status):
        self.begin += 1
        if (self.begin + state.turn_number) % 3 == 0:
            ai_attack(self, self_status, "L", 4, 2, state)
            ai_open_discard("A", state)
        elif (self.begin + state.turn_number) % 3 == 1:
            ai_attack(self, self_status, "L", 3, 1, state)
            ai_open_discard("A", state)
        else:
            print("Wolf uses Howl! All wolves gain 2 Strength!")
            for enemy in state.enemies:
                if enemy[0].name == "Wolf":
                    enemy[1].strength += 2
            ai_open_discard("L", state)

class Slime(Enemy):
    def __init__(self):
        self.name = "Slime"
        self.hp = random.randrange(9, 13)
        self.hp_max = self.hp
        self.begin = random.randrange(0, 3)

    def run_turn(self, state, self_status):
        self.begin += 1
        if (self.begin + state.turn_number) % 3 == 0:
            ai_attack(self, self_status, "W", 4, 2, state)
            ai_open_discard("W", state)
        elif (self.begin + state.turn_number) % 3 == 1:
            ai_attack(self, self_status, "L", 3, 1, state)
            ai_open_discard("A", state)
        else:
            print("Slime is wiggling around.")
            input("")

class KingSlime(Enemy):
    name = "KingSlime"
    hp = 100
    hp_max = hp

    def run_turn(self, state, self_status):
        if state.turn_number % 13 == 1:
            ai_attack(self, self_status, "F", 100, 12, state)
            ai_open_discard("F", state)
            ai_open_discard("F", state)
            ai_open_discard("F", state)
        if state.turn_number % 3 == 0:
            ai_attack(self, self_status, "W", 2, 2, state)
            ai_open_discard("W", state)
        else:
            ai_attack(self, self_status, "L", 3, 1, state)
            ai_open_discard("A", state)

def ai_attack(enemy, status, element, damage, countdown, state):
    actual_damage = damage + status.strength
    print("%s casts for %s %s damage in %s turn(s)!" % (enemy.name, actual_damage, element, countdown))
    print("")
    state.incoming_effects.append([element, actual_damage, countdown])

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
