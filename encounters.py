#!/usr/bin/env python3

import random

import enemies

def generate_encounter():
    possible_encounters = [
            [enemies.FlameTurtle()],
            [enemies.Slime(), enemies.Slime()]
            ]
    return random.choice(possible_encounters)

def generate_hard_encounter():
    possible_encounters = [
            [enemies.FlameTurtle(), enemies.Slime()],
            [enemies.Slime(), enemies.Slime(), enemies.Slime(), enemies.Slime()]
            ]
    return random.choice(possible_encounters)
