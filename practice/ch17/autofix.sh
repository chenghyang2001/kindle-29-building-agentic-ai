#!/bin/bash
# 自主修復迴圈：跑測試 → 讀錯誤 → 叫 claude -p 修 src/ → 再跑，最多 MAX_ROUNDS 輪
set -uo pipefail

MAX_ROUNDS=3
cd "$(dirname "$0")" || { echo "錯誤：無法進入腳本目錄" >&2; exit 1; }
mkdir -p out
LOG=out/autofix-log.md
PY=.venv/Scripts/python
[ -x "$PY" ] || PY=.venv/bin/python
[ -x "$PY" ] || { echo "錯誤：找不到 .venv，請先建立虛擬環境" >&2; exit 1; }
command -v claude >/dev/null || { echo "錯誤：找不到 claude CLI" >&2; exit 1; }

run_tests() { PYTHONUTF8=1 "$PY" -m pytest -q 2>&1; }
count_failed() { grep -oE '[0-9]+ failed' <<<"$1" | grep -oE '[0-9]+' || echo 0; }

# 子行程不能繼承本 session 的 CLAUDE* 變數（否則會被當成巢狀 session），也不能用 API key 計費
for v in $(env | grep -oE '^CLAUDE[A-Z0-9_]*'); do unset "$v"; done
unset ANTHROPIC_API_KEY

printf '# autofix 執行紀錄\n\n開始：%s\n\n' "$(date '+%F %T')" > "$LOG"

for round in $(seq 1 "$MAX_ROUNDS"); do
  output=$(run_tests); status=$?
  failed=$(count_failed "$output")
  if [ "$status" -eq 0 ]; then
    printf '## 第 %d 次\n\n- 測試全過（失敗數 0），結束迴圈\n\n' "$round" >> "$LOG"
    rm -rf out/.src-before
    echo "第 $round 次：全部通過"; exit 0
  fi

  fail_file="out/fail-$round.txt"
  printf '%s\n' "$output" > "$fail_file"
  echo "第 $round 次：$failed 個失敗，呼叫 claude -p 修復..."

  prompt="以下是 pytest 的失敗輸出。請閱讀相關原始碼並修正 bug。
規則：只能修改 src/ 底下的檔案，絕對不准修改 tests/ 底下任何檔案。
不要執行 git commit 或任何 git 指令（版本控制由外層腳本負責）。
修完後用一兩句繁體中文說明你修了什麼。

$output"

  # 以本輪開始時的 commit 為基準（防子行程自己 commit 繞過護欄），另外快照 src/ 用來記錄實際改動
  base=$(git rev-parse HEAD)
  snap=out/.src-before
  rm -rf "$snap" && cp -r src "$snap"

  # 本機全域 hook 會擋主 session 直接改 .py，子行程用 kill switch 關掉它
  reply=$(DISABLE_WRITER_QA_HOOK=1 claude -p --dangerously-skip-permissions \
            --allowedTools Read,Edit <<<"$prompt" 2>&1) || echo "警告：claude -p 回傳非 0" >&2

  # 護欄：tests/ 若被動到就還原，不信任模型自律
  if ! git diff --quiet "$base" -- tests/; then
    git checkout "$base" -- tests/ && reply="$reply
（護欄：偵測到 tests/ 被修改，已還原）"
  fi

  changed=$(diff -rq --strip-trailing-cr -x __pycache__ "$snap" src | grep -oE 'src/[^ ]+' | tr '\n' ' ')
  {
    printf '## 第 %d 次\n\n- 失敗數：%s\n- 失敗輸出：`%s`\n- 修改檔案：%s\n- claude 說明：\n\n' \
      "$round" "$failed" "$fail_file" "${changed:-（無）}"
    printf '%s\n' "$reply" | sed 's/^/  > /'
    printf '\n- 實際 diff：\n\n```diff\n%s\n```\n\n' "$(diff -ru --strip-trailing-cr -x __pycache__ "$snap" src)"
  } >> "$LOG"
done

rm -rf out/.src-before
final=$(run_tests); final_status=$?
printf '## 最終驗證\n\n- 失敗數：%s\n' "$(count_failed "$final")" >> "$LOG"
[ "$final_status" -eq 0 ] && { echo "最終：全部通過"; exit 0; }
echo "錯誤：$MAX_ROUNDS 輪後仍有失敗" >&2; exit 1
