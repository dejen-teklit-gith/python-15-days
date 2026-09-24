"""Day 14 · Part B — A mini RAG (Retrieval-Augmented Generation) support bot, from scratch.

RAG = search your own documents for relevant text, then give ONLY that text to an LLM
so it answers from facts instead of guessing.

python rag.py                         → demo questions (retrieval only, no API key needed)
python rag.py "How long is the warranty on batteries?"
ANTHROPIC_API_KEY=sk-... python rag.py "..."   → also generates an answer with Claude
"""
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
STOPWORDS = set("""a an the and or of to in on for is are be by with it its as at this that
from your you we our can do does not no if how what when which who will than then there""".split())


# ── 1. Chunk: split documents into small, self-contained passages ───────────
def load_chunks(folder: Path) -> list[dict]:
    chunks = []
    for path in sorted(folder.glob("*.md")):
        title = path.read_text().splitlines()[0].lstrip("# ").strip()
        for line in path.read_text().splitlines()[1:]:
            if line.strip():
                chunks.append({"source": path.name, "title": title, "text": line.strip()})
    return chunks


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w.rstrip("s") if len(w) > 3 else w for w in words if w not in STOPWORDS]  # tiny stemming


# ── 2. Embed: turn text into vectors so "similar meaning" = "nearby vectors" ─
class TfidfEmbedder:
    """Words that are frequent in a chunk but rare overall get the highest weight.
    Production systems use neural embeddings (same idea, captures synonyms too)."""

    def fit(self, texts: list[str]):
        docs = [set(tokenize(t)) for t in texts]
        self.vocab = {w: i for i, w in enumerate(sorted(set().union(*docs)))}
        df = Counter(w for d in docs for w in d)
        self.idf = np.array([math.log((1 + len(docs)) / (1 + df[w])) + 1 for w in self.vocab])
        return self

    def embed(self, text: str) -> np.ndarray:
        vec = np.zeros(len(self.vocab))
        for word, count in Counter(tokenize(text)).items():
            if word in self.vocab:
                vec[self.vocab[word]] = count
        vec *= self.idf
        norm = np.linalg.norm(vec)
        return vec / norm if norm else vec           # unit length → dot product = cosine


# ── 3. Retrieve: nearest chunks to the question ─────────────────────────────
class Retriever:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.embedder = TfidfEmbedder().fit([c["text"] for c in chunks])
        self.matrix = np.vstack([self.embedder.embed(c["text"]) for c in chunks])   # the "vector DB"

    def search(self, question: str, k: int = 3, min_score: float = 0.1) -> list[tuple[float, dict]]:
        scores = self.matrix @ self.embedder.embed(question)      # cosine similarity with every chunk
        best = np.argsort(scores)[::-1][:k]
        return [(float(scores[i]), self.chunks[i]) for i in best if scores[i] >= min_score]


# ── 4. Augment + generate: build a grounded prompt, ask the LLM ─────────────
def build_prompt(question: str, hits: list[tuple[float, dict]]) -> str:
    context = "\n".join(f"[{i + 1}] ({c['source']}) {c['text']}" for i, (_, c) in enumerate(hits))
    return (
        "You are a customer-support assistant. Answer using ONLY the context below. "
        "Cite sources like [1]. If the context doesn't contain the answer, say you don't know "
        "and suggest contacting support.\n\n"
        f"Context:\n{context or '(no relevant documents found)'}\n\nQuestion: {question}"
    )


def generate(prompt: str) -> str | None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None
    import anthropic                                   # pip install anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-5"),
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def answer(retriever: Retriever, question: str) -> None:
    hits = retriever.search(question)
    print(f"\n❓ {question}")
    if not hits:
        print("   (nothing relevant found → a good bot says 'I don't know' instead of inventing)")
    for score, c in hits:
        print(f"   {score:.2f}  [{c['source']}] {c['text']}")
    reply = generate(build_prompt(question, hits))
    if reply:
        print(f"🤖 {reply}")


if __name__ == "__main__":
    retriever = Retriever(load_chunks(HERE / "docs"))
    print(f"Indexed {len(retriever.chunks)} chunks, vocabulary of {len(retriever.embedder.vocab)} words")

    questions = sys.argv[1:] or [
        "Can I return a helmet I already wore?",
        "How long does delivery of a complete bike take?",
        "What warranty do e-bike batteries have?",
        "How should I store my battery over the winter?",
        "Do you sell skateboards?",
    ]
    for q in questions:
        answer(retriever, q)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n── Prompt that WOULD be sent to the LLM for the first question ──")
        print(build_prompt(questions[0], retriever.search(questions[0])))
        print("\nSet ANTHROPIC_API_KEY to generate real answers.")
