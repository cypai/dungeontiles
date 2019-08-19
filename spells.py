#!/usr/bin/env python3

class Spell:

    def __init__(self):
        self.tapped = False
        self.repeatable = False
        self.repeatable_max = 0
        self.repeatable_x = 0
        self.exhausted = False

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
    def name(self):
        return "Invoke"

    def description(self):
        return "Casts 2 (Elemental)."

    def tile_reqs(self):
        return [(1, "I")]

    def find_castable(self, hand):
        return list(map(lambda t: [t], hand))

    def cast(self, tiles, state):
        element = tiles[0][0]
        standard_target_menu(element, 2, state)

class QuickInvoke(Spell):
    repeatable = True
    repeatable_max = 1

    def name(self):
        return "Quick Invoke"

    def description(self):
        return "Casts 1 (Elemental). 1 (Repeatable)."

    def tile_reqs(self):
        return [(1, "I")]

    def find_castable(self, hand):
        return list(map(lambda t: [t], hand))

    def cast(self, tiles, state):
        element = tiles[0][0]
        standard_target_menu(element, 1, state)

class Ground(Spell):
    repeatable = True
    repeatable_max = 2

    def name(self):
        return "Ground"

    def description(self):
        return "Discard. 2 (Repeatable)."

    def tile_reqs(self):
        return [(1, "I")]

    def find_castable(self, hand):
        return list(map(lambda t: [t], hand))

    def cast(self, tiles, state):
        pass

class DualInvoke(Spell):
    def name(self):
        return "Dual Invoke"

    def description(self):
        return "Casts 2 (Elemental) 2 times."

    def tile_reqs(self):
        return [(2, "I")]

    def find_castable(self, hand):
        return find_identical(2, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        standard_target_menu(element, 1, state)
        standard_target_menu(element, 1, state)

class Blast(Spell):
    def name(self):
        return "Blast"

    def description(self):
        return "Casts 5 (Elemental) (AOE)."

    def tile_reqs(self):
        return [(3, "I")]

    def find_castable(self, hand):
        return find_identical(3, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        state.outgoing_effects.append([element, 5, True])

class Explosion(Spell):
    def name(self):
        return "Explosion"

    def description(self):
        return "Casts (Numeric)x3 (Elemental) (AOE). (Exhaust)."

    def tile_reqs(self):
        return [(3, "I")]

    def find_castable(self, hand):
        if self.exhausted:
            return []
        return find_identical(3, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        numeric = tiles[2][1]
        state.outgoing_effects.append([element, numeric * 3, True])
        self.exhausted = True

class Strike(Spell):
    def name(self):
        return "Strike"

    def description(self):
        return "Casts 7 (Elemental)."

    def tile_reqs(self):
        return [(3, "S")]

    def find_castable(self, hand):
        return find_sequences(3, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        standard_target_menu(element, 7, state)

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

def standard_target_menu(element, damage, state):
    print("Target?")
    menu_options = {}
    index = 1
    for incoming in state.incoming_effects:
        menu_options[str(index)] = incoming
        print("%s: incoming %s %s (%s turns)" % (index, incoming[0], incoming[1], incoming[2]))
        index += 1
    enemy_index = index
    menu_options[str(index)] = state.enemy
    print("%s: %s" % (index, state.enemy.name))
    while True:
        choice = input(">> ")
        if choice in menu_options:
            target = menu_options[choice]
            if int(choice) < enemy_index:
                if damage > target[1]:
                    print("Incoming attack was disrupted!")
                    state.incoming_effects.remove(target)
                else:
                    print("Incoming attack decreased in power by %s." % damage)
                    target[1] -= damage
            else:
                print("%s took %s %s damage!" % (target.name, damage, element))
                target.hp -= damage
            input("")
            return


def elementalist_rewards():
    return [QuickInvoke(), Ground(), DualInvoke(), Blast(), Strike(), Explosion()]
