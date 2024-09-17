from dataclasses import dataclass
from typing import Optional, Union

from chord_hand.chord.quality import ChordQuality, CustomChordQuality
from chord_hand.chord.note import Note


@dataclass
class Chord:
    root: Note
    quality: Union[ChordQuality, CustomChordQuality]
    bass: Optional[Note] = None

    def __post_init__(self):
        if not self.bass:
            self.bass = self.root

    def to_symbol(self):
        root_symbol = self.root.to_symbol()
        quality_symbol = self.quality.to_symbol()
        bass_symbol = f"/{self.bass.to_symbol()}" if self.is_inverted() else ""
        if root_symbol is None or quality_symbol is None or bass_symbol is None:
            return None

        return root_symbol + quality_symbol + bass_symbol

    def is_inverted(self):
        return self.bass != self.root

    def to_dict(self):
        return {
            'root': self.root.to_dict(),
            'quality': self.quality.to_dict(),
            'bass': self.bass.to_dict(),
        }

    @classmethod
    def from_dict(cls, data):
        is_quality_custom = data['quality'].pop('custom')
        return Chord(
            root=Note(**data['root']),
            quality=ChordQuality(**data['quality']) if not is_quality_custom else CustomChordQuality(**data['quality']),
            bass=Note(**data['bass'])
        )


class NoChord:
    def __str__(self):
        return "N.C."

    def to_string(self):
        return "NoChord()"


class RepeatChord:
    def __init__(self):
        print()

    def __str__(self):
        return "%"

    def to_string(self):
        return "RepeatChord()"
