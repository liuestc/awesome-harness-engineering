# ⚡ Awesome Harness Engineering

> **Harness Engineering** — 驾驭 AI Agent 的工程艺术。围绕 AI Agent 构建约束机制、反馈回路和持续改进循环的系统工程实践。
>
> `Agent = Model + Harness`

[![Daily Update](https://github.com/liuestc/awesome-harness-engineering/actions/workflows/daily_crawl.yml/badge.svg)](https://github.com/liuestc/awesome-harness-engineering/actions/workflows/daily_crawl.yml)
[![Resources](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/liuestc/awesome-harness-engineering/main/data/meta.json&query=$.stats.total_resources&label=Resources&color=blue)](data/meta.json)

🌐 **[查看交互式网站](https://liuestc.github.io/awesome-harness-engineering)**

---

## 📊 数据统计

数据每日自动更新，由 MiniMax 2.7 + Tavily 驱动。

| 类型 | 数量 |
|------|------|
| GitHub 仓库 | 见 [data/repositories.json](data/repositories.json) |
| 文章/博客 | 见 [data/articles.json](data/articles.json) |
| 关键人物 | 见 [data/people.json](data/people.json) |
| 最佳实践 | 见 [data/practices.json](data/practices.json) |
| 知识图谱 | 见 [data/graph.json](data/graph.json) |

---

## 🏗️ 项目结构

```
awesome-harness-engineering/
├── data/                    # 核心数据（每日自动更新）
│   ├── repositories.json    # GitHub 仓库
│   ├── articles.json        # 文章/博客
│   ├── people.json          # 关键人物
│   ├── practices.json       # 最佳实践
│   ├── timeline.json        # 演进时间轴
│   ├── graph.json           # 知识图谱（每周重建）
│   └── meta.json            # 元数据 & 统计
├── scripts/                 # 自动化脚本
│   ├── crawler.py           # 主爬取 & 分析 Pipeline
│   ├── update_stars.py      # GitHub Stars 同步
│   ├── build_graph.py       # 知识图谱构建
│   └── requirements.txt
└── .github/workflows/
    └── daily_crawl.yml      # 每日定时任务
```

---

## 🤖 自动化 Pipeline

```
每天 10:00 (北京时间)
    ↓
Tavily Search API  ──→  发现最新文章/博客
GitHub Search API  ──→  发现新仓库
    ↓
MiniMax 2.7 分析
  ├── 相关性判断（是否属于 Harness Engineering 生态）
  ├── 质量评分（6分以上收录）
  ├── 中英文摘要生成
  ├── 关键概念提取
  └── 知识图谱节点分类
    ↓
去重 & 存储到 data/*.json
    ↓
git commit + push（附带更新日志）
    ↓
网站自动展示最新数据
```

---

## 🔧 本地运行

```bash
# 克隆仓库
git clone https://github.com/liuestc/awesome-harness-engineering.git
cd awesome-harness-engineering

# 安装依赖
pip install -r scripts/requirements.txt

# 配置环境变量
export TAVILY_API_KEY="your_tavily_key"
export MINIMAX_API_KEY="your_minimax_key"
export GITHUB_TOKEN="your_github_token"  # 可选，提高 API 限额

# 运行爬虫
python scripts/crawler.py

# 更新 GitHub Stars
python scripts/update_stars.py

# 构建知识图谱
python scripts/build_graph.py
```

---

## ⚙️ GitHub Secrets 配置

在仓库 Settings → Secrets and variables → Actions 中添加：

| Secret | 说明 |
|--------|------|
| `TAVILY_API_KEY` | Tavily 搜索 API Key |
| `MINIMAX_API_KEY` | MiniMax 2.7 API Key |
| `NOTIFY_EMAIL` | 失败通知邮箱 |
| `SMTP_HOST` | 邮件服务器（如 smtp.qq.com） |
| `SMTP_PORT` | 端口（如 587） |
| `SMTP_USER` | 发件邮箱账号 |
| `SMTP_PASS` | 邮箱授权码 |

---

## 📈 数据字段说明（面向未来扩展）

每条资源除基础信息外，还预留了以下字段用于后续深度分析：

```json
{
  "raw_content": "原始全文（供洗数据）",
  "key_concepts": ["核心概念列表"],
  "relations": ["与其他资源的关系"],
  "quality_score": 8.5,
  "ai_summary_zh": "中文 AI 摘要",
  "ai_summary_en": "English AI summary",
  "embeddings_ready": false,
  "graph_node": {
    "type": "article",
    "cluster": "feedback-loops"
  }
}
```

**未来规划：**
- [ ] 向量化 (`embeddings_ready`) → 语义搜索
- [ ] 知识图谱可视化 → 交互式关系图
- [ ] 自动生成每周 Digest 邮件
- [ ] 基于关系图的资源推荐
- [ ] 支持 Twitter/X 用户监控

---

## 📚 什么是 Harness Engineering？

| 层次 | 定义 |
|------|------|
| Prompt Engineering | 你对 AI 说的话 |
| Context Engineering | 帮 AI 看路的一切（地图、路标） |
| **Harness Engineering** | **缰绳和马鞍** — 约束、引导、管控 AI 的执行环境 |

**五大核心组件：**
1. **Context Engineering** — 持续增强的代码库知识库
2. **Architectural Constraints** — 自定义 linter 和结构性测试
3. **Feedback Loops** — Generator-Evaluator 循环
4. **Observability** — 记录 Agent 的所有过程日志
5. **Garbage Collection** — 定期清理不一致和衰减

---

## 🤝 贡献

欢迎提交 Issue 推荐新资源！请包含：
- 资源 URL
- 简短说明（为什么值得收录）

---

*由 [Harness Bot 🤖](https://github.com/features/actions) 每日自动维护*
