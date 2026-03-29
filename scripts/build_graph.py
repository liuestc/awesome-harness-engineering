"""
知识图谱关系构建脚本（预留功能）
=====================================
使用 MiniMax 分析各资源之间的关系，生成知识图谱数据。
后期可用于：
  - 网页中渲染交互式知识图谱（D3.js / Cytoscape.js）
  - 发现资源之间的引用关系
  - 聚类分析，识别核心概念节点
  - 生成资源推荐

运行方式：
  python scripts/build_graph.py

输出：
  data/graph.json  — 节点和边的图数据
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"
MINIMAX_MODEL = "MiniMax-Text-01"


def minimax_chat(messages: list[dict]) -> str:
    if not MINIMAX_API_KEY:
        return ""
    try:
        resp = requests.post(
            MINIMAX_API_URL,
            headers={"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"},
            json={"model": MINIMAX_MODEL, "messages": messages, "temperature": 0.2, "max_tokens": 3000},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        log.error(f"MiniMax error: {e}")
        return ""


def load_all_resources() -> list[dict]:
    """加载所有资源，统一格式"""
    resources = []
    for filename, rtype in [("repositories.json", "repository"), ("articles.json", "article"), ("people.json", "person")]:
        items = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
        for item in items:
            resources.append({
                "id": item["id"],
                "type": rtype,
                "title": item.get("title_zh") or item.get("name") or item.get("description_zh", "")[:50],
                "key_concepts": item.get("key_concepts", []),
                "cluster": item.get("graph_node", {}).get("cluster", "general"),
                "url": item.get("url", ""),
            })
    return resources


def build_concept_edges(resources: list[dict]) -> list[dict]:
    """基于共享 key_concepts 自动生成边"""
    edges = []
    concept_to_resources: dict[str, list[str]] = {}

    for r in resources:
        for concept in r.get("key_concepts", []):
            concept_lower = concept.lower()
            if concept_lower not in concept_to_resources:
                concept_to_resources[concept_lower] = []
            concept_to_resources[concept_lower].append(r["id"])

    # 共享概念的资源之间建立边
    seen_pairs = set()
    for concept, ids in concept_to_resources.items():
        if len(ids) < 2:
            continue
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                pair = tuple(sorted([ids[i], ids[j]]))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                edges.append({
                    "source": ids[i],
                    "target": ids[j],
                    "relation_type": "shares_concept",
                    "label": concept,
                    "weight": 0.5,
                })

    return edges


def build_ai_relations(resources: list[dict]) -> list[dict]:
    """使用 MiniMax 分析更深层的引用和影响关系"""
    if not MINIMAX_API_KEY:
        log.warning("MiniMax API key not set, skipping AI relation analysis")
        return []

    # 构建资源摘要列表
    resource_list = "\n".join([
        f"- [{r['id']}] ({r['type']}) {r['title']} | 概念: {', '.join(r['key_concepts'][:3])}"
        for r in resources[:30]  # 限制数量避免 token 过多
    ])

    prompt = f"""你是知识图谱专家。以下是 Harness Engineering 领域的资源列表，请分析它们之间的关系。

资源列表：
{resource_list}

请识别以下类型的关系并以 JSON 数组返回：
- "引用"：一个资源引用或基于另一个资源
- "影响"：一个资源的思想影响了另一个资源
- "扩展"：一个资源扩展或深化了另一个资源的概念
- "对比"：两个资源讨论相似主题但有不同观点

只返回 JSON 数组，格式：
[
  {{"source": "id1", "target": "id2", "relation_type": "引用", "label": "简短描述", "weight": 0.8}},
  ...
]
最多返回 20 条关系。"""

    result = minimax_chat([{"role": "user", "content": prompt}])
    if not result:
        return []

    try:
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        return json.loads(result)
    except Exception as e:
        log.error(f"Failed to parse AI relations: {e}")
        return []


def build_graph():
    """构建完整知识图谱"""
    log.info("Building knowledge graph...")
    resources = load_all_resources()
    log.info(f"Loaded {len(resources)} resources")

    # 构建节点
    nodes = []
    for r in resources:
        nodes.append({
            "id": r["id"],
            "type": r["type"],
            "title": r["title"],
            "cluster": r["cluster"],
            "url": r["url"],
            "key_concepts": r.get("key_concepts", []),
        })

    # 构建边（概念共享 + AI 分析）
    concept_edges = build_concept_edges(resources)
    log.info(f"Concept-based edges: {len(concept_edges)}")

    ai_edges = build_ai_relations(resources)
    log.info(f"AI-analyzed edges: {len(ai_edges)}")

    all_edges = concept_edges + ai_edges

    # 去重边
    seen = set()
    unique_edges = []
    for e in all_edges:
        key = tuple(sorted([e["source"], e["target"]])) + (e["relation_type"],)
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    graph = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "node_count": len(nodes),
        "edge_count": len(unique_edges),
        "nodes": nodes,
        "edges": unique_edges,
        # 预留：聚类信息
        "clusters": {
            "foundations": {"label_zh": "基础理论", "label_en": "Foundations", "color": "#3B82F6"},
            "context-engineering": {"label_zh": "上下文工程", "label_en": "Context Engineering", "color": "#10B981"},
            "feedback-loops": {"label_zh": "反馈循环", "label_en": "Feedback Loops", "color": "#F59E0B"},
            "best-practices": {"label_zh": "最佳实践", "label_en": "Best Practices", "color": "#8B5CF6"},
            "tools": {"label_zh": "工具", "label_en": "Tools", "color": "#EF4444"},
            "frameworks": {"label_zh": "框架", "label_en": "Frameworks", "color": "#06B6D4"},
            "analysis": {"label_zh": "分析", "label_en": "Analysis", "color": "#84CC16"},
            "performance": {"label_zh": "性能", "label_en": "Performance", "color": "#F97316"},
            "observability": {"label_zh": "可观测性", "label_en": "Observability", "color": "#EC4899"},
            "tutorials": {"label_zh": "教程", "label_en": "Tutorials", "color": "#6366F1"},
            "community": {"label_zh": "社区", "label_en": "Community", "color": "#14B8A6"},
        }
    }

    output_path = DATA_DIR / "graph.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)
    log.info(f"Graph saved: {len(nodes)} nodes, {len(unique_edges)} edges")
    return graph


if __name__ == "__main__":
    build_graph()
