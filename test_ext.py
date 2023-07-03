from bs4 import BeautifulSoup

from ext import remove_redundant_primitive_tokens, clear_kanji_explanation


def test_remove_redundant_primitive_tokens():
    result = remove_redundant_primitive_tokens(['bound', 'bound up', 'up'])
    assert len(result) == 1
    assert result[0] == 'bound up'



def template_test_clear_kanji_explanations(html, expected_html):
    soup = BeautifulSoup(html, features='html.parser')
    results = soup.find_all(name='p', attrs={'class': 'k-kanji-explanation'})
    output_html = clear_kanji_explanation(results)
    assert output_html == expected_html


def test_clear_kanji_explanations_1():
    html = ('<p class="k-kanji-explanation">word '
            'word <span class="some-bad-class">inside_word</span> blah '
            'word. [1]</p>')

    expected_html = 'word word\ninside_word\nblah word. [1]\n'
    template_test_clear_kanji_explanations(html, expected_html)


def test_clear_kanji_explanations_2():
    html = ('<p class="k-kanji-explanation"><span '
            'class="no-style-override2">Person . . . monkey</span>. [7]</p> ')

    expected_html = ('<span class="no-style-override2">\n Person . . . '
                     'monkey\n</span>\n. [7]\n')

    template_test_clear_kanji_explanations(html, expected_html)


test_clear_kanji_explanations_2()
test_clear_kanji_explanations_1()
