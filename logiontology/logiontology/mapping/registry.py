#!/usr/bin/env python3
"""
HVDC Ontology Mapper v2.6 - DataFrame → RDF 변환

mapping_rules_v2.6.json 기반으로 DataFrame을 RDF로 변환하는 최신 실전 예제
"""

from __future__ import annotations
import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD
import json
import yaml
from pathlib import Path
import logging
from datetime import datetime
from typing import Any, Callable

logger = logging.getLogger(__name__)

# 🆕 NEW: mapping_utils에서 새로운 함수들 import
try:
    from mapping_utils import (
        normalize_code_num,
        codes_match,
        is_valid_hvdc_vendor,
        is_warehouse_code,
    )
except ImportError:
    # Fallback functions if mapping_utils is not available
    def normalize_code_num(code):
        import re

        return re.sub(r"\D", "", str(code)) if code else ""

    def codes_match(code1, code2):
        return normalize_code_num(code1) == normalize_code_num(code2)

    def is_valid_hvdc_vendor(code, valid_codes):
        return str(code) in valid_codes

    def is_warehouse_code(code, warehouse_codes):
        return any(wc in str(code) for wc in warehouse_codes)


Mapper = Callable[[dict[str, Any]], dict[str, Any]]


class MappingRegistry:
    def __init__(self) -> None:
        self.rules: dict[str, Any] = {}
        self.ns: dict[str, Namespace] = {}
        self.field_map: dict[str, str] = {}
        self.property_mappings: dict[str, dict] = {}
        self.class_mappings: dict[str, str] = {}
        self.hvdc_code3_valid: list[str] = ["HE", "SIM"]
        self.warehouse_codes: list[str] = ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz", "DSV MZP"]
        self.month_matching: str = "operation_month_eq_eta_month"

    def load(self, path: str | Path) -> None:
        """Load mapping rules from JSON or YAML file"""
        path = Path(path)
        if path.suffix.lower() == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            data = yaml.safe_load(path.read_text())

        self.rules = data or {}
        self._parse_rules()

    def _parse_rules(self) -> None:
        """Parse loaded rules into internal structures"""
        try:
            self.ns = {k: Namespace(v) for k, v in self.rules.get("namespaces", {}).items()}
            self.field_map = self.rules.get("field_map", {})
            self.property_mappings = self.rules.get("property_mappings", {})
            self.class_mappings = self.rules.get("class_mappings", {})
            self.hvdc_code3_valid = self.rules.get("hvdc_code3_valid", ["HE", "SIM"])
            self.warehouse_codes = self.rules.get(
                "warehouse_codes", ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz", "DSV MZP"]
            )
            self.month_matching = self.rules.get("month_matching", "operation_month_eq_eta_month")
        except Exception as e:
            logger.warning(f"Failed to parse rules, using defaults: {e}")
            self._set_defaults()

    def _set_defaults(self) -> None:
        """Set default values when rules parsing fails"""
        self.ns = {
            "ex": Namespace("http://samsung.com/project-logistics#"),
            "rdf": Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
            "rdfs": Namespace("http://www.w3.org/2000/01/rdf-schema#"),
            "xsd": Namespace("http://www.w3.org/2001/XMLSchema#"),
        }
        self.field_map = {}
        self.property_mappings = {}
        self.class_mappings = {}

    def apply_hvdc_filters_to_rdf(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        🆕 NEW: RDF 변환 전 HVDC 필터 적용

        Args:
            df: 원본 DataFrame

        Returns:
            pd.DataFrame: 필터링된 DataFrame
        """
        print("🔧 RDF 변환 전 HVDC 필터 적용 중...")

        # A. HVDC CODE 정규화 적용
        if "HVDC CODE" in df.columns and "HVDC CODE 4" in df.columns:
            df["HVDC_CODE_NORMALIZED"] = df["HVDC CODE"].apply(normalize_code_num)
            df["HVDC_CODE4_NORMALIZED"] = df["HVDC CODE 4"].apply(normalize_code_num)

            # 코드 매칭 검증
            df["CODE_MATCH"] = df.apply(
                lambda row: codes_match(row["HVDC CODE"], row["HVDC CODE 4"]), axis=1
            )

            # 매칭되지 않는 행 필터링
            original_count = len(df)
            df = df[df["CODE_MATCH"] == True]
            filtered_count = len(df)
            print(
                f"  ✅ HVDC CODE 매칭: {original_count} → {filtered_count} (필터링: {original_count - filtered_count}건)"
            )

        # B. CODE 3 필터 (HE, SIM만 처리)
        if "HVDC CODE 3" in df.columns:
            original_count = len(df)
            df = df[
                df["HVDC CODE 3"].apply(lambda x: is_valid_hvdc_vendor(x, self.hvdc_code3_valid))
            ]
            filtered_count = len(df)
            print(
                f"  ✅ 벤더 필터 (HE/SIM): {original_count} → {filtered_count} (필터링: {original_count - filtered_count}건)"
            )

        # C. 창고명(임대료) 필터 & SQM 적용
        if "HVDC CODE" in df.columns:
            warehouse_mask = df["HVDC CODE"].apply(
                lambda x: is_warehouse_code(x, self.warehouse_codes)
            )
            warehouse_df = df[warehouse_mask].copy()

            if "SQM" in warehouse_df.columns:
                warehouse_df["SQM"] = warehouse_df["SQM"].apply(
                    lambda x: float(x) if pd.notna(x) else 0
                )
                print(f"  ✅ 창고 임대료 집계: {len(warehouse_df)}건 (SQM 포함)")

        # D. Operation Month(월) 매칭
        if "Operation Month" in df.columns and "ETA" in df.columns:
            # INVOICE 데이터: invoice_month
            # WAREHOUSE 데이터: warehouse_month (ETA)
            df["INVOICE_MONTH"] = pd.to_datetime(
                df["Operation Month"], errors="coerce"
            ).dt.strftime("%Y-%m")
            df["WAREHOUSE_MONTH"] = pd.to_datetime(df["ETA"], errors="coerce").dt.strftime("%Y-%m")

            original_count = len(df)
            df = df[df["INVOICE_MONTH"] == df["WAREHOUSE_MONTH"]]
            filtered_count = len(df)
            print(
                f"  ✅ 월 매칭: {original_count} → {filtered_count} (필터링: {original_count - filtered_count}건)"
            )

        # E. Handling IN/OUT 필드 집계
        handling_fields = ["Handling In freight ton", "Handling out Freight Ton"]
        for field in handling_fields:
            if field in df.columns:
                df[field] = df[field].apply(lambda x: float(x) if pd.notna(x) else 0)
                print(f"  ✅ {field} 처리 완료")

        return df

    def dataframe_to_rdf(self, df: pd.DataFrame, output_path: str = "rdf_output/output.ttl") -> str:
        """
        DataFrame을 RDF로 변환 (mapping_rules 기반 + 🆕 NEW: HVDC 필터 적용)

        Args:
            df: 변환할 DataFrame
            output_path: 출력 파일 경로

        Returns:
            str: 생성된 RDF 파일 경로
        """
        print(f"🔗 DataFrame을 RDF로 변환 중: {output_path}")

        # 🆕 NEW: HVDC 필터 적용
        df = self.apply_hvdc_filters_to_rdf(df)

        # 출력 디렉토리 생성
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # RDF 그래프 생성
        g = Graph()

        # 네임스페이스 바인딩
        for prefix, ns in self.ns.items():
            g.bind(prefix, ns)

        # 각 행을 RDF 트리플로 변환
        for idx, row in df.iterrows():
            # TransportEvent URI 생성
            event_uri = self.ns["ex"][f"TransportEvent_{idx+1:05d}"]
            g.add((event_uri, RDF.type, self.ns["ex"].TransportEvent))

            # 각 컬럼을 RDF 프로퍼티로 변환
            for col, val in row.items():
                if pd.isna(val) or col not in self.field_map:
                    continue

                prop = self.ns["ex"][self.field_map[col]]

                # 🆕 NEW: property_mappings에서 데이터 타입 확인
                datatype = self.property_mappings.get(col, {}).get("datatype", XSD.decimal)

                # 데이터 타입에 따른 Literal 생성
                if isinstance(val, (int, float)):
                    lit = Literal(val, datatype=datatype)
                elif isinstance(val, str):
                    # 날짜 문자열인지 확인
                    try:
                        date_val = pd.to_datetime(val)
                        lit = Literal(date_val.date(), datatype=XSD.date)
                    except Exception:
                        lit = Literal(str(val))
                else:
                    lit = Literal(str(val))

                g.add((event_uri, prop, lit))

        # RDF 파일 저장
        g.serialize(destination=output_path, format="turtle")
        print(f"✅ RDF 변환 완료: {output_path}")

        return output_path

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        """Apply mapping rules to a single record"""
        # Placeholder for single record mapping
        return dict(record)

    def validate_rdf_conversion(self, df: pd.DataFrame) -> dict:
        """
        RDF 변환 검증

        Args:
            df: 검증할 DataFrame

        Returns:
            dict: 검증 결과
        """
        validation_result = {
            "total_records": len(df),
            "mappable_fields": 0,
            "unmappable_fields": [],
            "missing_mappings": [],
        }

        # 매핑 가능한 필드 확인
        for col in df.columns:
            if col in self.field_map:
                validation_result["mappable_fields"] += 1
            else:
                validation_result["unmappable_fields"].append(col)

        # mapping_rules에 정의된 필드가 DataFrame에 없는지 확인
        for field in self.field_map.keys():
            if field not in df.columns:
                validation_result["missing_mappings"].append(field)

        return validation_result
