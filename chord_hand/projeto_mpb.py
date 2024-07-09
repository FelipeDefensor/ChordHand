import chord_hand.settings


def analysis_to_projeto_mpb_code(analysis, modality):
    key = analysis.type.name, analysis.step, analysis.chroma
    qualities_to_codes = chord_hand.settings.analytic_type_args_to_projeto_mpb_code[modality].get(key, None)
    if not qualities_to_codes:
        return ''
    for quality_str, code in qualities_to_codes.items():
        if analysis.quality.match_string(quality_str):
            return code
