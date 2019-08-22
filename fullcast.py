#!/usr/bin/env python3

class FullCastSpell:
    def name(self):
        return ""

    def description(self):
        return ""

    def cast(self, hand, state):
        pass

class ClearIncoming(FullCastSpell):
    def name(self):
        return "Clear Incoming"

    def description(self):
        return "Disrupts all incoming attacks from the enemy."

    def cast(self, hand, state):
        print("All incoming attacks were Disrupted!")
        state.incoming_effects = []

class BasicFullCast(FullCastSpell):
    def name(self):
        return "Basic Full Cast"

    def description(self):
        return "Base Power: 30"

    def cast(self, hand, state):
        state.full_cast_damage += 30

class SequencePower(FullCastSpell):
    def name(self):
        return "Sequence Power"

    def description(self):
        return "Each sequence adds 2 power."

    def cast(self, hand, state):
        sets = [hand[x:x+3] for x in range(0, len(hand), 3)]
        sequences = 0
        for s in sets:
            if s[0] != s[1]:
                sequences += 1
        state.full_cast_damage += sequences * 2

class TriplePower(FullCastSpell):
    def name(self):
        return "Triple Power"

    def description(self):
        return "Each triple adds 3 power."

    def cast(self, hand, state):
        sets = [hand[x:x+3] for x in range(0, len(hand), 3)]
        triples = 0
        for s in sets:
            if s[0] == s[1]:
                triples += 1
        state.full_cast_damage += triples * 3
