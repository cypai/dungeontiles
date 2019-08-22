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
    def __init__(self):
        self.tapped = False
        self.repeatable = True
        self.repeatable_max = 1
        self.repeatable_x = 0
        self.exhausted = False

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

class Spark(Spell):
    def __init__(self):
        self.tapped = False
        self.repeatable = True
        self.repeatable_max = float("inf")
        self.repeatable_x = 0
        self.exhausted = False

    def name(self):
        return "Spark"

    def description(self):
        return "(Component) must be a 1. Casts 1 (Elemental). (Repeatable)."

    def tile_reqs(self):
        return [(1, "I")]

    def find_castable(self, hand):
        return list(map(lambda t: [t], filter(lambda x: x[0] in ["F", "W", "E"] and x[1] == 1, hand)))

    def cast(self, tiles, state):
        element = tiles[0][0]
        standard_target_menu(element, 1, state)

class Ground(Spell):
    def __init__(self):
        self.tapped = False
        self.repeatable = True
        self.repeatable_max = 2
        self.repeatable_x = 0
        self.exhausted = False

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

class Bump(Spell):
    def name(self):
        return "Bump"

    def description(self):
        return "Transform a tile into its (Successor)."

    def tile_reqs(self):
        return [(1, "I")]

    def find_castable(self, hand):
        return list(map(lambda t: [t], hand))

    def cast(self, tiles, state):
        element, number = tiles[0]
        if element in ["F", "W", "E"]:
            state.hand.append((element, number + 1 if number < 9 else 1))
        elif element == "S":
            state.hand.append((element, number + 3 if number < 9 else 0))
        elif element == "L":
            state.hand.append((element, number + 4 if number < 9 else 1))

class Nudge(Spell):
    def name(self):
        return "Nudge"

    def description(self):
        return "Transform a tile into its (Predecessor)."

    def tile_reqs(self):
        return [(1, "I")]

    def find_castable(self, hand):
        return list(map(lambda t: [t], hand))

    def cast(self, tiles, state):
        element, number = tiles[0]
        if element in ["F", "W", "E"]:
            state.hand.append((element, number - 1 if number > 1 else 9))
        elif element == "S":
            state.hand.append((element, number - 3 if number > 0 else 9))
        elif element == "L":
            state.hand.append((element, number - 4 if number > 1 else 9))

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
        aoe_target_menu(element, 5, state)

class Explosion(Spell):
    def name(self):
        return "Explosion"

    def description(self):
        return "Casts (Numeric)x3 (Elemental) (AOE). (Exhaust)."

    def tile_reqs(self):
        return [(3, "I")]

    def find_castable(self, hand):
        return find_identical(3, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        numeric = tiles[2][1]
        aoe_target_menu(element, numeric * 3, state)
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

class RampStrike(Spell):
    def name(self):
        return "Ramp Strike"

    def description(self):
        return "Casts 3 (Elemental). Increases damage by 1 per spell cast this turn."

    def tile_reqs(self):
        return [(3, "S")]

    def find_castable(self, hand):
        return find_sequences(3, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        standard_target_menu(element, 1 + state.spells_casted, state)

class Split(Spell):
    def name(self):
        return "Split"

    def description(self):
        return "Split an Elemental tile into 1s."

    def tile_reqs(self):
        return [(1, "S")]

    def find_castable(self, hand):
        return list(map(lambda t: [t], filter(lambda x: x[0] in ["F", "W", "E"], hand)))

    def cast(self, tiles, state):
        element, number = tiles[0]
        while len(state.hand) < 15 and number > 0:
            number -= 1
            state.hand.append((element, 1))

class Break(Spell):
    def name(self):
        return "Break"

    def description(self):
        return "Inflict 3 (Elemental) Break. F/W/E only."

    def tile_reqs(self):
        return [(3, "I")]

    def find_castable(self, hand):
        return find_identical(3, hand, ["F", "W", "E"])

    def cast(self, tiles, state):
        element = tiles[0][0]
        enemy, enemy_status = nonattack_target_menu(state)
        enemy_status.elem_break[element] += 3

class Dragonbreath(Spell):
    def name(self):
        return "Dragonbreath"

    def description(self):
        return "Cast 25 (Elemental) (AOE)."

    def tile_reqs(self):
        return [(9, "S")]

    def find_castable(self, hand):
        return find_sequences(9, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        aoe_target_menu(element, 25, state)

class SummonDragon(Spell):
    def name(self):
        return "Summon Dragon"

    def description(self):
        return "Summon an (Elemental) Dragon, which does 12 AOE damage to all enemies at the end of your turn."

    def tile_reqs(self):
        return [(9, "S")]

    def find_castable(self, hand):
        return find_sequences(9, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        state.status.dragon = element

class DragonScale(Spell):
    def name(self):
        return "Dragon Scale"

    def description(self):
        return "Drawn Elemental Tiles transform their element to (Elemental)."

    def tile_reqs(self):
        return [(9, "S")]

    def find_castable(self, hand):
        return find_sequences(9, hand)

    def cast(self, tiles, state):
        element = tiles[0][0]
        state.status.dragon_scale = element

def find_identical(amount, hand, allowed_elements=["F", "W", "E", "S", "L"]):
    count = {}
    for tile in hand:
        if tile[0] in allowed_elements:
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
    for enemy in state.enemies:
        menu_options[str(index)] = enemy
        print("%s: %s" % (index, enemy[0].name))
        index += 1
    incoming_index = index
    for incoming in state.incoming_effects:
        menu_options[str(index)] = incoming
        print("%s: incoming %s %s (%s turns)" % (index, incoming[0], incoming[1], incoming[2]))
        index += 1
    while True:
        choice = input(">> ")
        if choice in menu_options:
            target = menu_options[choice]
            if int(choice) >= incoming_index:
                if damage > target[1]:
                    print("Incoming attack was disrupted!")
                    state.incoming_effects.remove(target)
                else:
                    print("Incoming attack decreased in power by %s." % damage)
                    target[1] -= damage
            else:
                actual_damage = damage
                if element in ["F", "W", "E"] and target[1].elem_break[element] > 0:
                    actual_damage = int(damage * 1.5)
                print("%s took %s %s damage!" % (target[0].name, actual_damage, element))
                target[0].hp -= actual_damage
                if target[0].hp <= 0:
                    print("%s was defeated!" % target[0].name)
                    state.enemies.remove(target)
            input("")
            return

def nonattack_target_menu(state):
    print("Target?")
    menu_options = {}
    index = 1
    for enemy in state.enemies:
        menu_options[str(index)] = enemy
        print("%s: %s" % (index, enemy[0].name))
        index += 1
    while True:
        choice = input(">> ")
        if choice in menu_options:
            target = menu_options[choice]
            return target

def aoe_target_menu(element, damage, state):
    print("Target?")
    print("e: All enemies")
    print("i: Incoming attacks")
    while True:
        choice = input(">> ")
        if choice == "e":
            for enemy in state.enemies[:]:
                actual_damage = damage
                if element in ["F", "W", "E"] and enemy[1].elem_break[element] > 0:
                    actual_damage = int(damage * 1.5)
                print("%s took %s %s damage!" % (enemy[0].name, actual_damage, element))
                enemy[0].hp -= actual_damage
                if enemy[0].hp <= 0:
                    print("%s was defeated!" % enemy[0].name)
                    state.enemies.remove(enemy)
            input("")
            return
        if choice == "i":
            for incoming in state.incoming_effects[:]:
                if damage > incoming[1]:
                    print("Incoming attack was disrupted!")
                    state.incoming_effects.remove(incoming)
                else:
                    print("Incoming attack decreased in power by %s." % damage)
                    incoming[1] -= damage
            input("")
            return

def elementalist_rewards():
    return [QuickInvoke(), Spark(), Ground(), DualInvoke(), Blast(), Strike(), Explosion(), RampStrike(), Split(), Bump(), Nudge()]
