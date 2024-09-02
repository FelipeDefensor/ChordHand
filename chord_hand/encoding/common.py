from chord_hand.chord.keymap import NEXT_BAR_CODE, REPEAT_CHORD_CODE, SLASH


def decode_chord_code_sequence(text):
    # delay import so decoder is available
    from chord_hand.settings import decoder

    codes = text.replace("\n", "").split(" ")
    result = []
    for measure in codes:
        chords = decoder.decode_measure(measure)
        chords = [c for c in chords if c]
        result.append(chords)

    return result


def split_measure_codes_into_chord_codes(code):
    if code == "":
        return ['']

    rest = list(code)
    result = []

    while rest:
        if rest[0] == REPEAT_CHORD_CODE:
            result.append(rest.pop(0))
            continue

        root_code = rest.pop(0)
        quality_code = rest.pop(0) if rest and rest[0] != '{' else ''
        if not rest:
            result.append(root_code + quality_code)
            break
        if rest[0] == '{':
            code = root_code + rest.pop(0)  # get bracket
            while rest:
                code += rest.pop(0)
                if code[-1] == '}':
                    break
            if code[-1] != '}':
                code += '}'
            result.append(code)

        elif rest[0] == SLASH:
            rest.pop(0)  # ignore the slash
            bass_code = rest.pop(0) if rest else ''
            result.append(root_code + quality_code + bass_code)
        else:
            result.append(root_code + quality_code)

    return result
