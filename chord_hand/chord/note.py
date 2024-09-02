from dataclasses import dataclass

STEP_TO_NAME = {-1: "X", 0: "C", 1: "D", 2: "E", 3: "F", 4: "G", 5: "A", 6: "B"}
STEP_TO_PITCH_CLASS = {0: 0, 1: 2, 2: 4, 3: 5, 4: 7, 5: 9, 6: 11}

CHROMA_TO_SIGN = {
    -2: "ꞵ",
    -1: "b",
    0: "",
    1: "#",
    2: "x",
}


@dataclass
class Note:
    step: int
    chroma: int

    def to_symbol(self):
        try:
            return STEP_TO_NAME[self.step] + CHROMA_TO_SIGN[self.chroma]
        except KeyError:
            return None

    def to_string(self):
        return (
            f'{str(self.step)}{"+" if self.chroma >= 0 else "-"}{str(abs(self.chroma))}'
        )

    @classmethod
    def from_string(cls, string):
        if len(string) == 4:
            return Note(-1, 0)
        return Note(int(string[:1]), int(string[1:]))

    def to_pitch_class(self):
        return STEP_TO_PITCH_CLASS[self.step] + self.chroma

    def __hash__(self):
        return hash(self.to_string())

    def to_dict(self):
        return {
            'step': self.step,
            'chroma': self.chroma
        }

    @classmethod
    def from_dict(cls, data):
        return Note(int(data['step']), int(data['chroma']))
