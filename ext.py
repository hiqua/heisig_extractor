#!/usr/bin/env pypy3
"""
Notes:
* ~2x faster when using pypy.
"""
import cProfile
import csv
import logging
from pstats import SortKey

from bs4 import BeautifulSoup
from bs4.element import ResultSet

from params import FAULTY_ENTRIES, EF, F, KANJI_EXPORT_FIELDS, DEBUG
from primitive_extraction import extract_primitive_elements


def profile(func):
    def new_func(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        func(*args, **kwargs)
        pr.disable()
        pr.print_stats(sort=SortKey.CUMULATIVE)

    return new_func


def fix_faulty_entries(kanji_entries):
    """Fixes entries that are not correctly parsed.

    :param kanji_entries: All the kanji entries to fix.


    XXX: also need to remove Heisig descriptions for these as they don't
    strictly apply.
    """
    faulty_ids_to_process = list(FAULTY_ENTRIES.keys())

    for entry in kanji_entries:
        number = entry[EF.NUMBER]
        if number in faulty_ids_to_process:
            faulty_ids_to_process.remove(number)
            assert entry[EF.KEYWORD] == FAULTY_ENTRIES[

                number][EF.KEYWORD], f'Check key word in: {entry}'
            entry[EF.KANJI_FRAME] = FAULTY_ENTRIES[
                number][EF.KANJI_FRAME]

    assert len(faulty_ids_to_process) == 0


def extract_html_explanation_from_field_paragraphs(
        field_paragraphs: ResultSet) -> str:
    decoded_paragraphs = []

    for paragraph in field_paragraphs:
        allowed_classes = {
            'no-style-override2': 'primitive',
            'k-kanji-in-text-30106-0-override': 'kanji-in-text'}

        for tag in paragraph.find_all():
            logging.debug(tag['class'])

            for cls in tag['class']:
                if cls in allowed_classes:
                    tag['class'] = [allowed_classes[cls]]
                    break
            else:
                # For non-allowed tags
                logging.debug(f'Unwrapping: {tag}')
                tag.unwrap()

        # Using decode_contents instead of decode gets rid of the
        # k-kanji-explanation tags.
        decoded_paragraphs.append(paragraph.decode_contents().strip())

    logging.debug(decoded_paragraphs)

    html_explanation = ''.join(decoded_paragraphs)
    logging.debug(f'HTML explanation: {html_explanation}')
    return html_explanation


def extract_entries_from_file(file):
    with open(file) as fs:
        content = fs.read()
    soup = BeautifulSoup(content, features='html.parser')
    tables = soup.find_all('table')
    # Entries that are kanji (and can be primitives), vs primitives only
    kanji_entries, pure_primitive_entries = [], []
    for table in tables:
        entry = {}
        # generic fields that are easy to get by class.
        for field in F:
            field_paragraphs = table.find_all(name='p',
                                              attrs={'class': field.value})
            if field_paragraphs:
                entry[EF(field.value)]: ResultSet = field_paragraphs

        # Kanji Explanations, with several corresponding classes.
        for field in ("k-kanji-explanation", "k-kanji-explanation-2nd",
                      "k-kanji-explanation-28336-0-override",
                      "k-kanji-explanation-28336-0-override1",
                      "k-kanji-explanation-2nd-30110-0-override",
                      ):
            field_paragraphs = table.find_all(name='p',
                                              attrs={'class': field})
            if field_paragraphs:
                entry.setdefault(EF.KANJI_EXPLANATION, []).extend(
                    field_paragraphs)

        # Kanji explanations, html, other method
        if EF.KANJI_EXPLANATION in entry:
            explanation = extract_html_explanation_from_field_paragraphs(
                entry[EF.KANJI_EXPLANATION]
            )
            entry[EF.KANJI_EXPLANATION_HTML] = explanation

        if entry:
            if EF.NUMBER in entry:  # Considered kanji.
                extract_primitive_elements(entry)
                kanji_entries.append(entry)
            else:
                pure_primitive_entries.append(entry)
        else:
            raise ValueError(f'No field in this table: {table}')

    return kanji_entries, pure_primitive_entries


def export_primitives(primitives):
    # https://youtrack.jetbrains.com/issue/PY-29435
    # noinspection PyUnreachableCode
    if __debug__:
        # There should be at least one of these for the visual representation.
        drawing_fields = {
            EF.STROKES,
            EF.KANJI_FRAME,
            EF.KANJIBOOK_LARGER,
            EF.KANJIBOOK_LARGEST,
            EF.KANJIBOOK,
        }

        assert min(len(drawing_fields & p.keys()) for p in primitives) > 0

    with open(f'primitive_entries.csv', 'w', newline='\n') as csvfile:
        fieldnames = [
            EF.KEYWORD,
            EF.KANJI_FRAME,
            EF.STROKES,
            EF.KANJI_FRAME,
            EF.KANJIBOOK_LARGER,
            EF.KANJIBOOK_LARGEST,
            EF.KANJIBOOK,
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                extrasaction='ignore', delimiter='|',
                                dialect='unix')
        if DEBUG:
            writer.writeheader()
        for primitive in primitives:
            writer.writerow(primitive)


def export_kanji(entries, fields=KANJI_EXPORT_FIELDS):
    """
    kanji;key word;primitive elements;story;primitive meaning

    :param fields:
    :param entries:
    :return:
    """
    with open('kanji_entries.csv', 'w', newline='\n') as csvfile:
        dialect = csv.unix_dialect
        # This character doesn't seem to appear, and there doesn't seem to be
        # quoting needed anyway.
        # TODO: double-check on the final output.
        dialect.quotechar = '^'


        dialect.quoting = csv.QUOTE_MINIMAL
        # XXX: shouldn't ignore extras?
        writer = csv.DictWriter(csvfile, fieldnames=fields,
                                extrasaction='ignore', delimiter='|',
                                dialect=dialect)

        if DEBUG:
            writer.writeheader()
        for entry in entries:
            assert EF.KANJI_FRAME in entry, entry
            assert EF.NUMBER in entry, entry
            writer.writerow(entry)


def convert_field_to_string(entry, field):
    if field in entry:
        entry[field] = ''.join(r.get_text() for r in entry[field])


def sanitize(entries):
    for entry in entries:
        convert_field_to_string(entry, EF.NUMBER)
        if EF.NUMBER in entry:
            entry[EF.NUMBER] = int(entry[EF.NUMBER])

        convert_field_to_string(entry, EF.KEYWORD)
        convert_field_to_string(entry, EF.KANJI_FRAME)
        convert_field_to_string(entry, EF.KANJI_EXPLANATION)
        convert_field_to_string(entry, EF.PRIMITIVES_EXPLANATION)
        convert_field_to_string(entry, EF.STROKES)
        convert_field_to_string(entry, EF.KANJIBOOK_LARGER)
        convert_field_to_string(entry, EF.KANJIBOOK_LARGEST)
        convert_field_to_string(entry, EF.KANJIBOOK)


# @profile
def main():
    logging.info('Starting...')

    # TODO: take epub as input
    files = [
        'text/part0001.html',
        'text/part0002.html',
        'text/part0003.html',
        'text/part0004.html',
        'text/part0005.html',
        'text/part0006.html',
        'text/part0007.html',
    ]
    pure_primitive_entries = []
    kanji_entries = []
    for file in files:
        logging.info(f'Running on file: {file}')
        kanji, prim = extract_entries_from_file(file)
        kanji_entries.extend(kanji)
        pure_primitive_entries.extend(prim)

    sanitize(kanji_entries)
    sanitize(pure_primitive_entries)
    fix_faulty_entries(kanji_entries)
    assert len(kanji_entries) == 2200
    export_kanji(kanji_entries)
    export_primitives(pure_primitive_entries)
    logging.info('Done.')


if __name__ == '__main__':
    main()
