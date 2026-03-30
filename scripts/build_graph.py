#!/usr/bin/env python3
"""
build_graph.py — Knowledge Graph Builder for Awesome Harness Engineering
==========================================================================
Design Philosophy (AI-First):
  1. Seed Nodes: Core concepts, people, orgs always present
  2. Resource Nodes: Repos, articles, tools from data/*.json
  3. Entity Extraction: MiniMax-M2.5 extracts deeper entities from raw_content
  4. Relation Modeling: NetworkX DiGraph, exported to graph.json for D3.js
  5. Metrics: PageRank + Betweenness centrality for node importance

Node types: person | repo | article | concept | tool | organization
Edge types: authored | references | implements | influenced_by | part_of | discusses
"""

import json
import os
import re
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
GRAPH_FILE = DATA_DIR / "graph.json"
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"
MODEL = "MiniMax-M2.5"

# ── Seed Nodes ───────────────────────────────────────────────────────────────
SEED_CONCEPTS = [
    {"id": "concept_harness_engineering", "label": "Harness Engineering", "type": "concept",
     "desc": "The discipline of designing execution environments that constrain and guide AI agents",
     "cluster": "foundations"},
    {"id": "concept_context_engineering", "label": "Context Engineering", "type": "concept",
     "desc": "Crafting the information environment (context window) for AI agents",
     "cluster": "context-engineering"},
    {"id": "concept_agent_loop", "label": "Agent Loop", "type": "concept",
     "desc": "The iterative perceive-think-act cycle of an AI agent",
     "cluster": "foundations"},
    {"id": "concept_feedback_loop", "label": "Feedback Loop", "type": "concept",
     "desc": "Mechanisms for agents to observe results and self-correct",
     "cluster": "feedback-loops"},
    {"id": "concept_ralph_loop", "label": "Ralph Loop", "type": "concept",
     "desc": "Mitchell Hashimoto's framework: Read-Act-Learn-Plan-Harness",
     "cluster": "foundations"},
    {"id": "concept_context_gc", "label": "Context GC", "type": "concept",
     "desc": "Strategies for managing and pruning the agent context window",
     "cluster": "context-engineering"},
    {"id": "concept_observability", "label": "Observability", "type": "concept",
     "desc": "Monitoring and tracing agent behavior and decision paths",
     "cluster": "observability"},
    {"id": "concept_vibe_coding", "label": "Vibe Coding", "type": "concept",
     "desc": "Casual AI-assisted coding without systematic engineering discipline",
     "cluster": "community"},
    {"id": "concept_agents_md", "label": "AGENTS.md", "type": "concept",
     "desc": "Project-level instruction file that defines agent behavior and constraints",
     "cluster": "best-practices"},
    {"id": "concept_prompt_engineering", "label": "Prompt Engineering", "type": "concept",
     "desc": "Crafting inputs to guide model outputs",
     "cluster": "foundations"},
    {"id": "concept_tool_use", "label": "Tool Use", "type": "concept",
     "desc": "Agent ability to call external tools and APIs",
     "cluster": "frameworks"},
    {"id": "concept_multi_agent", "label": "Multi-Agent Systems", "type": "concept",
     "desc": "Architectures with multiple coordinating AI agents",
     "cluster": "frameworks"},
]

SEED_PEOPLE = [
    {"id": "person_mitchell_hashimoto", "label": "Mitchell Hashimoto", "type": "person",
     "url": "https://mitchellh.com", "desc": "HashiCorp founder, coined Harness Engineering",
     "cluster": "community"},
    {"id": "person_kasong2048", "label": "kasong2048", "type": "person",
     "url": "https://x.com/kasong2048", "desc": "Key Harness Engineering advocate on X",
     "cluster": "community"},
    {"id": "org_anthropic", "label": "Anthropic Engineering", "type": "organization",
     "url": "https://anthropic.com/engineering", "desc": "Published foundational Harness design patterns",
     "cluster": "community"},
    {"id": "org_openai", "label": "OpenAI", "type": "organization",
     "url": "https://openai.com", "desc": "Published Harness Engineering best practices",
     "cluster": "community"},
    {"id": "org_humanlayer", "label": "HumanLayer", "type": "organization",
     "url": "https://humanlayer.dev", "desc": "Human-in-the-loop for AI agents",
     "cluster": "tools"},
]

SEED_RELATIONS = [
    ("concept_harness_engineering", "concept_context_engineering", "part_of", 0.9),
    ("concept_harness_engineering", "concept_agent_loop", "implements", 0.9),
    ("concept_harness_engineering", "concept_feedback_loop", "implements", 0.85),
    ("concept_harness_engineering", "concept_observability", "implements", 0.8),
    ("concept_harness_engineering", "concept_context_gc", "implements", 0.8),
    ("concept_harness_engineering", "concept_tool_use", "implements", 0.75),
    ("concept_ralph_loop", "concept_harness_engineering", "part_of", 0.95),
    ("concept_agents_md", "concept_harness_engineering", "implements", 0.85),
    ("concept_harness_engineering", "concept_vibe_coding", "influenced_by", 0.7),
    ("concept_harness_engineering", "concept_prompt_engineering", "influenced_by", 0.8),
    ("concept_multi_agent", "concept_harness_engineering", "implements", 0.8),
    ("person_mitchell_hashimoto", "concept_harness_engineering", "authored", 1.0),
    ("person_mitchell_hashimoto", "concept_ralph_loop", "authored", 1.0),
    ("org_anthropic", "concept_harness_engineering", "discusses", 0.9),
    ("org_openai", "concept_harness_engineering", "discusses", 0.85),
    ("person_kasong2048", "concept_harness_engineering", "discusses", 0.9),
    ("org_humanlayer", "concept_harness_engineering", "implements", 0.8),
]

# ── MiniMax Helper ───────────────────────────────────────────────────────────
def call_minimax(prompt: str, system: str = "") -> str:
    if not MINIMAX_API_KEY:
        return ""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        resp = requests.post(
            MINIMAX_URL,
            headers={"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL, "messages": messages, "max_tokens": 4096,
                  "temperature": 0.1, "response_format": {"type": "json_object"}},
            timeout=60
        )
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if "<think>" in content:
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
        return content
    except Exception as e:
        log.error(f"MiniMax error: {e}")
        return ""


def extract_entities_and_relations(resource: dict) -> dict:
    """Use MiniMax to extract entities and relations from a resource."""
    title = resource.get("title", "")
    summary = resource.get("ai_summary_zh") or resource.get("ai_summary_en") or resource.get("description", "")
    raw = resource.get("raw_content", "")[:1500]
    key_concepts = resource.get("key_concepts", [])

    prompt = f"""分析以下 Harness Engineering 资源，提取实体和关系。

资源标题: {title}
摘要: {summary[:300]}
关键概念: {', '.join(key_concepts) if key_concepts else '无'}
原文片段: {raw[:400] if raw else '无'}

返回 JSON：
{{
  "entities": [
    {{"label": "英文实体名", "type": "concept|person|tool|organization", "desc": "一句话描述"}}
  ],
  "relations": [
    {{"source": "源实体label", "target": "目标实体label", "type": "references|implements|influenced_by|discusses|authored|part_of", "weight": 0.8}}
  ]
}}

规则：只提取 Harness Engineering 生态相关实体，最多 4 个实体和 5 条关系，label 用英文。"""

    result = call_minimax(prompt, system="你是知识图谱构建专家，专注于 AI Agent Harness Engineering 领域。")
    if not result:
        return {"entities": [], "relations": []}
    try:
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass
    return {"entities": [], "relations": []}


# ── Simple Graph (no networkx dependency) ───────────────────────────────────
class SimpleGraph:
    def __init__(self):
        self.nodes = {}  # id -> attrs
        self.edges = []  # list of (src, tgt, attrs)
        self._edge_set = set()

    def add_node(self, node_id: str, **attrs):
        if node_id not in self.nodes:
            self.nodes[node_id] = {"id": node_id, **attrs}

    def has_node(self, node_id: str) -> bool:
        return node_id in self.nodes

    def add_edge(self, src: str, tgt: str, **attrs):
        key = (src, tgt, attrs.get("type", ""))
        if key not in self._edge_set:
            self._edge_set.add(key)
            self.edges.append((src, tgt, attrs))

    def degree(self, node_id: str) -> int:
        count = 0
        for s, t, _ in self.edges:
            if s == node_id or t == node_id:
                count += 1
        return count

    def compute_pagerank(self, damping=0.85, iterations=50) -> dict:
        """Simple PageRank implementation."""
        nodes = list(self.nodes.keys())
        n = len(nodes)
        if n == 0:
            return {}
        pr = {node: 1.0 / n for node in nodes}
        # Build adjacency
        out_edges = {node: [] for node in nodes}
        for s, t, attrs in self.edges:
            if s in out_edges:
                out_edges[s].append((t, attrs.get("weight", 0.5)))
        for _ in range(iterations):
            new_pr = {}
            for node in nodes:
                rank = (1 - damping) / n
                for s, t, attrs in self.edges:
                    if t == node:
                        out_count = len(out_edges.get(s, []))
                        if out_count > 0:
                            rank += damping * pr[s] * attrs.get("weight", 0.5) / out_count
                new_pr[node] = rank
            pr = new_pr
        return pr


# ── Graph Builder ────────────────────────────────────────────────────────────
def load_all_resources() -> list:
    resources = []
    for fname, rtype in [("repositories.json", "repo"), ("articles.json", "article"), ("people.json", "person")]:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            continue
        data = json.loads(fpath.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("items", [])
        for item in items:
            item["_rtype"] = rtype
            resources.append(item)
    return resources


def build_node_id(label: str, node_type: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9]', '_', label.lower().strip())
    return f"{node_type}_{clean}"


def build_graph() -> dict:
    G = SimpleGraph()

    # 1. Add seed nodes
    log.info("Adding seed nodes...")
    for node in SEED_CONCEPTS + SEED_PEOPLE:
        G.add_node(node["id"], **node)

    # 2. Add seed relations
    for src, tgt, rel_type, weight in SEED_RELATIONS:
        G.add_edge(src, tgt, type=rel_type, weight=weight)

    # 3. Load and add resources
    resources = load_all_resources()
    log.info(f"Processing {len(resources)} resources...")

    for i, res in enumerate(resources):
        res_id = res.get("id", f"resource_{i}")
        res_type = res.get("_rtype", res.get("type", "article"))
        title = res.get("title") or res.get("name") or res.get("title_zh") or f"Resource {i}"
        url = res.get("url", "")
        cluster = res.get("graph_node", {}).get("cluster", "general")

        G.add_node(res_id,
                   label=str(title)[:60],
                   type=res_type,
                   url=url,
                   quality_score=res.get("quality_score", 7.0),
                   date_added=res.get("date_added", ""),
                   desc=str(res.get("ai_summary_zh") or res.get("description") or "")[:100],
                   cluster=cluster)

        # Connect to seed concepts via key_concepts
        key_concepts = res.get("key_concepts", [])
        for kc in key_concepts:
            kc_lower = kc.lower()
            for seed in SEED_CONCEPTS:
                if any(word in kc_lower for word in seed["label"].lower().split()):
                    G.add_edge(res_id, seed["id"], type="discusses", weight=0.7)
                    break

        # Default connections
        if res_type == "repo":
            G.add_edge(res_id, "concept_harness_engineering", type="implements", weight=0.75)
        elif res_type == "article":
            G.add_edge(res_id, "concept_harness_engineering", type="discusses", weight=0.7)

        # MiniMax deep extraction (first 15 resources with raw_content)
        if MINIMAX_API_KEY and res.get("raw_content") and i < 15:
            log.info(f"  Extracting entities from: {str(title)[:40]}...")
            extracted = extract_entities_and_relations(res)
            time.sleep(1.5)

            for ent in extracted.get("entities", []):
                ent_id = build_node_id(ent["label"], ent["type"])
                if not G.has_node(ent_id):
                    G.add_node(ent_id, label=ent["label"], type=ent["type"],
                               desc=ent.get("desc", ""), cluster="general")
                G.add_edge(res_id, ent_id, type="discusses", weight=0.6)

            for rel in extracted.get("relations", []):
                src_id = build_node_id(rel["source"], "concept")
                tgt_id = build_node_id(rel["target"], "concept")
                # Match to existing nodes
                for node_id in G.nodes:
                    node_label = G.nodes[node_id].get("label", "").lower()
                    if rel["source"].lower() in node_label:
                        src_id = node_id
                    if rel["target"].lower() in node_label:
                        tgt_id = node_id
                if G.has_node(src_id) and G.has_node(tgt_id):
                    G.add_edge(src_id, tgt_id,
                               type=rel.get("type", "references"),
                               weight=rel.get("weight", 0.6))

    # 4. Compute metrics
    log.info("Computing graph metrics...")
    pagerank = G.compute_pagerank()

    # 5. Serialize
    nodes_out = []
    for node_id, attrs in G.nodes.items():
        nodes_out.append({
            "id": node_id,
            "label": attrs.get("label", node_id),
            "type": attrs.get("type", "concept"),
            "url": attrs.get("url", ""),
            "desc": attrs.get("desc", ""),
            "cluster": attrs.get("cluster", "general"),
            "quality_score": attrs.get("quality_score", 0),
            "date_added": attrs.get("date_added", ""),
            "pagerank": round(pagerank.get(node_id, 0), 4),
            "degree": G.degree(node_id),
        })

    edges_out = []
    for src, tgt, attrs in G.edges:
        edges_out.append({
            "source": src,
            "target": tgt,
            "type": attrs.get("type", "references"),
            "weight": round(attrs.get("weight", 0.5), 2),
        })

    nodes_out.sort(key=lambda x: x["pagerank"], reverse=True)

    # Count types
    node_types = {}
    edge_types = {}
    for n in nodes_out:
        t = n["type"]
        node_types[t] = node_types.get(t, 0) + 1
    for e in edges_out:
        t = e["type"]
        edge_types[t] = edge_types.get(t, 0) + 1

    graph_data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stats": {
            "total_nodes": len(nodes_out),
            "total_edges": len(edges_out),
            "node_types": node_types,
            "edge_types": edge_types,
        },
        "clusters": {
            "foundations": {"label_zh": "基础理论", "label_en": "Foundations", "color": "#3B82F6"},
            "context-engineering": {"label_zh": "上下文工程", "label_en": "Context Engineering", "color": "#10B981"},
            "feedback-loops": {"label_zh": "反馈循环", "label_en": "Feedback Loops", "color": "#F59E0B"},
            "best-practices": {"label_zh": "最佳实践", "label_en": "Best Practices", "color": "#8B5CF6"},
            "tools": {"label_zh": "工具", "label_en": "Tools", "color": "#EF4444"},
            "frameworks": {"label_zh": "框架", "label_en": "Frameworks", "color": "#06B6D4"},
            "observability": {"label_zh": "可观测性", "label_en": "Observability", "color": "#EC4899"},
            "community": {"label_zh": "社区", "label_en": "Community", "color": "#14B8A6"},
            "general": {"label_zh": "通用", "label_en": "General", "color": "#94A3B8"},
        },
        "nodes": nodes_out,
        "edges": edges_out,
    }

    GRAPH_FILE.write_text(json.dumps(graph_data, ensure_ascii=False, indent=2))
    log.info(f"Graph saved: {len(nodes_out)} nodes, {len(edges_out)} edges → {GRAPH_FILE}")
    return graph_data


if __name__ == "__main__":
    log.info("Building Harness Engineering Knowledge Graph...")
    result = build_graph()
    log.info(f"Done! Node types: {result['stats']['node_types']}")
    log.info(f"      Edge types: {result['stats']['edge_types']}")
