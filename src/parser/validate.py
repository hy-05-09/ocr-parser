from __future__ import annotations
from .schema import ValidationResult, Fields

def validate_fields(fields: Fields) -> ValidationResult:
    v = ValidationResult()

    # 실중량 = 총중량 - 차중량 검증
    if fields.gross_kg is not None and fields.tare_kg is not None and fields.net_kg is not None:
        v.net_equals_gross_minus_tare = (fields.gross_kg - fields.tare_kg) == fields.net_kg
        if not v.net_equals_gross_minus_tare:
            v.warnings.append(
                f"net_kg mismatch: gross({fields.gross_kg}) - tare({fields.tare_kg}) != net({fields.net_kg})"
            )

    # 기타 검증
    if fields.date is None:
        v.warnings.append("date not found")
    if fields.vehicle_no is None:
        v.warnings.append("vehicle_no not found")
    if fields.gross_kg is None:
        v.warnings.append("gross_kg not found")
    if fields.net_kg is None:
        v.warnings.append("net_kg not found")
    
    return v














