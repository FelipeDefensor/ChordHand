from dataclasses import dataclass
from typing import Literal

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
            hash_str += getattr(self, attr) if getattr(self, attr) else "_"
        return hash_str

    def to_symbol(self):
        if self.is_name_only():
            return self.name
        try:
            return quality_to_symbol[self]
        except KeyError:
            print(f"No symbol found for {self}")
            return "ERROR"

    def to_chordal_type(self):
        return quality_to_chordal_type[self]


quality_to_symbol = {
    ChordQuality("", "p"): "sus4",
    ChordQuality("", "p", "m"): "4/7",
    ChordQuality("", "p", fourth="p", ninth="M"): "4/7(9)",
    ChordQuality("", "p", fourth="p", thirteenth="M"): "4/7(13)",
    ChordQuality("M", ""): "(omit5)",
    ChordQuality("M", "A"): "#5",
    ChordQuality("M", "A", "m"): "#5(7)",
    ChordQuality("M", "A", "M"): "#5(maj7)",
    ChordQuality("M", "p"): "",
    ChordQuality("M", "p", ninth="M"): "(add9)",
    ChordQuality("M", "p", eleventh="A", thirteenth="M"): "(#11,13)",
    ChordQuality("M", "p", "M"): "maj7",
    ChordQuality("M", "p", "M", "M"): "maj7(9)",
    ChordQuality("M", "p", "M", thirteenth="M"): "maj7(13)",
    ChordQuality("M", "p", "M", "M", eleventh="A"): "maj7(9,#11)",
    ChordQuality("M", "p", "M", eleventh="A"): "maj7(#11)",
    ChordQuality("M", "p", "m"): "7",
    ChordQuality("M", "p", "m", "M"): "7(9)",
    ChordQuality("M", "p", "m", "M", eleventh="A"): "7(9,#11)",
    ChordQuality("M", "p", "m", ninth="A"): "7(#9)",
    ChordQuality("M", "p", "m", ninth="M", thirteenth="m"): "7(9,b13)",
    ChordQuality("M", "p", "m", ninth="M", thirteenth="M"): "7(9,13)",
    ChordQuality("M", "p", "m", ninth="m"): "7(b9)",
    ChordQuality("M", "p", "m", ninth="m", thirteenth="m"): "7(b9,b13)",
    ChordQuality("M", "p", "m", eleventh="p"): "7(11)",
    ChordQuality("M", "p", "m", thirteenth="M"): "7(13)",
    ChordQuality("M", "p", "m", thirteenth="m"): "7(b13)",
    ChordQuality("M", "p", eleventh="A"): "#11",
    ChordQuality("M", "p", sixth="M"): "6",
    ChordQuality("M", "p", sixth="M", ninth="M"): "6(9)",
    ChordQuality("M", "p", sixth="M", ninth="m"): "6(♭9)",
    ChordQuality("m", "d"): "o",
    ChordQuality("m", "d", "d"): "o7",
    ChordQuality("m", "d", "m"): "ø",
    ChordQuality("m", "d", "m", ninth="M"): "ø(9)",
    ChordQuality("m", "p"): "m",
    ChordQuality("m", "p", "M"): "m(maj7)",
    ChordQuality("m", "p", "m"): "m7",
    ChordQuality("m", "p", "m", "M"): "m7(9)",
    ChordQuality("m", "p", "m", eleventh="p"): "m7(11)",
    ChordQuality("m", "p", "m", ninth="m"): "m7(b9)",
    ChordQuality("m", "p", ninth="M"): "m(add9)",
    ChordQuality("m", "p", ninth="m"): "m(b9)",
    ChordQuality("m", "p", sixth="m"): "m6",
    ChordQuality("m", "p", sixth="m", ninth="M"): "m6(9)",
    ChordQuality("m", "p", eleventh="p"): "m(11)",
    ChordQuality("M", "p", "m", eleventh="A"): "7(#11)",
}

quality_to_chordal_type = {
    ChordQuality("", "p"): ('',),  # "sus4"
    ChordQuality("", "p", "m"): ('Y', 1),  # '"4/7"
    ChordQuality("", "p", fourth="p", ninth="M"): ('Y', 11),  # "4/7(9)"
    ChordQuality("", "p", fourth="p", thirteenth="M"): ('Y', 13),  # "4/7(13)"
    ChordQuality("M", ""): ('',),  # "(omit5)"
    ChordQuality("M", "A"): ('V', 4),  # "#5"
    ChordQuality("M", "A", "m"): ('W', 0),  # "#5(7)"
    ChordQuality("M", "A", "M"): ('Z', 4),  # "#5(maj7)"
    ChordQuality("M", "p"): ('V', 0),  # ""
    ChordQuality("M", "p", ninth="M"): ('V', 2),  # "(add9)"
    ChordQuality("M", "p", eleventh="A", thirteenth="M"): ('',),  # "(#11,13)"
    ChordQuality("M", "p", "M"): ('Z', 0),  # "maj7"
    ChordQuality("M", "p", "M", "M"): ('Z', 2),  # "maj7(9)"
    ChordQuality("M", "p", "M", thirteenth="M"): ('',),  # "maj7(13)"
    ChordQuality("M", "p", "M", "M", eleventh="A"): ('Z', 21),  # "maj7(9,#11)"
    ChordQuality("M", "p", "M", eleventh="A"): ('Z', 3),  # "maj7(#11)"
    ChordQuality("M", "p", "m"): ('Y', 0),  # "7"
    ChordQuality("M", "p", "m", "M"): ('Y', 2),  # "7(9)"
    ChordQuality("M", "p", "m", "M", eleventh="A"): ('Y', 21),  # "7(9,#11)"
    ChordQuality("M", "p", "m", ninth="A"): ('Y', 24),  # "7(#9)"
    ChordQuality("M", "p", "m", ninth="M", thirteenth="m"): ('Y', 223),  # "7(9,b13)"
    ChordQuality("M", "p", "m", ninth="M", thirteenth="M"): ('Y', 22),  # "7(9,13)"
    ChordQuality("M", "p", "m", ninth="m"): ('Y', 23),  # "7(b9)"
    ChordQuality("M", "p", "m", ninth="m", thirteenth="m"): ('Y', 2211),  # "7(b9,b13)"
    ChordQuality("M", "p", "m", eleventh="p"): ('',),  # "7(11)"
    ChordQuality("M", "p", "m", thirteenth="M"): ('Y', 4),  # "7(13)"
    ChordQuality("M", "p", "m", thirteenth="m"): ('Y', 41),  # "7(b13)"
    ChordQuality("M", "p", eleventh="A"): ('V', 3),  # "#11"
    ChordQuality("M", "p", sixth="M"): ('Z', 1),  # "6"
    ChordQuality("M", "p", sixth="M", ninth="M"): ('Z', 11),  # "6(9)"
    ChordQuality("M", "p", sixth="M", ninth="m"): ('',),  # "6(♭9)"
    ChordQuality("m", "d"): ('v', 3),  # "o"
    ChordQuality("m", "d", "d"): ('x', 0),  # "o7"
    ChordQuality("m", "d", "m"): ('y', 0),  # "ø"
    ChordQuality("m", "d", "m", ninth="M"): ('y', 1),  # "ø(9)"
    ChordQuality("m", "p"): ('v', 0),  # "m"
    ChordQuality("m", "p", "M"): ('w', 0),  # "m(maj7)"
    ChordQuality("m", "p", "m"): ('z', 0),  # "m7"
    ChordQuality("m", "p", "m", "M"): ('z', 2),  # "m7(9)"
    ChordQuality("m", "p", "m", eleventh="p"): ('z', 3),  # "m7(11)"
    ChordQuality("m", "p", "m", ninth="m"): ('',),  # "m7(b9)"
    ChordQuality("m", "p", ninth="M"): ('v', 1),  # "m(add9)"
    ChordQuality("m", "p", ninth="m"): ('',),  # "m(b9)"
    ChordQuality("m", "p", sixth="m"): ('z', 1),  # "m6"
    ChordQuality("m", "p", sixth="m", ninth="M"): ('z', 11),  # "m6(9)"
    ChordQuality("m", "p", eleventh="p"): ('v', 2),  # "m(11)"
    ChordQuality("M", "p", "m", eleventh="A"): ('Y', 3),  # "7(#11)"
}