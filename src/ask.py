"""Step 6: the CLI — the whole pipeline behind one command.

    python src/ask.py "Can I open a bank account over a video call?"

Add --show-chunks to also print what the retriever found (useful for debugging
why an answer went wrong: is it the librarian or the writer?).
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from retrievers import get_retriever  # noqa: E402

search = get_retriever(os.environ.get("RETRIEVER", "rerank"))


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--show-chunks"]
    show = "--show-chunks" in sys.argv
    question = " ".join(args)
    if not question:
        print('usage: python src/ask.py "your question" [--show-chunks]')
        return

    if show:
        print("--- retrieved ---")
        for score, chunk in search(question):
            print(f"[{score:.3f}] p.{chunk['page']}  {chunk['text'][:90]}...")
        print("--- answer ---")

    from answer import answer  # deferred: needs ANTHROPIC_API_KEY

    print(answer(question))


if __name__ == "__main__":
    main()
