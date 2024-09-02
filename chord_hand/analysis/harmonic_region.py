from dataclasses import dataclass

from chord_hand.analysis.modality import Modality
from chord_hand.chord.note import Note


@dataclass
class HarmonicRegion:
    tonic: Note
    modality: Modality

    def to_symbol(self):
        modality = 'm' if self.modality == Modality.MINOR else ''
        return self.tonic.to_symbol() + modality

    def to_dict(self):
        return {
            'tonic': self.tonic.to_dict(),
            'modality': self.modality.value
        }

    @classmethod
    def from_dict(cls, data):
        return HarmonicRegion(
            tonic=Note.from_dict(data['tonic']),
            modality=Modality(data['modality'])
        )