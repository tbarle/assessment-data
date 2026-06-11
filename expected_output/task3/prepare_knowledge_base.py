#!/usr/bin/env python3
"""
Task 3: Prepare Knowledge Base for RAG.

Reads cleaned data from task2/cleaned_data/, builds text chunks per source
(FAQ, projects, interactions), calls OpenAI text-embedding-3-small, and
writes knowledge_base.jsonl.

Usage:
    OPENAI_API_KEY=sk-... python prepare_knowledge_base.py
"""
import json
import os
import time
from pathlib import Path

from openai import OpenAI

# ─── Paths ───────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent.parent
CLEANED_DIR = ROOT / "expected_output" / "task2" / "cleaned_data"
OUT_DIR = ROOT / "expected_output" / "task3"
OUT_FILE = OUT_DIR / "knowledge_base.jsonl"

# ─── Config ──────────────────────────────────────────────────────────────────

EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM = 1536
BATCH_SIZE = 100  # max inputs per OpenAI embeddings request
EMBED_TOKEN_LIMIT = 8192  # hard limit di text-embedding-3-small


# ─── Loaders ─────────────────────────────────────────────────────────────────

def load_json(name: str) -> list[dict]:
    with open(CLEANED_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


# ─── Chunk builders ──────────────────────────────────────────────────────────

def build_faq_chunks(faqs: list[dict], categories: dict[int, str]) -> list[dict]:
    """One chunk per Q+A pair — already a self-contained semantic unit."""
    chunks = []
    for faq in faqs:
        cat_name = categories.get(faq["category_id"], "Generale")
        content = f"Q: {faq['question']}\nA: {faq['answer']}"
        chunks.append({
            "id": f"faq-{faq['id']:03d}",
            "content": content,
            "metadata": {
                "source": "faq",
                "category": cat_name,
                "category_id": faq["category_id"],
                "language": "it",
                "created_at": faq["created_at"],
            },
        })
    return chunks


def build_project_chunks(
    projects: list[dict],
    clients: dict[int, dict],
    methodologies: dict[int, dict],
) -> list[dict]:
    """One chunk per project — denormalised prose so the embedding captures
    all relevant fields in a single vector."""
    chunks = []
    for p in projects:
        client = clients.get(p["client_id"], {})
        meth = methodologies.get(p["methodology_id"], {})

        lines = [
            f"Progetto {p['project_id']}: {p['project_name'] or 'N/A'}",
            f"Cliente: {client.get('client_name', 'N/A')} | Workspace: {p['workspace_id']}",
            f"Topic: {p['research_topic'] or 'N/A'} | Metodologia: {meth.get('methodology_name', 'N/A')}",
        ]
        details = []
        if p.get("country_code"):
            details.append(f"Paese: {p['country_code']}")
        if p.get("sample_size"):
            details.append(f"Campione: {p['sample_size']} rispondenti")
        if p.get("budget") is not None:
            details.append(f"Budget: €{p['budget']:,.0f}")
        if details:
            lines.append(" | ".join(details))
        date_range = " → ".join(filter(None, [p.get("start_date"), p.get("end_date")]))
        if date_range:
            lines.append(f"Periodo: {date_range}")
        lines.append(f"Stato: {p.get('status') or 'N/A'}")
        if p.get("notes"):
            lines.append(f"Note: {p['notes']}")

        chunks.append({
            "id": f"project-{p['project_id'].lower()}",
            "content": "\n".join(lines),
            "metadata": {
                "source": "projects",
                "workspace_id": p["workspace_id"],
                "project_id": p["project_id"],
                "status": p.get("status"),
                "country_code": p.get("country_code"),
                "methodology_code": meth.get("methodology_code"),
                "created_at": f"{p['start_date']}T00:00:00+00:00" if p.get("start_date") else None,
            },
        })
    return chunks


def build_interaction_chunks(interactions: list[dict]) -> list[dict]:
    """One chunk per support interaction — captures the full case context
    (problem + resolution) in a single retrievable unit."""
    chunks = []
    for ix in interactions:
        outcome = "Risolto" if ix.get("resolved") else "Non risolto"
        score = ix.get("satisfaction_score")
        hours = ix.get("resolution_time_hours")

        lines = [
            f"Interazione {ix['interaction_id']} — {ix.get('issue_type', 'N/A')} via {ix.get('channel', 'N/A')}",
            f"Progetto: {ix.get('project_id') or 'N/A'} | Workspace: {ix['workspace_id']}",
            f"Data: {ix['interaction_date']}",
            f"Problema: {ix.get('issue_description') or 'N/A'}",
        ]
        if ix.get("resolution"):
            lines.append(f"Risoluzione: {ix['resolution']}")
        time_str = f"{hours}h" if hours is not None else "N/A"
        score_str = f"{score}/5" if score is not None else "N/A"
        lines.append(f"Esito: {outcome} in {time_str} | Soddisfazione: {score_str}")

        chunks.append({
            "id": f"interaction-{ix['interaction_id'].lower()}",
            "content": "\n".join(lines),
            "metadata": {
                "source": "interactions",
                "workspace_id": ix["workspace_id"],
                "project_id": ix.get("project_id"),
                "interaction_id": ix["interaction_id"],
                "issue_type": ix.get("issue_type"),
                "channel": ix.get("channel"),
                "resolved": ix.get("resolved"),
                "created_at": ix["interaction_date"],
            },
        })
    return chunks


# ─── Embedding ───────────────────────────────────────────────────────────────

def embed_chunks(client: OpenAI, chunks: list[dict]) -> list[dict]:
    for chunk in chunks:
        estimated = len(chunk["content"]) // 3
        if estimated > EMBED_TOKEN_LIMIT:
            print(f"  [WARN] chunk '{chunk['id']}' supera il limite stimato ({estimated} token > {EMBED_TOKEN_LIMIT})")

    texts = [c["content"] for c in chunks]
    n_batches = -(-len(texts) // BATCH_SIZE)  # ceiling division
    result = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i: i + BATCH_SIZE]
        batch_chunks = chunks[i: i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"  Batch {batch_num}/{n_batches} ({len(batch_texts)} chunks)...")

        response = client.embeddings.create(model=EMBED_MODEL, input=batch_texts)
        embeddings = [item.embedding for item in response.data]

        for chunk, emb in zip(batch_chunks, embeddings):
            result.append({**chunk, "embedding": emb})

        if i + BATCH_SIZE < len(texts):
            time.sleep(0.3)  # gentle rate limiting between batches

    return result


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv(ROOT / ".env")
            api_key = os.environ.get("OPENAI_API_KEY")
        except ImportError:
            pass
    if not api_key:
        raise SystemExit("OPENAI_API_KEY not set. Define it as an env variable or in a .env file at the project root.")

    client = OpenAI(api_key=api_key)

    print("Loading cleaned data...")
    faqs = load_json("faq")
    faq_cats_list = load_json("faq_categories")
    projects = load_json("projects")
    clients_list = load_json("clients")
    methodologies_list = load_json("methodologies")
    interactions = load_json("interactions")

    faq_categories: dict[int, str] = {c["category_id"]: c["category_name"] for c in faq_cats_list}
    clients: dict[int, dict] = {c["client_id"]: c for c in clients_list}
    methodologies: dict[int, dict] = {m["methodology_id"]: m for m in methodologies_list}

    print("\nBuilding chunks...")
    faq_chunks = build_faq_chunks(faqs, faq_categories)
    project_chunks = build_project_chunks(projects, clients, methodologies)
    interaction_chunks = build_interaction_chunks(interactions)
    chunks = faq_chunks + project_chunks + interaction_chunks
    print(f"  FAQ: {len(faq_chunks)} | Projects: {len(project_chunks)} | Interactions: {len(interaction_chunks)}")
    print(f"  Total: {len(chunks)} chunks")

    print(f"\nGenerating embeddings ({EMBED_MODEL}, {EMBED_DIM} dim)...")
    records = embed_chunks(client, chunks)

    print(f"\nWriting {OUT_FILE.name}...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Done. {len(records)} records → {OUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
