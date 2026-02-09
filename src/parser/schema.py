from __future__ import annotations
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

Direction = Literal["IN", "OUT", "UNKNOWN"] # 입고/출고/알수없음

# 추출 결과 검증 후 이상 징후 경고로 모아두는 품질 리포트
class ValidationResult(BaseModel):
    net_equals_gross_minus_tare: Optional[bool] = None # 실중량 = 총중량 - 차중량
    warnings: List[str] = Field(default_factory=list) # 필수 필드 누락, 무결성 불일치, 형식 이상 등

# 핵심 데이터 객체
class Fields(BaseModel):
    date: Optional[str] = None # YYYY-MM-DD
    time: Optional[str] = None # HH:MM:SS

    vehicle_no: Optional[str] = None # 차량번호
    partner_name: Optional[str] = None # 거래처
    issuer_name: Optional[str] = None # 발행자
    item_name: Optional[str] = None # 품목
    direction: Direction = "UNKNOWN" # 입고/출고/알수없음

    gross_kg: Optional[int] = None # 총중량
    tare_kg: Optional[int] = None # 차중량
    net_kg: Optional[int] = None # 실중량

    lat: Optional[float] = None # 위도
    lon: Optional[float] = None # 경도

    id_no: Optional[str] = None # 식별번호
    weigh_count: Optional[str] = None # 계량횟수

# 원문 + 추출값 + 경고 + 메타정보
class ParsedDocument(BaseModel):
    schema_version: str = "1.0" # 스키마 version
    source_file: str 
    parsed_at: str # 결과 산출 시각 
    fields: Fields
    validation: ValidationResult
    raw_text: str
