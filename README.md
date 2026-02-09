# OCR Text Parser 

## Overview
OCR 결과 텍스트(계근지/계근표)를 입력으로 받아 주요 필드를 파싱/정규화하여 구조화(JSON)로 출력합니다.  
노이즈(띄어쓰기, 오탈자, 라벨 누락, 숫자 포맷 불규칙, 순서 변경)를 고려하여 정규식 기반 extractor + fallback 전략을 사용합니다.

## Assumptions
- 입력 JSON은 top-level `text` 필드에 OCR 원문 텍스트를 포함합니다.
- 무게 단위는 `kg`로 표기된 값만 추출 대상으로 가정합니다.
- 총중량/차중량/실중량 라벨이 없을 경우, 시간+kg 패턴에서 2~3개의 계량값을 수집해 gross/tare/net을 추정합니다.

## Features
- date/time/차량번호/거래처/발행자/품목/입출고/총중량/차중량/실중량/좌표/ID/계량횟수 추출
- 숫자 정규화(콤마/공백 혼합 포맷 대응)
- 무결성 검증: `net_kg == gross_kg - tare_kg` (경고 리스트로 리포팅)
- CLI 지원: 단일 파일 / 디렉토리 일괄 처리
- 테스트 포함(pytest)

## Environment
- Python: 3.10+ (권장)
- Dependencies: `requirements.txt` 참고
- Main libs: pydantic, pytest


## Install
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

## Run (CLI)
### Single file
```bash
python cli.py --input samples/sample_01.json --out outputs/sample_01.parsed.json
```
### Directory
```bash
python cli.py --input-dir samples --out-dir outputs
```
### Test
```bash
pytest -q
```


## Output Schema
- fields: 파싱 결과
- validation: 무결성 체크 및 warnings

예시 결과 파일: `outputs/sample_01.parsed.json` ~ `outputs/sample_04.parsed.json`


## Design Notes
- pipeline.py: normalize → 핵심 extractor 호출 → validate → 결과 생성

- extractors.py: 라벨 기반 추출 우선, 실패 시 time+kg 패턴 기반 fallback 사용

- normalize.py: 날짜/시간/좌표 파싱 및 숫자 정규화

- validate.py: net/gross/tare 관계 검증 및 필수 필드 누락 경고

## Limitations & Improvements
시간(time) 추출은 현재 문서 내에서 가장 먼저 발견되는 시각 토큰을 우선 사용합니다.  계근지 형태에 따라 총중량/차중량 시각과 발행 시각이 함께 존재할 수 있어, 의도한 “기준 시간(예: 발행 시각)”과 다를 수 있습니다. 개선 방향으로는 라벨(예: 발행/확인/출력) 기반 우선순위 규칙을 추가하거나, 총/차중량 라인의 시각 조합에서 최종 확정 시각을 선택하는 휴리스틱을 적용할 수 있습니다.
