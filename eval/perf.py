"""Performance numbers for the README (retrieval part is LLM-free / quota-safe).

    python eval/perf.py                 # retrieval latency p50/p95 over all 50 questions
    python eval/perf.py --retriever rerank

Generation latency + cost are documented from a small sample (needs LLM quota);
retrieval latency here is measured live and needs no key.
"""

import argparse
import csv
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from retrievers import get_retriever  # noqa: E402

QUESTIONS = Path("eval/questions.csv")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--retriever", default="hybrid")
    ap.add_argument("--top-k", type=int, default=5)
    args = ap.parse_args()

    questions = [r["question"] for r in csv.DictReader(QUESTIONS.open())]
    search = get_retriever(args.retriever)

    search(questions[0], top_k=args.top_k)  # warm up (model load, caches)

    times = []
    for q in questions:
        t0 = time.perf_counter()
        search(q, top_k=args.top_k)
        times.append((time.perf_counter() - t0) * 1000)  # ms

    times.sort()
    p50 = statistics.median(times)
    p95 = times[int(len(times) * 0.95)]
    print(f"retrieval [{args.retriever}] latency over {len(times)} queries:")
    print(f"  p50 = {p50:6.1f} ms")
    print(f"  p95 = {p95:6.1f} ms")
    print(f"  max = {max(times):6.1f} ms")


if __name__ == "__main__":
    main()
