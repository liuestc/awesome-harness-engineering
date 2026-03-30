#!/usr/bin/env python3
"""
semantic_search.py — Semantic Search for Harness Engineering Resources
=======================================================================
Architecture (AI-First, no heavy dependencies):
  1. Embedding: MiniMax Embedding API (embo-01 model)
  2. Storage: Local JSON vector index (data/embeddings.json)
  3. Search: Cosine similarity in pure Python/NumPy
  4. Output: data/search_index.json (lightweight, for frontend MiniSearch)

Two modes:
  - build: Vectorize all resources → save embeddings.json
  - search: Query → cosine similarity → return top-k results
  - export: Build lightweight search_index.json for frontend full-text search

Usage:
  python scripts/semantic_search.py build
  python scripts/semantic_search.py search "how to design agent feedback loops"
  python scripts/semantic_search.py export
"""

import json
import os
import sys
import math
import logging
import time
from pathlib import Path
from datetime import datetime, timezone
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.json"
SEARCH_INDEX_FILE = DATA_DIR / "search_index.json"

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_EMBED_URL = "https://api.minimax.chat/v1/embeddings"
MINIMAX_CHAT_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"
EMBED_MODEL = "embo-01"
CHAT_MODEL = "MiniMax-M2.5"

# ── Embedding API ─────────────────────────────────────────────────────────────
def get_embedding(text: str) -> list[float] | None:
    """Get embedding vector from MiniMax API."""
    if not MINIMAX_API_KEY:
        log.warning("MINIMAX_API_KEY not set")
        return None
    try:
        resp = requests.post(
            MINIMAX_EMBED_URL,
            headers={"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"},
            json={"model": EMBED_MODEL, "input": [text[:2000]], "type": "query"},
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]
    except Exception as e:
        log.error(f"Embedding error: {e}")
        return None


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Pure Python cosine similarity."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── Resource Loading ──────────────────────────────────────────────────────────
def load_all_resources() -> list[dict]:
    """Load all resources with unified text representation."""
    resources = []

    # Repositories
    repos_file = DATA_DIR / "repositories.json"
    if repos_file.exists():
        repos = json.loads(repos_file.read_text(encoding="utf-8"))
        for r in (repos if isinstance(repos, list) else []):
            text = f"{r.get('name', '')} {r.get('description_zh', '')} {r.get('ai_summary_zh', '')} {' '.join(r.get('key_concepts', []))}"
            resources.append({
                "id": r["id"],
                "type": "repository",
                "title_zh": r.get("name", ""),
                "title_en": r.get("name", ""),
                "url": r.get("url", ""),
                "summary_zh": r.get("ai_summary_zh", r.get("description_zh", "")),
                "summary_en": r.get("ai_summary_en", r.get("description_en", "")),
                "quality_score": r.get("quality_score", 7.0),
                "key_concepts": r.get("key_concepts", []),
                "raw_content": r.get("raw_content", ""),
                "embed_text": text.strip(),
                "embeddings_ready": r.get("embeddings_ready", False),
            })

    # Articles
    articles_file = DATA_DIR / "articles.json"
    if articles_file.exists():
        articles = json.loads(articles_file.read_text(encoding="utf-8"))
        for a in (articles if isinstance(articles, list) else []):
            text = f"{a.get('title_zh', '')} {a.get('title_en', '')} {a.get('summary_zh', '')} {' '.join(a.get('key_concepts', []))}"
            resources.append({
                "id": a["id"],
                "type": "article",
                "title_zh": a.get("title_zh", ""),
                "title_en": a.get("title_en", ""),
                "url": a.get("url", ""),
                "summary_zh": a.get("summary_zh", ""),
                "summary_en": a.get("summary_en", ""),
                "quality_score": a.get("quality_score", 7.0),
                "key_concepts": a.get("key_concepts", []),
                "raw_content": a.get("raw_content", ""),
                "embed_text": text.strip(),
                "embeddings_ready": a.get("embeddings_ready", False),
            })

    # People
    people_file = DATA_DIR / "people.json"
    if people_file.exists():
        people = json.loads(people_file.read_text(encoding="utf-8"))
        for p in (people if isinstance(people, list) else []):
            text = f"{p.get('name', '')} {p.get('role_zh', '')} {p.get('contribution_zh', '')} {p.get('key_quote_zh', '')}"
            resources.append({
                "id": p["id"],
                "type": "person",
                "title_zh": p.get("name", ""),
                "title_en": p.get("name", ""),
                "url": p.get("blog", p.get("twitter", "")),
                "summary_zh": p.get("contribution_zh", ""),
                "summary_en": p.get("contribution_en", ""),
                "quality_score": 8.0,
                "key_concepts": p.get("key_concepts", []),
                "raw_content": p.get("key_quote_zh", ""),
                "embed_text": text.strip(),
                "embeddings_ready": False,
            })

    return resources


# ── Build Mode ────────────────────────────────────────────────────────────────
def build_embeddings():
    """Vectorize all resources and save to embeddings.json."""
    resources = load_all_resources()
    log.info(f"Building embeddings for {len(resources)} resources...")

    # Load existing embeddings to avoid re-computing
    existing = {}
    if EMBEDDINGS_FILE.exists():
        try:
            existing = {e["id"]: e for e in json.loads(EMBEDDINGS_FILE.read_text())}
            log.info(f"Loaded {len(existing)} existing embeddings")
        except Exception:
            pass

    embeddings = []
    new_count = 0

    for i, res in enumerate(resources):
        res_id = res["id"]

        # Skip if already embedded and content hasn't changed
        if res_id in existing:
            embeddings.append(existing[res_id])
            continue

        if not MINIMAX_API_KEY:
            # No API key: create placeholder
            embeddings.append({**res, "embedding": [], "embedded_at": ""})
            continue

        log.info(f"  [{i+1}/{len(resources)}] Embedding: {res['title_zh'][:40]}...")
        vec = get_embedding(res["embed_text"])
        if vec:
            embeddings.append({
                **res,
                "embedding": vec,
                "embedded_at": datetime.now(timezone.utc).isoformat(),
            })
            new_count += 1
            time.sleep(0.5)  # Rate limit
        else:
            embeddings.append({**res, "embedding": [], "embedded_at": ""})

    EMBEDDINGS_FILE.write_text(json.dumps(embeddings, ensure_ascii=False, indent=2))
    log.info(f"Embeddings saved: {len(embeddings)} total, {new_count} new → {EMBEDDINGS_FILE}")
    return embeddings


# ── Search Mode ───────────────────────────────────────────────────────────────
def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Search resources by semantic similarity."""
    if not EMBEDDINGS_FILE.exists():
        log.error("embeddings.json not found. Run: python semantic_search.py build")
        return []

    embeddings = json.loads(EMBEDDINGS_FILE.read_text())
    valid = [e for e in embeddings if e.get("embedding")]

    if not valid:
        log.warning("No embeddings available. Falling back to keyword search.")
        return keyword_search(query, embeddings, top_k)

    log.info(f"Searching '{query}' in {len(valid)} embedded resources...")
    query_vec = get_embedding(query)
    if not query_vec:
        log.warning("Failed to embed query. Falling back to keyword search.")
        return keyword_search(query, embeddings, top_k)

    scored = []
    for e in valid:
        score = cosine_similarity(query_vec, e["embedding"])
        scored.append({
            "id": e["id"],
            "type": e["type"],
            "title_zh": e["title_zh"],
            "title_en": e["title_en"],
            "url": e["url"],
            "summary_zh": e["summary_zh"],
            "quality_score": e.get("quality_score", 7.0),
            "key_concepts": e.get("key_concepts", []),
            "similarity": round(score, 4),
        })

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    results = scored[:top_k]

    # Use MiniMax to generate a synthesis answer
    if MINIMAX_API_KEY and results:
        context = "\n".join([
            f"- [{r['type']}] {r['title_zh']}: {r['summary_zh'][:100]}"
            for r in results[:5]
        ])
        synthesis_prompt = f"""基于以下 Harness Engineering 资源，回答问题："{query}"

相关资源：
{context}

请用 2-3 句话给出精炼的综合回答，重点突出核心洞见。"""
        try:
            resp = requests.post(
                MINIMAX_CHAT_URL,
                headers={"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"},
                json={"model": CHAT_MODEL, "messages": [{"role": "user", "content": synthesis_prompt}],
                      "max_tokens": 512, "temperature": 0.3},
                timeout=30
            )
            synthesis = resp.json()["choices"][0]["message"]["content"]
            log.info(f"\n=== AI Synthesis ===\n{synthesis}\n")
        except Exception:
            pass

    return results


def keyword_search(query: str, resources: list[dict], top_k: int = 10) -> list[dict]:
    """Fallback keyword search."""
    query_lower = query.lower()
    scored = []
    for r in resources:
        text = f"{r.get('title_zh', '')} {r.get('title_en', '')} {r.get('summary_zh', '')} {' '.join(r.get('key_concepts', []))}".lower()
        score = sum(1 for word in query_lower.split() if word in text)
        if score > 0:
            scored.append({**r, "similarity": score / 10.0})
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]


# ── Export Mode ───────────────────────────────────────────────────────────────
def export_search_index():
    """Export lightweight search index for frontend MiniSearch."""
    resources = load_all_resources()

    index = []
    for r in resources:
        index.append({
            "id": r["id"],
            "type": r["type"],
            "title_zh": r["title_zh"],
            "title_en": r["title_en"],
            "url": r["url"],
            "summary_zh": r["summary_zh"][:200],
            "summary_en": r["summary_en"][:200],
            "quality_score": r["quality_score"],
            "key_concepts": r["key_concepts"][:5],
        })

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(index),
        "items": index,
    }
    SEARCH_INDEX_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    log.info(f"Search index exported: {len(index)} items → {SEARCH_INDEX_FILE}")
    return output


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "export"

    if mode == "build":
        build_embeddings()
    elif mode == "search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "harness engineering best practices"
        results = semantic_search(query)
        print(f"\nTop {len(results)} results for: '{query}'")
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['type']}] {r['title_zh']} (sim={r['similarity']:.3f})")
            print(f"     {r['url']}")
    elif mode == "export":
        export_search_index()
    else:
        print("Usage: python semantic_search.py [build|search <query>|export]")
