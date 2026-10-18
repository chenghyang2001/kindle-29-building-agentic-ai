"""文字統計工具：字數、字元頻率、最常出現的單字。"""
from collections import Counter


def word_count(text):
    """回傳以空白分隔的單字數；連續空白、tab、換行都視為一個分隔。"""
    if text is None:
        raise ValueError("text 不可為 None")
    return len(text.split())


def char_frequency(text):
    """回傳非空白字元的出現次數 dict（區分大小寫）。"""
    if text is None:
        raise ValueError("text 不可為 None")
    return dict(Counter(ch for ch in text if not ch.isspace()))


def top_words(text, n):
    """回傳出現次數最多的前 n 個單字 [(word, count)]，不分大小寫。

    排序：次數由多到少；次數相同時依字母順序，確保結果穩定可測。
    """
    if n < 0:
        raise ValueError("n 不可為負數")
    counts = Counter(w.lower() for w in text.split())
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[:n]
