from __future__ import annotations
from typing import Optional, Tuple
import re


RE_DATE = re.compile(r"(20\d{2})[-/.](\d{2})[-/.](\d{2})")
RE_TIME_HMS = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)(?::([0-5]\d))?\b")
RE_TIME_KO = re.compile(r"(\d{1,2})\s*시\s*(\d{1,2})\s*분")
RE_LATLON = re.compile(r"(-?\d{1,3\.\d+})\s*,\s*(-?\d{1,3}\.\d+)")

def normalize_whitespace(s: str) -> str:
    """
    - 줄바꿈 통일
    - 연속 공백/탭 줄이기
    - 양 끝 공백 제거
    """
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]", "", s)
    return s.strip()

def normalize_kg_number(token: str) -> Optional[int]:
    """
    - "14,080" -> 14080
    - "13 460" -> 13460
    """
    digits = re.findall(r"\d+", token or "")
    if not digits:
        return None
    return int("".join(digits))

def pick_first_date(text: str) -> Optional[str]:
    m = RE_DATE.search(text)
    if not m:
        return None
    y, mm, dd = m.group(1), m.group(2), m.group(3)
    return f"{y}-{mm}-{dd}"
    

def pick_first_time(text: str) -> Optional[str]:
    """
    우선순위:
        1) HH:MM(:SS)
        2) HH시 MM분
        3) 날짜 뒤에 오는 HHMM, e.g., '2026-02-02 0016'
    """
    m = RE_TIME_HMS.search(text)
    if m:
        hh, mm, ss = m.group(1), m.group(2), m.group(3) or "00"
        return f"{int(hh):02d}:{int(mm):02d}:{int(ss):02d}"
    
    m = RE_TIME_KO.search(text)
    if m:
        hh, mm = int(m.group(1)), int(m.group(2))
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            return f"{hh:02d}:{mm:02d}:00"
        
    m_date = RE_DATE.search(text)
    if m_date:
        after = text[m_date.end() : m_date.end() + 20]
        m4 = re.search(r"\b(\d{4})\b", after)
        if m4:
            hhmm = m4.group(1)
            hh, mm = int(hhmm[:2]), int(hhmm[2:])
            if 0 <= hh <= 23 and 0 <= mm <= 59:
                return f"{hh:02d}:{mm:02d}:00"
    return None


def pick_lat_lon(text: str) -> Tuple[Optional[float], Optional[float]]:
    m = RE_LATLON.search(text)
    if not m:
        return None, None
    return float(m.group(1)), float(m.group(2))