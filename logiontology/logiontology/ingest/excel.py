#!/usr/bin/env python3
"""
HVDC Excel to RDF Converter
Excel 파일을 RDF/TTL 형식으로 변환하는 스크립트
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
from rdflib.plugins.sparql import prepareQuery
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Mapping
import warnings
warnings.filterwarnings('ignore')

from .normalize import normalize_columns

# 네임스페이스 정의
EX = Namespace("http://samsung.com/project-logistics#")
ns = {
    "ex": "http://samsung.com/project-logistics#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
}

# 매핑 규칙 정의
FIELD_MAPPINGS = {
    "Case No.": "hasCase",
    "Date": "hasDate",
    "Location": "hasLocation",
    "Qty": "hasQuantity",
    "Amount": "hasAmount",
    "Handling Fee": "hasHandlingFee",
    "HVDC CODE": "hasHvdcCode",
    "HVDC CODE 2": "hasHvdcCode2",
    "HVDC CODE 3": "hasHvdcCode3",
    "HVDC CODE 4": "hasHvdcCode4",
    "Operation Month": "hasOperationMonth",
    "ETA": "hasETA",
    "SQM": "hasSQM",
    "Handling In freight ton": "hasHandlingIn",
    "Handling out Freight Ton": "hasHandlingOut",
    "CBM": "hasCBM",
    "Pkg": "hasPackage",
    "G.W(KG)": "hasGrossWeight",
    "N.W(kgs)": "hasNetWeight",
    "L(CM)": "hasLength",
    "W(CM)": "hasWidth",
    "H(CM)": "hasHeight"
}

def load_excel(path: str, sheet: str | int | None = 0, rename_map: Mapping[str, str] | None = None) -> pd.DataFrame:
    """Load Excel file and normalize columns"""
    df = pd.read_excel(path, sheet_name=sheet)
    return normalize_columns(df, rename_map=rename_map)

def convert_excel_to_rdf(excel_path: str, output_path: str = None) -> str:
    """
    Excel 파일을 RDF로 변환
    
    Args:
        excel_path: Excel 파일 경로
        output_path: 출력 RDF 파일 경로 (기본값: 자동 생성)
        
    Returns:
        str: 생성된 RDF 파일 경로
    """
    print(f"📊 Excel 파일 로드 중: {excel_path}")
    
    # Excel 파일 로드
    try:
        df = pd.read_excel(excel_path)
        print(f"✅ 로드 완료: {len(df)}행, {len(df.columns)}열")
    except Exception as e:
        print(f"❌ Excel 로드 실패: {e}")
        return None
    
    # 출력 경로 설정
    if output_path is None:
        excel_name = Path(excel_path).stem
        output_path = f"rdf_output/{excel_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ttl"
    
    # 출력 디렉토리 생성
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # RDF 그래프 생성
    g = Graph()
    
    # 네임스페이스 바인딩
    for prefix, uri in ns.items():
        g.bind(prefix, Namespace(uri))
    
    # 각 행을 RDF 트리플로 변환
    for idx, row in df.iterrows():
        # TransportEvent URI 생성
        event_uri = EX[f"TransportEvent_{idx+1:05d}"]
        g.add((event_uri, RDF.type, EX.TransportEvent))
        
        # 각 컬럼을 RDF 프로퍼티로 변환
        for col, val in row.items():
            if pd.isna(val) or col not in FIELD_MAPPINGS:
                continue
                
            prop = EX[FIELD_MAPPINGS[col]]
            
            # 데이터 타입에 따른 Literal 생성
            if isinstance(val, (int, float)):
                if col in ["Qty", "Pkg"]:
                    lit = Literal(int(val), datatype=XSD.integer)
                else:
                    lit = Literal(float(val), datatype=XSD.decimal)
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

def batch_convert_excel_to_rdf(input_dir: str, output_dir: str = "rdf_output") -> list[str]:
    """
    디렉토리 내 모든 Excel 파일을 RDF로 변환
    
    Args:
        input_dir: Excel 파일들이 있는 디렉토리
        output_dir: 출력 디렉토리
        
    Returns:
        list[str]: 생성된 RDF 파일 경로 목록
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    excel_files = list(input_path.glob("*.xlsx")) + list(input_path.glob("*.xls"))
    converted_files = []
    
    print(f"📁 Excel 파일 {len(excel_files)}개 발견")
    
    for excel_file in excel_files:
        try:
            output_file = output_path / f"{excel_file.stem}.ttl"
            result = convert_excel_to_rdf(str(excel_file), str(output_file))
            if result:
                converted_files.append(result)
        except Exception as e:
            print(f"❌ {excel_file.name} 변환 실패: {e}")
    
    print(f"✅ 배치 변환 완료: {len(converted_files)}개 파일")
    return converted_files

def validate_excel_data(df: pd.DataFrame) -> dict:
    """
    Excel 데이터 검증
    
    Args:
        df: 검증할 DataFrame
        
    Returns:
        dict: 검증 결과
    """
    validation_result = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
        "data_types": df.dtypes.to_dict(),
        "required_columns": [],
        "missing_required": []
    }
    
    # 필수 컬럼 확인
    required_cols = ["Case No.", "Date", "Location", "Qty"]
    validation_result["required_columns"] = required_cols
    
    for col in required_cols:
        if col not in df.columns:
            validation_result["missing_required"].append(col)
    
    return validation_result

def generate_excel_summary(df: pd.DataFrame) -> dict:
    """
    Excel 데이터 요약 생성
    
    Args:
        df: 요약할 DataFrame
        
    Returns:
        dict: 요약 정보
    """
    summary = {
        "file_info": {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "memory_usage": df.memory_usage(deep=True).sum(),
        },
        "data_quality": {
            "missing_values": df.isnull().sum().sum(),
            "duplicate_rows": df.duplicated().sum(),
            "unique_values": df.nunique().to_dict(),
        },
        "numeric_summary": {},
        "categorical_summary": {}
    }
    
    # 숫자형 컬럼 요약
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        summary["numeric_summary"] = df[numeric_cols].describe().to_dict()
    
    # 범주형 컬럼 요약
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        summary["categorical_summary"][col] = {
            "unique_count": df[col].nunique(),
            "most_common": df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None,
            "most_common_count": df[col].value_counts().iloc[0] if len(df[col].value_counts()) > 0 else 0
        }
    
    return summary
