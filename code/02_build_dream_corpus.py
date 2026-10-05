"""Build a provenance-preserving DreamBank blind-series corpus from saved HTML."""
from __future__ import annotations
import csv, html, re
from pathlib import Path

RAW = Path("data/dreambank/raw/blind_series_show_complete_2026-10-05.html")
OUT = Path("data/dreambank/processed/dream_reports.csv")

label_re = re.compile(r'<input[^>]+value="(?P<id>(?:blind-f|blind-m):[^"]+)"[^>]*>\s*<label[^>]*>(?P<label>.*?)</label><br/><br[^>]*>(?P<text>.*?)(?=<hr)', re.S)
code_re = re.compile(r'#(?P<code>\d+)-')

# Transcribed from the public DreamBank series metadata page, whose key defines
# C=congenital and A=adventitious. Exact onset age is not available.
META = {
 "101": ("ACQUIRED_UNSPECIFIED", "19", "A/T"), "102": ("CONGENITAL", "32", "C/T"),
 "103": ("ACQUIRED_UNSPECIFIED", "10", "A/P"), "104": ("CONGENITAL", "45", "C/T"),
 "105": ("ACQUIRED_UNSPECIFIED", "43", "A/P"), "109": ("ACQUIRED_UNSPECIFIED", "20", "A/T"),
 "111": ("CONGENITAL", "50", "C/L"), "113": ("ACQUIRED_UNSPECIFIED", "17", "A/T"),
 "114": ("CONGENITAL", "52", "C/T"), "115": ("ACQUIRED_UNSPECIFIED", "60", "A/T"),
 "117": ("CONGENITAL", "44", "C/T"), "120": ("ACQUIRED_UNSPECIFIED", "47", "A/T"),
 "122": ("ACQUIRED_UNSPECIFIED", "46", "A/T"), "124": ("CONGENITAL", "46", "C/T"), "125": ("CONGENITAL", "44", "C/T"),
}

def clean(value: str) -> str:
    value = re.sub(r'<[^>]+>', ' ', value)
    return re.sub(r'\s+', ' ', html.unescape(value)).strip()

def main() -> None:
    raw = RAW.read_text(encoding="utf-8")
    rows = []
    for m in label_re.finditer(raw):
        did, label, text = m.group("id"), clean(m.group("label")), clean(m.group("text"))
        code = code_re.search(label).group("code")
        group, years, degree = META[code]
        rows.append({
            "dream_id": f"DREAMBANK_{did}", "dataset": "DreamBank", "series": did.split(":")[0],
            "dreamer_id_pseudonymous": f"DB_{code}", "blindness_group": group,
            "blindness_onset_age": "NOT_REPORTED", "blindness_duration_years": years,
            "blindness_metadata": degree, "dream_text": text, "collection_method": "archival_free_recall",
            "free_recall_or_prompted": "free_recall", "date_if_available": "NOT_REPORTED",
            "source_url": "https://dreambank.net/", "license": "CC-BY-NC-SA-4.0",
            "metadata_confidence": "HIGH_FOR_CONGENITAL_VS_ADVENTITIOUS; NO_EXACT_ONSET",
        })
    assert len(rows) == 381, f"expected 381 blind F/M reports, got {len(rows)}"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)

if __name__ == "__main__":
    main()
