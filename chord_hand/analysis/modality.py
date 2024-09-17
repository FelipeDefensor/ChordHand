from enum import Enum


class Modality(Enum):
    MAJOR = 'major'
    MINOR = 'minor'


tonic_to_scale_step_chroma = {
    0: [0, 0, 0, 0, 0, 0, 0],
    1: [0, 0, 1, 0, 0, 0, 1],
    2: [0, 1, 1, 0, 0, 1, 1],
    3: [0, 0, 0, -1, 0, 0, 0],
    4: [0, 0, 0, 0, 0, 0, 1],
    5: [0, 0, 1, 0, 0, 1, 1],
    6: [0, 1, 1, 0, 1, 1, 1],
}


def get_scale_step_chroma(tonic, chroma):
    return [x + chroma for x in tonic_to_scale_step_chroma[tonic]]
