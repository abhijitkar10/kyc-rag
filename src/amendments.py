"""Phase 4: amendment / version index, parsed from the document's own footnotes.

The corpus is a single CONSOLIDATED Master Direction, but every amended clause
carries a footnote naming the circular and date that changed it
("Amended vide circular DOR.AML.REC.46/... dated August 14, 2025"). Parsing
those footnotes gives an amendment history WITHOUT the separate circular PDFs
(which RBI's server bot-blocks). This is the honest 'versioning' story: the
system knows the provenance and date of each change and can answer
"which circular amended X, and when".

Full cross-version diffing (old text vs new text) would need the individual
circular PDFs — deferred; links recorded in READING_GUIDE.md.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

PAGES = Path("data/processed/pages.jsonl")

# "Amended|Inserted|Deleted vide circular <ID> dated <Month DD, YYYY>"
PAT = re.compile(
    r"(Amended|Inserted|Deleted)\s+vide\s+circular\s+"
    r"([A-Za-z0-9.No/\- ]+?)\s+dated\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})"
)


def build_index(pages_path: Path = PAGES) -> dict:
    """circular_id -> {dates, actions, pages}."""
    idx: dict[str, dict] = defaultdict(
        lambda: {"dates": set(), "actions": set(), "pages": set()})
    for line in pages_path.open():
        rec = json.loads(line)
        for action, circ, date in PAT.findall(rec["text"]):
            circ = re.sub(r"\s+", "", circ).rstrip(".")
            e = idx[circ]
            e["dates"].add(date.replace(" ,", ",").strip())
            e["actions"].add(action)
            e["pages"].add(rec["page"])
    return idx


def timeline(idx: dict | None = None) -> list[tuple[str, str, int]]:
    """(date, circular, #pages-touched), newest first by parsed date."""
    import datetime

    idx = idx or build_index()
    rows = []
    for circ, e in idx.items():
        for d in e["dates"]:
            try:
                dt = datetime.datetime.strptime(d, "%B %d, %Y")
            except ValueError:
                dt = datetime.datetime.min
            rows.append((dt, d, circ, len(e["pages"])))
    rows.sort(reverse=True)
    return [(d, circ, n) for _, d, circ, n in rows]


if __name__ == "__main__":
    idx = build_index()
    print(f"{len(idx)} distinct amending circulars found in footnotes\n")
    print("Amendment timeline (newest first):")
    for date, circ, n_pages in timeline(idx):
        print(f"  {date:>20}  {circ:<40} touches {n_pages} page(s)")
