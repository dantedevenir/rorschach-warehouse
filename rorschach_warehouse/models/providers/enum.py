from enum import Enum

class Name(Enum):
    aetna = 1
    ambetter = 2
    molina = 3
    oscar = 4
    florida_blue = 5
    blue_cross = 6
    united = 7
    cigna = 8
    avmed = 9
    ameritas = 10
    healthsherpa = 11
    healthcare = 12

class Type(Enum):
    obamacare = 1
    private = 2
    group = 3