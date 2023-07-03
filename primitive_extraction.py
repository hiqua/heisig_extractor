from params import EF


def _remove_redundant_primitive_tokens(tokens: list[str]):
    """

    E.g. [bound up, up, bound] -> [bound up]

    :param tokens:
    :return:
    """
    if not tokens:
        return []
    tokens.sort(key=len, reverse=True)
    filtered = []
    for token in tokens:
        for master_token in filtered:
            if token in master_token:
                break
        else:
            filtered.append(token)

    return filtered


def extract_primitive_elements(kanji_entry):
    """


    This returns too many primitive elements, because there's no style
    difference between primitives that are mentioned in passing but have no
    connection with the kanji (example: "four" mentioned in the description
    for "seven").

    Hopefully that's rare enough that it's easy to fix manually or ignore.

    :param kanji_entry:
    :return:
    """
    if EF.KANJI_EXPLANATION not in kanji_entry:
        # XXX: in which case?
        return

    def normalize(token):
        return token.lower().strip(' .,;:')

    tokens = [normalize(token.get_text())
              for explanation in kanji_entry[
                  EF.KANJI_EXPLANATION]
              for token in
              explanation.find_all(name='span',
                                   attrs={'class':
                                              'no-style-override2'})
              ]
    _remove_redundant_primitive_tokens(tokens)
    # TODO: it's a list
    kanji_entry[
        EF.PRIMITIVE_ELEMENTS] = ', '.join(
        _remove_redundant_primitive_tokens(
            tokens))
