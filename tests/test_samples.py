from pathlib import Path
import json
from parser.pipeline import parse_text

EXPECTED = {
    "sample_01.json": {
        "date": "2026-02-02",
        "vehicle_no": "8713",
        "direction": "UNKNOWN",
        "gross_kg": 12480,
        "tare_kg": 7470,
        "net_kg": 5010,
    },
    "sample_02.json": {
        "date": "2026-02-02",
        "vehicle_no": "80구8713",
        "direction": "IN",
        "gross_kg": 13460,
        "tare_kg": 7560,
        "net_kg": 5900,
    },
    "sample_03.json": {
        "date": "2026-02-01",
        "vehicle_no": "5405",
        "direction": "IN",
        "gross_kg": 14080,
        "tare_kg": 13950,
        "net_kg": 130,
    },
    "sample_04.json": {
        "date": "2025-12-01",
        "vehicle_no": "0580",
        "direction": "IN",
        "gross_kg": 14230,
        "tare_kg": 12910,
        "net_kg": 1320,
    },
}

SAMPLES = list(EXPECTED.keys())


def _load_raw_text(base: Path, filename: str) -> str:
    data = json.loads((base / filename).read_text(encoding="utf-8"))
    return data["text"]


def test_parse_all_samples_have_expected_weights_and_integrity():
    base = Path("samples")
    for fname in SAMPLES:
        raw_text = _load_raw_text(base, fname)
        doc = parse_text(fname, raw_text)

        exp = EXPECTED[fname]

        # 필수 필드(기본)
        assert doc.fields.date == exp["date"]
        assert doc.fields.vehicle_no == exp["vehicle_no"]
        assert doc.fields.direction == exp["direction"]

        # 무게 값
        assert doc.fields.gross_kg == exp["gross_kg"]
        assert doc.fields.tare_kg == exp["tare_kg"]
        assert doc.fields.net_kg == exp["net_kg"]

        # 무결성 검증(실중량 = 총 - 차)
        assert doc.validation.net_equals_gross_minus_tare is True
        assert (doc.fields.gross_kg - doc.fields.tare_kg) == doc.fields.net_kg

        # 정상 케이스일 시 경고 리스트가 빈칸
        assert doc.validation.warnings == []
