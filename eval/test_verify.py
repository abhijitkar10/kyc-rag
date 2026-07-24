"""Deterministic unit tests for the Phase 4 citation guardrail (no LLM needed).

    python eval/test_verify.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import verify  # noqa: E402


def test_grounded():
    v, u = verify.verify("OVDs include passport [KYC Master Direction, p.8].", [8, 16])
    assert v == "grounded" and u == set()


def test_ungrounded_single():
    v, u = verify.verify("Balance cap is 1 lakh [KYC Master Direction, p.26].", [27, 32])
    assert v == "ungrounded" and u == {26}


def test_ungrounded_mixed():
    # one good cite, one invented — must be caught as ungrounded
    txt = "A [KYC Master Direction, p.16]. B [KYC Master Direction, p.99]."
    v, u = verify.verify(txt, [16, 17])
    assert v == "ungrounded" and u == {99}


def test_refusal():
    v, u = verify.verify("Not found in the provided documents.", [])
    assert v == "refusal"


def test_uncited():
    v, u = verify.verify("Some confident claim with no citation.", [16])
    assert v == "uncited"


def test_enforce_annotates_ungrounded():
    out, v = verify.enforce("X [KYC Master Direction, p.99].", [16])
    assert v == "ungrounded" and "UNVERIFIED" in out


def test_enforce_passes_grounded():
    out, v = verify.enforce("X [KYC Master Direction, p.16].", [16])
    assert v == "grounded" and "⚠" not in out


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"\n{len(tests)}/{len(tests)} tests passed")
