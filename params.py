import logging
from enum import Enum

# Making things easier to debug but less reliable, don't use when exporting.
DEBUG = False
# DEBUG = True

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

# The number of primitives listed in the Index 1.
NUM_PRIMITIVES = 5 + (8 * 4 + 6) + (8 * 4 + 3) + (8 * 4 + 5) + (8 * 4 + 4) + (
        8 * 3 + 2) + (8 + 4) + (8 + 3) + (8 + 3) + 7 + 4 + 4 + 2
assert NUM_PRIMITIVES == 228

# classes for kanji explanations:
"""
"k-kanji-explanation"
"k-kanji-explanation-2nd" 
"k-kanji-explanation-28336-0-override" # seems relevant, but only used in first file, so just ignore it.
"k-kanji-explanation-28336-0-override1" # this one doesn't matter
"k-kanji-explanation-2nd-30110-0-override" # seems relevant, but only used in first file, so just ignore it.
"""


# TODO: give proper name depending on semantics
class F(Enum):
    KEYWORD = 'k-keyword'
    KANJI_EXPLANATION = 'kanji-explanation'
    PRIMITIVES_EXPLANATION = 'k-primitives-explained'
    KANJI_FRAME = 'k-frame-kanji'
    NUMBER = 'k-title-page-press'
    STROKES = 'k-strokes'
    KANJIBOOK_LARGER = 'k-frame-kanjibooks-larger'
    KANJIBOOK_LARGEST = 'k-frame-kanjibook-largest'
    KANJIBOOK = 'k-frame-kanji-kanjibooks'


# XXX: hack to copy the same enum
class EF(Enum):
    KEYWORD = 'k-keyword'
    KANJI_EXPLANATION = 'kanji-explanation'
    KANJI_EXPLANATION_HTML = 'kanji-explanation-html'
    PRIMITIVES_EXPLANATION = 'k-primitives-explained'
    KANJI_FRAME = 'k-frame-kanji'
    NUMBER = 'k-title-page-press'
    STROKES = 'k-strokes'
    PRIMITIVE_ELEMENTS = 'primitive_elements'
    KANJIBOOK_LARGER = 'k-frame-kanjibooks-larger'
    KANJIBOOK_LARGEST = 'k-frame-kanjibook-largest'
    KANJIBOOK = 'k-frame-kanji-kanjibooks'


# Entries that can't be parsed directly and need manual adjustments. Don't
# trust this until you've double-checked.
FAULTY_ENTRIES = {
    99: {
        EF.KANJI_FRAME: '子',
        EF.KEYWORD: 'sniff',
    },
    129: {
        EF.KANJI_FRAME: '嗅',
        EF.KEYWORD: 'sniff',
    },
    308: {
        # Heisig uses a less common variant '喻'.
        EF.KANJI_FRAME: '喩',
        EF.KEYWORD: 'metaphor',
    },
    509: {
        EF.KANJI_FRAME: '軟',
        EF.KANJI_EXPLANATION: 'TODO',
    },
    511: {
        EF.KANJI_FRAME: '茨',
        EF.KANJI_EXPLANATION: 'TODO',
    },
    680: {
        EF.KANJI_FRAME: '惧',
        EF.KEYWORD: 'disquieting',
    },
    1011: {
        # Heisig uses a simplified variant '笺'.
        EF.KANJI_FRAME: '箋',
        EF.KEYWORD: 'stationery',
    },
    1394: {
        # This is a simplified variant of '箋'
        EF.KANJI_FRAME: '隙',
        EF.KEYWORD: 'chink',
    },
    1522: {
        # wrong kanji in the epub
        EF.KANJI_FRAME: '腕',
        EF.KEYWORD: 'arm',
    },
}

KANJI_EXPORT_FIELDS = (
    EF.NUMBER,
    EF.KANJI_FRAME,
    EF.KEYWORD,
    EF.KANJI_EXPLANATION,
    # EF.STROKES,

    # EF.PRIMITIVE_ELEMENTS,

    # EF.KANJI_EXPLANATION_HTML,
    # EF.PRIMITIVES_EXPLANATION,

)
