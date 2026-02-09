from __future__ import annotations
import re
from typing import Optional
from .normalize import normalize_kg_number

RE_KG_BLOCK = re.compile(r"(?P<num>[0-9][0-9 ,]*)\s*kg", re.IGNORECASE)
RE_TIME_TOKEN = re.compile(
    r"(\d{1,2}\s*[:：]\s*\d{1,2})|"         # 02:07, 02 : 13
    r"(\d{1,2}\s*시\s*\d{1,2}\s*분)|"   # 11시 33분
    r"(\d{1,2}\s*시)|"                 # 11시
    r"(\d{1,2}\s*분)",                 # 33분
    re.IGNORECASE
)
RE_TIME_HMS = re.compile(r"([01]?\d|2[0-3])\s*[:：]\s*([0-5]\d)(?:\s*[:：]\s*([0-5]\d))?")


def extract_vehicle_no(text: str) -> Optional[str]:
    for pat in [
        r"차량\s*번호\s*[:：][ \t]*([0-9A-Za-z가-힣-]+)", # 차량번호: 80구8713
        r"차량\s*(?:No\.?|NO\.?)[ \t]*[:：]?[ \t]*([0-9A-Za-z가-힣-]+)", # 차량 No 80구8713
        r"차\s*번호\s*[:：][ \t]*([0-9A-Za-z가-힣-]+)", # 차 번호 : 80구8713
    ]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            token = m.group(1).replace(" ","").strip()
            token2 = re.sub(r"[^0-9]+$", "", token)
            return token2 if re.search(r"\d", token2) else None
    return None


def extract_partner(text: str) -> Optional[str]:
    for pat in [
        r"거\s*래\s*처\s*[:：][ \t]*([^\n]+)",
        r"상\s*호\s*[:：][ \t]*([^\n]+)",
    ]:
        m = re.search(pat, text)
        if m:
            val = m.group(1).strip()
            if val:
                return val
    m = re.search(r"([^\n]+)\s*귀하", text)
    if m:
        val = m.group(1).strip()
        return val or None
    return None

def extract_issuer(text: str) -> Optional[str]:
    m = re.search(r"\n([^\n]*(?:\(주\)|주식회사)[^\n]*)\n", text)
    return (m.group(1).strip() or None) if m else None 

def extract_item_name(text: str) -> Optional[str]:
    m = re.search(r"품\s*명\s*[:：][ \t]*([^\n]+)", text)
    if m:
        val = m.group(1).strip()
        return val or None
    
    m = re.search(r"품\s*명[ \t]*([^\n]+)\s+구\s*분", text)
    if m:
        val = m.group(1).strip()
        return val or None
    
    return None
    
def extract_direction(text: str) -> str:
    m = re.search(r"구\s*분\s*[:：][ \t]*([^\n]+)", text)
    if m:
        v = m.group(1).strip()
        if "입" in v:
            return "IN"
        if "출" in v:
            return "OUT"
        
    if re.search(r"\b입\s*고\b", text):
        return "IN"
    if re.search(r"\b출\s*고\b", text):
        return "OUT"
    if re.search(r"입\s*고", text):
        return "IN"
    if re.search(r"출\s*고", text):
        return "OUT"
    return "UNKNOWN"

def _extract_two_weighings_timekg(text: str) -> list[int]:
    """
    라벨 없이 'HH:MM(:SS) ... N kg' 형태로 찍힌 계량값들을 순서대로 수집
    """
    vals: list[int] = []
    for line in text.splitlines():
        if not RE_TIME_HMS.search(line):
            continue

        line_wo_time = RE_TIME_HMS.sub(" ", line)

        mkg = RE_KG_BLOCK.search(line_wo_time)
        if not mkg:
            continue

        num_clean = re.sub(r"[^\d]", "", mkg.group("num"))
        v = normalize_kg_number(num_clean)
        if v is not None:
            vals.append(v)
    return vals

def _fallback_gross_tare_by_timekg(text: str) -> tuple[Optional[int], Optional[int], Optional[int]]:
    vals = _extract_two_weighings_timekg(text)

    if len(vals) == 3:
        a, b, c = vals[0], vals[1], vals[2]
        gross = max(a, b, c)
        net = min(a, b, c)
        tare = a + b + c - gross - net
        return gross, tare, net
    
    if len(vals) == 2:
        a, b = vals[0], vals[1]
        gross = max(a, b)
        tare = min(a, b)
        return gross, tare, None

    return None, None, None

def _extract_weight_by_label(text: str, label_regex: str) -> Optional[int]:
    m = re.search(label_regex, text)
    if not m :
        return None
    tail = text[m.end():m.end()+80]

    tail = RE_TIME_TOKEN.sub(" ", tail)

    m2 = RE_KG_BLOCK.search(tail)
    if not m2:
        return None
    
    num_raw = m2.group("num")
    num_clean = re.sub(r"[^\d]", "", num_raw) 

    if not re.search(r"\d", num_clean):
        return None

    return normalize_kg_number(num_clean)

def extract_gross_kg(text: str) -> Optional[int]:
    v = _extract_weight_by_label(text, r"총\s*중\s*량\s*[:：]?\s*")
    if v is not None:
        return v
    gross, _, _ = _fallback_gross_tare_by_timekg(text)
    return gross

def extract_tare_kg(text: str) -> Optional[int]:
    v = _extract_weight_by_label(text, r"(?:차\s*중\s*량|공\s*차\s*중\s*량)\s*[:：]?\s*")
    if v is not None:
        return v
    _, tare, _ = _fallback_gross_tare_by_timekg(text)
    return tare

def extract_net_kg(text: str) -> Optional[int]:
    v = _extract_weight_by_label(text, r"실\s*중\s*량[ \t]*[:：]?[ \t]*")
    if v is not None:
        return v
    _, _, net = _fallback_gross_tare_by_timekg(text)
    return net

def extract_id_no(text: str) -> Optional[str]:
    m = re.search(r"I\s*D\s*-\s*N\s*O\s*[:：][ \t]*([0-9A-Za-z-]+)", text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def extract_weigh_count(text: str) -> Optional[str]:
    m = re.search(r"계\s*량\s*횟\s*수\s*[:：]?[ \t]*([0-9]{3,})", text)
    return m.group(1).strip() if m else None
