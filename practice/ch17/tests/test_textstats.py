"""textstats 的 pytest 測試。"""
import pytest

from src.textstats import char_frequency, top_words, word_count


def test_word_count_basic():
    assert word_count("hello world foo") == 3


def test_word_count_multiple_spaces():
    assert word_count("  hello    world \t\n foo  ") == 3


def test_word_count_empty():
    assert word_count("") == 0


def test_word_count_none_raises():
    with pytest.raises(ValueError):
        word_count(None)


def test_char_frequency_counts_and_skips_spaces():
    assert char_frequency("aab b") == {"a": 2, "b": 2}


def test_top_words_order():
    text = "cat dog cat bird dog cat"
    assert top_words(text, 2) == [("cat", 3), ("dog", 2)]


def test_top_words_case_insensitive_and_tie_break():
    text = "B a A b c"
    assert top_words(text, 3) == [("a", 2), ("b", 2), ("c", 1)]


def test_top_words_negative_n_raises():
    with pytest.raises(ValueError):
        top_words("a b", -1)
