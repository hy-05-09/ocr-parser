from __future__ import annotations
from datetime import datetime, timezone, timedelta
from .schema import ParsedDocument, Fields
from .normalize import normalize_whitespace, pick_first_date, pick_first_time, pick_lat_lon
from .extractors import (
    extract_vehicle_no, extract_partner, extract_issuer, extract_item_name, extract_direction,
    extract_gross_kg, extract_tare_kg, extract_net_kg, extract_id_no, extract_weigh_count
)
from .validate import validate_fields

KST = timezone(timedelta(hours=9))

def parse_text(source_file: str, raw_text: str) -> ParsedDocument:
    text = normalize_whitespace(raw_text)

    date = pick_first_date(text)
    time = pick_first_time(text)
    lat, lon = pick_lat_lon(text)

    fields = Fields(
        date=date,
        time=time,
        vehicle_no=extract_vehicle_no(text),
        partner_name=extract_partner(text),
        issuer_name=extract_issuer(text),
        item_name=extract_item_name(text),
        direction=extract_direction(text),

        gross_kg=extract_gross_kg(text),
        tare_kg=extract_tare_kg(text),
        net_kg=extract_net_kg(text),

        lat=lat,
        lon=lon,

        id_no=extract_id_no(text),
        weigh_count=extract_weigh_count(text),
    )

    validation = validate_fields(fields)

    return ParsedDocument(
        source_file=source_file,
        parsed_at=datetime.now(KST).isoformat(timespec="seconds"),
        fields=fields,
        validation=validation,
        raw_text=raw_text,
    )
