"""第 12 章演練：代理可呼叫的三個工具，以及給模型看的 JSON schema。"""
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ALLOWED_DIRS = [BASE_DIR / "data", BASE_DIR / "out"]


class ToolError(Exception):
    """工具輸入不合法時拋出，代理會把訊息餵回模型。"""


def _safe_path(path: str) -> Path:
    """把路徑限制在 data/ 或 out/ 內，防止模型讀寫任意檔案。"""
    if not isinstance(path, str) or not path.strip():
        raise ToolError("path 必須是非空字串")
    resolved = (BASE_DIR / path).resolve()
    for allowed in ALLOWED_DIRS:
        if resolved == allowed.resolve() or allowed.resolve() in resolved.parents:
            return resolved
    raise ToolError(f"路徑越界：{path}（只允許 data/ 或 out/）")


def read_csv(path: str) -> list[dict]:
    """讀取 CSV，數值欄位自動轉成 int/float。"""
    file_path = _safe_path(path)
    if not file_path.is_file():
        raise ToolError(f"檔案不存在：{path}")
    with file_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key, value in row.items():
            row[key] = _to_number(value)
    return rows


def _to_number(value):
    """CSV 讀出來都是字串，能轉數字就轉，方便後續計算。"""
    for cast in (int, float):
        try:
            return cast(value)
        except (TypeError, ValueError):
            continue
    return value


def compute_stats(rows: list[dict], group_by: str) -> list[dict]:
    """依 group_by 分組，回傳各組總營收、平均單筆營收、筆數（依總營收降冪）。"""
    if not isinstance(rows, list):
        raise ToolError("rows 必須是 list")
    if not rows:
        return []
    groups: dict[str, list[float]] = {}
    for row in rows:
        if group_by not in row:
            raise ToolError(f"欄位不存在：{group_by}")
        try:
            revenue = float(row["quantity"]) * float(row["unit_price"])
        except (KeyError, TypeError, ValueError) as e:
            raise ToolError(f"資料列缺少 quantity/unit_price 或格式錯誤：{e}") from e
        groups.setdefault(str(row[group_by]), []).append(revenue)
    stats = [
        {
            group_by: key,
            "total_revenue": round(sum(vals), 2),
            "avg_revenue": round(sum(vals) / len(vals), 2),
            "count": len(vals),
        }
        for key, vals in groups.items()
    ]
    return sorted(stats, key=lambda s: s["total_revenue"], reverse=True)


def write_report(path: str, markdown: str) -> dict:
    """把 Markdown 報告寫到 out/（或 data/）內。"""
    file_path = _safe_path(path)
    if not isinstance(markdown, str) or not markdown.strip():
        raise ToolError("markdown 不可為空")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(markdown, encoding="utf-8")
    return {"written": str(file_path.relative_to(BASE_DIR)).replace("\\", "/"),
            "chars": len(markdown)}


TOOL_SCHEMAS = [
    {
        "name": "read_csv",
        "description": "讀取 data/ 或 out/ 內的 CSV 檔，回傳資料列陣列（數值已轉型）。",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "相對路徑，例如 data/sales.csv"}},
            "required": ["path"],
        },
    },
    {
        "name": "compute_stats",
        "description": "依指定欄位分組，計算各組總營收(quantity*unit_price)、平均單筆營收與筆數。"
                       "rows 可傳字串 \"$last_rows\" 代表上一次 read_csv 的結果。",
        "input_schema": {
            "type": "object",
            "properties": {
                "rows": {"description": "資料列陣列，或字串 \"$last_rows\""},
                "group_by": {"type": "string", "description": "分組欄位，例如 region"},
            },
            "required": ["rows", "group_by"],
        },
    },
    {
        "name": "write_report",
        "description": "把 Markdown 報告寫入 out/ 內的檔案。",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "例如 out/report.md"},
                "markdown": {"type": "string", "description": "報告全文（Markdown）"},
            },
            "required": ["path", "markdown"],
        },
    },
]

TOOLS = {"read_csv": read_csv, "compute_stats": compute_stats, "write_report": write_report}


if __name__ == "__main__":
    sales_rows = read_csv("data/sales.csv")
    print(len(sales_rows), compute_stats(sales_rows, "region")[0])
