from dataclasses import dataclass
from enum import StrEnum, auto

from chord_hand.chord.note import Note, CHROMA_TO_SIGN
from chord_hand.analysis.analysis import str_to_note, STEP_TO_NOTE_NAME


class Modality(StrEnum):
    MAJOR = auto()
    MINOR = auto()


@dataclass
class HarmonicRegion:
    tonic: Note
    modality: Modality

    def to_symbol(self):
        step = STEP_TO_NOTE_NAME[self.tonic.step]
        accidental = CHROMA_TO_SIGN[self.tonic.chroma] if self.tonic.chroma else ''
        modality = 'm' if self.modality == Modality.MINOR else ''
        return step + accidental + modality

    @classmethod
    def from_string(cls, s):
        if len(s) > 1 and s[1] not in list(CHROMA_TO_SIGN.values()) + ['m', 'M']: # invalid second letter
            return None

        try:
            tonic = str_to_note(s[0].upper() + s[1:])
        except KeyError:
            return None

        if tonic.step == -1:  # -1 indicates an error
            return None

        if s[0].islower() or (len(s) > 1 and s[1] == 'm'):
            modality = Modality.MINOR
        else:
            modality = Modality.MAJOR

        return HarmonicRegion(tonic, modality)

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