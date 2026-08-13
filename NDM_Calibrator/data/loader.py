"""CSV / XLSX data loading with robust error handling."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd

from core.exceptions import DataError


def load_dataframe(path: Path | str) -> Tuple[pd.DataFrame, str]:
    """Load a CSV or XLSX file into a DataFrame.

    Returns (df, source_name). Raises DataError with a friendly message on
    any failure (missing file, bad encoding, empty workbook, ...).
    """
    path = Path(path)
    if not path.exists():
        raise DataError(f"文件不存在: {path}")

    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            return _load_csv(path), path.name
        if suffix in (".xlsx", ".xlsm"):
            return _load_xlsx(path), path.name
        raise DataError(f"不支持的文件类型: {suffix} (仅支持 CSV / XLSX)")
    except DataError:
        raise
    except Exception as exc:
        raise DataError(f"读取文件失败: {exc}") from exc


def _load_csv(path: Path) -> pd.DataFrame:
    # Try UTF-8, then GBK (common on Chinese Windows), then latin-1 as fallback.
    errors = []
    for encoding in ("utf-8", "gbk", "utf-8-sig", "latin-1"):
        try:
            df = pd.read_csv(path, encoding=encoding)
            if df.empty:
                raise DataError(f"CSV 文件 {path.name} 没有数据")
            return df
        except (UnicodeDecodeError, pd.errors.ParserError, DataError) as exc:
            errors.append(f"{encoding}: {exc}")
    raise DataError(f"无法解析 CSV 文件 {path.name}: {'; '.join(errors)}")


def _load_xlsx(path: Path) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    if not xl.sheet_names:
        raise DataError(f"Excel 文件 {path.name} 没有工作表")
    df = pd.read_excel(xl, sheet_name=xl.sheet_names[0])
    if df.empty:
        raise DataError(f"Excel 文件 {path.name} 第一个工作表没有数据")
    return df
