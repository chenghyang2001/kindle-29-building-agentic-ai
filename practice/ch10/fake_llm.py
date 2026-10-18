"""可預測的假 LLM：依提示詞前綴與關鍵字回傳寫死的回應，不呼叫任何真模型。

提示詞格式約定：每個模式用不同的前綴標籤（例如 "[react]"、"[critique]"），
這樣同一個函式就能扮演四種模式裡的 LLM。
"""
import json
import re

# 擷取階段用：辨識「欄位：值」這種中文鍵值對
_FIELD_PATTERN = re.compile(r"(\S+?)：(\S+?)(?:[，。,]|$)")
_KEY_MAP = {"姓名": "name", "年齡": "age", "城市": "city"}


def fake_llm(prompt: str) -> str:
    """依前綴分派到對應的假回應。"""
    if prompt is None:
        raise ValueError("prompt 不可為 None")
    handlers = {
        "[react]": _react,
        "[draft]": _draft,
        "[critique]": _critique,
        "[revise]": _revise,
        "[plan]": _plan,
        "[execute]": _execute,
        "[extract]": _extract,
        "[transform]": _transform,
        "[summary]": _summary,
    }
    for prefix, handler in handlers.items():
        if prompt.startswith(prefix):
            return handler(prompt[len(prefix):].strip())
    return "我不知道。"


# ---------- ReAct ----------
def _react(body: str) -> str:
    # 「無限」問題：假 LLM 永遠想再查一次，用來測試步數上限
    if "無限" in body:
        return "Thought: 資料不夠，再查一次\nAction: lookup[未知城市人口]"
    if "Observation: 2500100" in body:
        return "Thought: 已經得到答案\nFinal Answer: 2500100"
    if "Observation: 2500000" in body:
        return "Thought: 人口查到了，再加 100\nAction: calculator[2500000 + 100]"
    if "台北" in body:
        return "Thought: 先查台北人口\nAction: lookup[台北人口]"
    return "Thought: 這題不需要工具\nFinal Answer: 我不知道"


# ---------- Reflection ----------
def _draft(topic: str) -> str:
    return f"{topic}是會使用工具的程式。"


def _critique(draft: str) -> str:
    if "頑固" in draft:
        return "FAIL: 這份草稿怎麼改都不夠好"
    if "自主" not in draft:
        return "FAIL: 缺少「自主決策」的說明"
    if "例如" not in draft:
        return "FAIL: 缺少範例"
    return "PASS"


def _revise(body: str) -> str:
    draft, _, critique = body.partition("\n---\n")
    if "自主" in critique:
        return draft + "它能自主決策下一步。"
    if "範例" in critique:
        return draft + "例如 ReAct 迴圈。"
    return draft + "（已潤飾）"


# ---------- Planning ----------
def _plan(goal: str) -> str:
    if not goal:
        return ""
    if "部落格" in goal:
        return "1. 蒐集資料\n2. 列出大綱\n3. 撰寫草稿\n4. 校稿發布"
    return f"1. 理解目標：{goal}\n2. 執行目標\n3. 檢查結果"


def _execute(step: str) -> str:
    return f"完成：{step}"


# ---------- Sequential ----------
def _extract(text: str) -> str:
    pairs = _FIELD_PATTERN.findall(text)
    return ";".join(f"{key}={value}" for key, value in pairs)


def _transform(body: str) -> str:
    record = {}
    for pair in filter(None, body.split(";")):
        key, _, value = pair.partition("=")
        record[_KEY_MAP.get(key, key)] = int(value) if value.isdigit() else value
    return json.dumps(record, ensure_ascii=False)


def _summary(body: str) -> str:
    record = json.loads(body)
    name = record.get("name", "某人")
    age = record.get("age", "?")
    city = record.get("city", "未知")
    return f"{name}，{age} 歲，住在{city}。"


if __name__ == "__main__":
    print(fake_llm("[react] 台北人口加 100 是多少？"))
    print(fake_llm("[extract] 姓名：王小明，年齡：30，城市：台北。"))
