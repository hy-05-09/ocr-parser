from __future__ import annotations
import argparse, json, os
from pathlib import Path
from parser.pipeline import parse_text

def load_text_from_json(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, dict) and "text" in data:
        return data["text"]
    raise ValueError("Input JSON does not contain top-level 'text' field")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=str, help="input json file (single)")
    ap.add_argument("--input-dir", type=str, help="input directory containing json files")
    ap.add_argument("--out", type=str, help="output file path (single mode)")
    ap.add_argument("--out-dir", type=str, help="output directory (dir mode)")
    args = ap.parse_args()

    if args.input:
        in_path = Path(args.input)
        out_path = Path(args.out) if args.out else Path("outputs") / f"{in_path.stem}.parsed.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        text = load_text_from_json(in_path)
        doc = parse_text(in_path.name, text)
        out_path.write_text(doc.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"OK: {in_path} -> {out_path}")
        return

    if args.input_dir:
        in_dir = Path(args.input_dir)
        out_dir = Path(args.out_dir or "outputs")
        out_dir.mkdir(parents=True, exist_ok=True)
        for p in sorted(in_dir.glob("*.json")):
            try:
                text = load_text_from_json(p)
                doc = parse_text(p.name, text)
                out_path = out_dir / f"{p.stem}.parsed.json"
                out_path.write_text(doc.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"OK: {p.name} -> {out_path.name}")
            except Exception as e:
                print(f"FAIL: {p.name}: {e}")
        return

    ap.error("Provide --input or --input-dir")

if __name__ == "__main__":
    main()
