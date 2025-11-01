from __future__ import annotations
import pandas as pd
from typing import Mapping
from ..core.contracts import DEFAULT_RENAME_MAP


def normalize_columns(
    df: pd.DataFrame, rename_map: Mapping[str, str] | None = None
) -> pd.DataFrame:
    mapping = {k.lower(): v for k, v in (rename_map or DEFAULT_RENAME_MAP).items()}
    df = df.rename(columns=lambda c: mapping.get(str(c).lower(), str(c)))
    return df
