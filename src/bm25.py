"""BM25 keyword search, implemented from scratch (no rank_bm25 / no library).

This is the project's designated "built it myself" component. BM25 ranks a
chunk for a query by summing, over the query's words, a score that rewards:
  - words that appear more often in the chunk        (term frequency, saturating)
  - words that are rare across the whole corpus       (inverse document frequency)
  - and gently penalises very long chunks             (length normalisation)

Formula (Robertson/Sparck-Jones "Okapi BM25"):
  score(D,Q) = sum_t IDF(t) * ( f(t,D)*(k1+1) ) / ( f(t,D) + k1*(1 - b + b*|D|/avgdl) )
  IDF(t)     = ln( (N - n(t) + 0.5) / (n(t) + 0.5) + 1 )
where f(t,D)=freq of term t in chunk D, n(t)=#chunks containing t, N=#chunks,
|D|=chunk length in tokens, avgdl=average chunk length. k1 controls how fast
term-frequency saturates; b controls length normalisation.
"""

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

CHUNKS = Path("data/processed/chunks.jsonl")
K1 = 1.5   # term-frequency saturation
B = 0.75   # length-normalisation strength

_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Lowercase, keep alphanumerics. Digits matter here ('16', '50000')."""
    return _TOKEN.findall(text.lower())


class BM25Index:
    def __init__(self, chunks_path: Path = CHUNKS):
        self.chunks = [json.loads(line) for line in chunks_path.open()]
        tokenized = [tokenize(c["text"]) for c in self.chunks]
        self.doc_len = [len(t) for t in tokenized]
        self.avgdl = sum(self.doc_len) / len(self.doc_len)

        # Inverted index: term -> [(chunk_id, term_freq), ...]
        self.postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        df: dict[str, int] = defaultdict(int)
        for i, toks in enumerate(tokenized):
            for term, freq in Counter(toks).items():
                self.postings[term].append((i, freq))
                df[term] += 1

        n_docs = len(self.chunks)
        self.idf = {
            term: math.log((n_docs - n + 0.5) / (n + 0.5) + 1)
            for term, n in df.items()
        }

    def search(self, query: str, top_k: int = 5) -> list[tuple[float, dict]]:
        scores: dict[int, float] = defaultdict(float)
        for term in tokenize(query):
            if term not in self.postings:
                continue
            idf = self.idf[term]
            for doc_id, freq in self.postings[term]:
                dl = self.doc_len[doc_id]
                denom = freq + K1 * (1 - B + B * dl / self.avgdl)
                scores[doc_id] += idf * (freq * (K1 + 1)) / denom
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
        return [(score, self.chunks[i]) for i, score in ranked]


if __name__ == "__main__":
    import sys

    idx = BM25Index()
    for s, c in idx.search(" ".join(sys.argv[1:]) or "video call account opening"):
        print(f"[{s:.3f}] p.{c['page']}  {c['text'][:90]}...")
