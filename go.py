#!/usr/bin/env python3

import random
import itertools

def generate_mana():
    elements = ["F", "W", "E", "L"]
    numbers = range(1, 10)
    mana = list(itertools.product(elements, numbers))
    mana += [("P", 0)] * 4
    mana *= 4
    random.shuffle(mana)
    return mana

def main():
    mana = generate_mana()
    print(mana)

main()
