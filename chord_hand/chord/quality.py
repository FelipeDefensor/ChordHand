from dataclasses import dataclass
from typing import Literal

import chord_hand.settings

THIRD = Literal["", "M", "m", "d", "A"]
FIFTH = Literal["", "p", "d", "A"]
SEVENTH = Literal["", "M", "m", "d"]
NINTH = Literal["", "m", "M", "A"]
THIRTEENTH = Literal["", "m", "M"]
SIXTH = Literal["", "m", "M", "A"]
SECOND = Literal["", "M"]
FOURTH = Literal["", "p"]
ELEVENTH = Literal["", "p", "A"]


@dataclass
class ChordQuality:
    third: THIRD
    fifth: FIFTH
    seventh: SEVENTH = ""
    ninth: NINTH = ""
    eleventh: ELEVENTH = ""
    thirteenth: THIRTEENTH = ""
    second: SECOND = ""
    fourth: FOURTH = ""
    sixth: SIXTH = ""
    name: str = ""

    NAME_ONLY_INDICATOR = "$"

    def __repr__(self):
        return f"ChordQuality({self.to_string()})"

    def __hash__(self):
        return hash(self.to_string())

    def is_name_only(self):
        return not any(
            [getattr(self, attr) for attr in self.__dict__ if attr != "name"]
        )

    @classmethod
    def from_string(cls, string):
        if string[0] == cls.NAME_ONLY_INDICATOR:
            return cls("", "", name=string[1:])
        args = []
        for char in string:
            args.append(char if char != "_" else "")
        return cls(*args)

    def to_string(self):
        if self.is_name_only():
            return self.NAME_ONLY_INDICATOR + self.name

        hash_str = ""
        for attr in self.__dict__:
            if attr == 'name':
                continue
            hash_str += getattr(self, attr) if getattr(self, attr) else "_"
        return hash_str

    def to_symbol(self):
        if self.is_name_only():
            return self.name
        try:
            return chord_hand.settings.chord_quality_to_symbol[self]
        except KeyError:
            print(f"No symbol found for {self}")
            return "ERROR"

    def to_chordal_type(self):
        return chord_hand.settings.chord_quality_to_chordal_type[self]

    def to_dict(self):
        return self.__dict__ | {'custom': False}

    def match_string(self, string):
        string_intervals = [s if s != '_' else '' for s in string]
        own_intervals = [
            self.third,
            self.fifth,
            self.seventh,
            self.ninth,
            self.eleventh,
            self.thirteenth,
            self.second,
            self.fourth,
            self.sixth
        ]
        for string_interval, own_interval in zip(string_intervals, own_intervals):
            match = string_interval == '*' or string_interval == own_interval
            if not match:
                return False
        return True


@dataclass
class CustomChordQuality:
    name: str

    @classmethod
    def from_string(cls, value):
        return cls(value)

    def __str__(self):
        return self.to_string()

    def to_string(self):
        return self.name

    def to_symbol(self):
        return self.name

    def to_chordal_type(self):
        return None

    def to_dict(self):
        return {'name': self.name, 'custom': True}

    def to_code(self):
        return '{' + self.name + '}'