# SGG Data Agent — Code Wiki

> **项目名称**: `data-agent` (掌柜问数 — 数据智能体)
> **版本**: 0.1.0
> **Python**: >= 3.12
> **包管理器**: uv (pyproject.toml)

---

## 目录

1. [项目概述](#1-项目概述)
2. [整体架构](#2-整体架构)
3. [目录结构](#3-目录结构)
4. [配置系统](#4-配置系统)
5. [核心基础设施 (`app/core/`)](#5-核心基础设施-appcore)
6. [客户端管理器 (`app/clients/`)](#6-客户端管理器-appclients)
7. [数据模型层 (`app/models/`)](#7-数据模型层-appmodels)
8. [业务实体层 (`app/entities/`)](#8-业务实体层-appentities)
9. [对象映射层 (`app/mappers/`)](#9-对象映射层-appmappers)
10. [持久层 (`app/repositories/`)](#10-持久层-apprepositories)
11. [业务服务层 (`app/services/`)](#11-业务服务层-appservices)
12. [提示词系统 (`app/prompt/` + `prompts/`)](#12-提示词系统-appprompt--prompts)
13. [智能体工作流 (`app/agent/`)](#13-智能体工作流-appagent)
14. [脚本与工具 (`app/scripts/`)](#14-脚本与工具-appscripts)
15. [依赖关系](#15-依赖关系)
16. [项目运行方式](#16-项目运行方式)
17. [附录：技术栈总览](#17-附录技术栈总览)

---

## 1. 项目概述

`data-agent` 是 **尚硅谷大模型项目之掌柜问数** 的后端数据智能体服务。该项目面向企业数仓场景，结合大模型（LLM）、向量检索、全文检索等技术，实现自然语言到 SQL 的智能转换与数据查询（NL2SQL）。

**核心能力：**
- 连接 MySQL 数仓（dw）与元数据库（meta），管理表/字段/指标元数据
- 集成 Elasticsearch 提供全文检索能力（字段枚举值匹配）
- 集成 Qdrant 向量数据库 + HuggingFace Embedding 模型实现语义检索（字段/指标召回）
- 基于 LangChain / LangGraph 构建 LLM 工作流，编排多节点检索-生成流水线
- 集成 DeepSeek 大模型进行自然语言理解与 SQL 生成

**两条主要业务流：**
1. **元数据知识库构建流**（离线）：将人工配置的元信息同步到 MySQL meta、Qdrant 向量库、ES 全文索引
2. **问数智能体工作流**（在线）：自然语言 → 关键词抽取 → 多路召回 → 过滤 → SQL 生成 → 校验/校正 → 执行

**涉及的外部服务（均部署于 `192.168.200.10`）：**

| 服务 | 端口 | 用途 |
|------|------|------|
| MySQL (meta) | 3306 | 元数据存储（表、字段、指标信息） |
| MySQL (dw) | 3306 | 数仓数据存储 |
| Elasticsearch | 9200 | 全文检索（字段取值） |
| Qdrant | 6333 | 向量语义检索（字段/指标） |
| Embedding Service | 8081 | 文本向量化（BAAI/bge-large-zh-v1.5） |
| DeepSeek LLM | API | 大模型推理 |

---

## 2. 整体架构

### 2.1 分层架构

```
┌──────────────────────────────────────────────────────────┐
│  入口层   main.py (FastAPI 预留) / app/scripts/*.py       │
├──────────────────────────────────────────────────────────┤
│  智能体层 app/agent/  (LangGraph 工作流编排)              │
│    graph.py · state.py · context.py · llm.py · nodes/    │
├──────────────────────────────────────────────────────────┤
│  服务层   app/services/  (MetaKnowledgeService 业务逻辑)  │
├──────────────────────────────────────────────────────────┤
│  持久层   app/repositories/  (es / mysql[dw,meta] / qdrant)│
├──────────────────────────────────────────────────────────┤
│  映射层   app/mappers/   (entity ↔ ORM model 转换)        │
├──────────────────────────────────────────────────────────┤
│  实体层   app/entities/  (业务 dataclass)                  │
│  模型层   app/models/    (SQLAlchemy ORM 模型)            │
├──────────────────────────────────────────────────────────┤
│  客户端层 app/clients/   (MySQL / ES / Qdrant / Embedding) │
├──────────────────────────────────────────────────────────┤
│  核心层   app/core/      (log · context)                   │
│  配置层   app/conf/      (app_config · meta_config)        │
└──────────────────────────────────────────────────────────┘
```

**分层职责说明：**

| 层级 | 目录 | 职责 |
|------|------|------|
| 入口层 | `main.py` / `app/scripts/` | FastAPI 应用入口（预留）、离线脚本入口 |
| 智能体层 | `app/agent/` | 基于 LangGraph 编排问数工作流，定义节点与边 |
| 服务层 | `app/services/` | 封装业务逻辑（元数据知识库构建） |
| 持久层 | `app/repositories/` | 屏蔽数据存储细节，提供 ES/MySQL/Qdrant 的 CRUD |
| 映射层 | `app/mappers/` | 业务实体与 ORM 模型互转 |
| 实体层 | `app/entities/` | 纯数据业务对象（dataclass） |
| 模型层 | `app/models/` | 元数据库 ORM 模型定义 |
| 客户端层 | `app/clients/` | 外部服务连接管理（单例） |
| 核心层 | `app/core/` | 日志、请求上下文 |
| 配置层 | `app/conf/` | 统一配置管理（OmegaConf + dataclass） |

### 2.2 问数智能体工作流（核心流程）

```
                          ┌─────────────────┐
                          │  extract_keywords│  (jieba 抽取关键词)
                          └────────┬─────────┘
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                     ▼
     ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
     │  recall_column  │  │  recall_metric  │  │  recall_value   │
     │ (字段向量召回)   │  │ (指标向量召回)   │  │ (取值全文召回)   │
     └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
              └────────────────────┼────────────────────┘
                                   ▼
                          ┌─────────────────┐
                          │merge_retrieved_info│ (合并召回信息)
                          └────────┬─────────┘
              ┌────────────────────┴────────────────────┐
              ▼                                          ▼
     ┌─────────────────┐                        ┌─────────────────┐
     │  filter_table   │                        │  filter_metric  │
     │ (过滤表/字段)    │                        │ (过滤指标)       │
     └────────┬────────┘                        └────────┬────────┘
              └────────────────────┬────────────────────┘
                                   ▼
                          ┌─────────────────┐
                          │ add_extra_context│ (补充上下文/时间)
                          └────────┬─────────┘
                                   ▼
                          ┌─────────────────┐
                          │   generate_sql  │ (LLM 生成 SQL)
                          └────────┬─────────┘
                                   ▼
                          ┌─────────────────┐
                          │   validate_sql  │ (校验 SQL)
                          └────────┬─────────┘
                                   │
                      error? ──────┴────── no error?
                        │                   │
                        ▼                   ▼
                ┌─────────────────┐  ┌─────────────────┐
                │   correct_sql   │  │   execute_sql   │
                │ (LLM 校正 SQL)   │  │ (执行 SQL)      │
                └────────┬────────┘  └────────┬────────┘
                         └──────►─────────────┘
                                   ▼
                                   END
```

---

## 3. 目录结构

```
sgg_data-agent/
├── main.py                          # 应用入口（PyCharm 默认模板，FastAPI 预留）
├── pyproject.toml                   # 项目元数据与依赖声明
├── uv.lock                          # uv 依赖锁定文件
├── README.md                        # 项目说明（空）
├── CODE_WIKI.md                     # 本文档
│
├── conf/                            # 配置文件目录
│   ├── app_config.yaml              # 应用主配置（数据库、ES、Qdrant、LLM等）
│   ├── meta_config.yaml             # 元数据知识库人工配置（表/字段/指标定义）
│   └── text_config.yaml             # 文本配置示例（教学用）
│
├── prompts/                         # LLM 提示词模板目录
│   ├── extend_keywords_for_column_recall.prompt   # 字段召回关键词扩展
│   ├── extend_keywords_for_metric_recall.prompt   # 指标召回关键词扩展
│   ├── extend_keywords_for_value_recall.prompt    # 取值召回关键词扩展
│   ├── filter_table_info.prompt      # 过滤表/字段
│   ├── filter_metric_info.prompt     # 过滤指标
│   ├── generate_sql.prompt           # 生成 SQL
│   └── correct_sql.prompt            # 校正 SQL
│
├── app/                             # 应用主包
│   ├── __init__.py
│   │
│   ├── conf/                        # 配置加载模块
│   │   ├── app_config.py            # 应用配置加载器（OmegaConf + dataclass）
│   │   ├── meta_config.py           # 元数据配置 dataclass 定义
│   │   └── text_config.py           # 文本配置加载器（教学示例）
│   │
│   ├── core/                        # 核心基础设施
│   │   ├── __init__.py
│   │   ├── log.py                   # 日志系统（loguru）
│   │   └── context.py               # 请求上下文变量（ContextVar）
│   │
│   ├── clients/                     # 外部服务客户端管理器
│   │   ├── mysql_client_manager.py
│   │   ├── es_client_manager.py
│   │   ├── qdrant_client_manager.py
│   │   └── embedding_client_manager.py
│   │
│   ├── models/                      # ORM 数据模型（对应 meta 库）
│   │   ├── base.py
│   │   ├── table_info_mysql.py
│   │   ├── column_info_mysql.py
│   │   ├── metric_info_mysql.py
│   │   └── column_metric_mysql.py
│   │
│   ├── entities/                    # 业务实体（dataclass）
│   │   ├── table_info.py
│   │   ├── column_info.py
│   │   ├── metric_info.py
│   │   ├── column_metric.py
│   │   └── value_info.py
│   │
│   ├── mappers/                     # entity ↔ model 映射器
│   │   ├── table_info_mapper.py
│   │   ├── column_info_mapper.py
│   │   ├── metric_info_mapper.py
│   │   └── column_metric_mapper.py
│   │
│   ├── repositories/                # 持久层
│   │   ├── es/
│   │   │   └── value_es_repository.py
│   │   ├── mysql/
│   │   │   ├── dw/
│   │   │   │   └── dw_mysql_repository.py
│   │   │   └── meta/
│   │   │       └── meta_mysql_repository.py
│   │   └── qdrant/
│   │       ├── column_qdrant_repository.py
│   │       └── metric_qdrant_repository.py
│   │
│   ├── services/                    # 业务服务层
│   │   └── meta_knowledge_service.py
│   │
│   ├── prompt/                      # 提示词加载器
│   │   └── prompt_loader.py
│   │
│   ├── agent/                       # 智能体工作流（LangGraph）
│   │   ├── graph.py                 # 图定义（节点 + 边）
│   │   ├── state.py                 # 工作流状态定义
│   │   ├── context.py               # 运行时上下文定义
│   │   ├── llm.py                   # LLM 客户端实例
│   │   └── nodes/                   # 工作流节点
│   │       ├── extract_keywords.py
│   │       ├── recall_column.py
│   │       ├── recall_metric.py
│   │       ├── recall_value.py
│   │       ├── merge_retrieved_info.py
│   │       ├── filter_table.py
│   │       ├── filter_metric.py
│   │       ├── add_extra_context.py
│   │       ├── generate_sql.py
│   │       ├── validate_sql.py
│   │       ├── correct_sql.py
│   │       └── execute_sql.py
│   │
│   └── scripts/                     # 运维脚本
│       └── build_meta_knowledge.py  # 元数据知识库构建脚本
│
├── test/
│   └── my_graph.mmd                 # 工作流 Mermaid 图（自动生成）
│
└── 笔记/                             # 课程资料（非代码）
    ├── 尚硅谷大模型项目之掌柜问数.md
    ├── 4.SQL脚本/
    │   ├── meta-schema.sql          # 元数据库建表 DDL
    │   ├── meta-schema-data.sql     # 元数据库初始数据
    │   ├── dw-schema.sql            # 数仓建表 DDL
    │   └── dw-schema-data.sql       # 数仓初始数据
    └── *.drawio / *.png             # 架构图
```

---

## 4. 配置系统

### 4.1 设计模式

配置系统采用 **OmegaConf + Python dataclass** 组合模式，实现类型安全的配置管理：

1. 从 YAML 文件加载原始配置 (`OmegaConf.load`)
2. 从 dataclass 生成结构化 Schema (`OmegaConf.structured`)
3. 合并两者，转换为强类型 dataclass 对象 (`OmegaConf.to_object`)

### 4.2 应用配置 (`app/conf/app_config.py`)

对应文件 `conf/app_config.yaml`。

| 配置类 | 对应 YAML Key | 字段 | 说明 |
|--------|---------------|------|------|
| `File` | `logging.file` | `enable`, `level`, `path`, `rotation`, `retention` | 文件日志配置 |
| `Console` | `logging.console` | `enable`, `level` | 控制台日志配置 |
| `LoggingConfig` | `logging` | `file: File`, `console: Console` | 日志总配置 |
| `DBConfig` | `db_meta` / `db_dw` | `host`, `port`, `user`, `password`, `database` | 数据库连接配置 |
| `QdrantConfig` | `qdrant` | `host`, `port`, `embedding_size` | Qdrant 向量库配置 |
| `EmbeddingConfig` | `embedding` | `host`, `port`, `model` | Embedding 服务配置 |
| `ESConfig` | `es` | `host`, `port`, `index_name` | Elasticsearch 配置 |
| `LLMConfig` | `llm` | `model_name`, `api_key` | 大模型配置 |
| `AppConfig` | 根节点 | 聚合以上所有配置 | 应用总配置 |

**全局实例**（模块加载时自动实例化）：

```python
app_config: AppConfig = OmegaConf.to_object(OmegaConf.merge(structured, context))
```

所有模块通过 `from app.conf.app_config import app_config` 获取全局唯一配置实例。

### 4.3 元数据配置 (`app/conf/meta_config.py`)

对应文件 `conf/meta_config.yaml`。用于离线构建知识库时，描述需要同步的表/字段/指标人工元信息。

| 配置类 | 字段 | 说明 |
|--------|------|------|
| `ColumnConfig` | `name`, `role`, `description`, `alias`, `sync` | 字段配置（`sync` 控制枚举值是否入 ES） |
| `TableConfig` | `name`, `role`, `description`, `columns` | 表配置 |
| `MetricConfig` | `name`, `description`, `relevant_columns`, `alias` | 指标配置 |
| `MetaConfig` | `tables`, `metrics` | 元数据根配置 |

`conf/meta_config.yaml` 示例结构（包含 5 张表：`dim_region`/`dim_customer`/`dim_product`/`dim_date`/`fact_order`，2 个指标：`GMV`/`AOV`）。

### 4.4 应用配置文件 (`conf/app_config.yaml`)

```yaml
logging:
  file:    { enable: true, level: INFO, path: logs, rotation: "10 MB", retention: "7 days" }
  console: { enable: true, level: INFO }

db_meta:  { host: 192.168.200.10, port: 3306, user: atguigu, password: Atguigu.123, database: meta }
db_dw:    { host: 192.168.200.10, port: 3306, user: atguigu, password: Atguigu.123, database: dw }
qdrant:   { host: 192.168.200.10, port: 6333, embedding_size: 1024 }
embedding:{ host: 192.168.200.10, port: 8081, model: BAAI/bge-large-zh-v1.5 }
es:       { host: 192.168.200.10, port: 9200, index_name: data_agent }
llm:      { model_name: deepseek-v4-pro, api_key: <deepseek_api_key> }
```

---

## 5. 核心基础设施 (`app/core/`)

### 5.1 日志系统 (`app/core/log.py`)

**核心依赖**: `loguru`

**功能说明**:
- 移除 loguru 默认 handler，使用自定义格式
- 通过 `logger.patch(inject_request_id)` 为每条日志注入 `request_id`（来自 ContextVar）
- 支持双通道输出：控制台 + 文件
- 文件日志输出到项目根目录 `logs/app.log`，支持自动轮转（rotation）和保留策略（retention）

**关键函数**:

| 函数 | 说明 |
|------|------|
| `inject_request_id(record)` | 从 `request_id_ctx_var` 获取当前请求 ID 并注入到 log record 的 extra 字段 |

**日志格式**:
```
2026-06-21 12:00:00.000 | INFO     | request_id - request-1 | module:function:line - message
```

**全局 logger 实例**: 通过 `from app.core.log import logger` 导入使用。

---

### 5.2 上下文变量 (`app/core/context.py`)

**核心依赖**: `contextvars.ContextVar`

定义异步安全的请求上下文变量 `request_id_ctx_var`，用于在异步/多请求场景下追踪每个请求的唯一标识。

```python
request_id_ctx_var = ContextVar("request_id", default=1)
```

该变量在日志系统（`log.py`）中被自动消费，实现请求级别的日志追踪。

---

## 6. 客户端管理器 (`app/clients/`)

所有客户端管理器遵循统一设计模式：
- 构造函数接收配置对象
- 提供 `init()` 方法初始化连接
- 支持 `close()` 方法释放资源
- 模块级全局单例实例

### 6.1 MySQL 客户端管理器 (`mysql_client_manager.py`)

**类**: `MysqlClientManager`  **核心依赖**: `sqlalchemy[asyncio]`, `asyncmy`

| 成员 | 类型 | 说明 |
|------|------|------|
| `db_config` | `DBConfig` | 数据库连接配置 |
| `engine` | `AsyncEngine` | SQLAlchemy 异步引擎，内置连接池（pool_size=10） |
| `session_factory` | `async_sessionmaker` | 异步 Session 工厂（autoflush=False, expire_on_commit=False） |

**关键方法**:

| 方法 | 说明 |
|------|------|
| `_get_url()` | 构建 `mysql+asyncmy://` 连接字符串 |
| `init()` | 创建 `AsyncEngine` 和 `async_sessionmaker` |
| `close()` | 释放引擎连接池 |

**全局实例**:
- `dw_mysql_client_manager` — 连接数仓数据库（dw）
- `meta_mysql_client_manager` — 连接元数据库（meta）

---

### 6.2 Elasticsearch 客户端管理器 (`es_client_manager.py`)

**类**: `ESClientManager`  **核心依赖**: `elasticsearch[async]`

| 成员 | 类型 | 说明 |
|------|------|------|
| `config` | `ESConfig` | ES 连接配置 |
| `client` | `AsyncElasticsearch` | ES 异步客户端（timeout=600） |

**全局实例**: `es_client_manager`

**主要功能**: 提供索引管理（创建/删除索引）、文档 CRUD（index/bulk）、全文检索等能力。支持 IK 中文分词器。

---

### 6.3 Qdrant 向量数据库客户端管理器 (`qdrant_client_manager.py`)

**类**: `QdrantClientManager`  **核心依赖**: `qdrant-client`

| 成员 | 类型 | 说明 |
|------|------|------|
| `config` | `QdrantConfig` | Qdrant 连接配置 |
| `client` | `AsyncQdrantClient` | Qdrant 异步客户端 |

**全局实例**: `qdrant_client_manager`

**主要功能**:
- 集合管理：创建/删除集合，配置向量维度（1024）和距离算法（Cosine）
- 向量写入：`upsert` 批量写入 `PointStruct`（id + vector + payload）
- 语义检索：`query_points` 支持相似度阈值过滤（score_threshold）和条件过滤（Filter）

---

### 6.4 Embedding 客户端管理器 (`embedding_client_manager.py`)

**类**: `EmbeddingClientManager`  **核心依赖**: `langchain-huggingface`

| 成员 | 类型 | 说明 |
|------|------|------|
| `config` | `EmbeddingConfig` | Embedding 服务配置 |
| `client` | `HuggingFaceEndpointEmbeddings` | HuggingFace 远程 Embedding 客户端 |

**全局实例**: `embedding_client_manager`

**主要功能**:
- 同步/异步单条向量化：`embed_query` / `aembed_query`
- 同步/异步批量向量化：`embed_documents` / `aembed_documents`

**模型**: `BAAI/bge-large-zh-v1.5`（1024 维中文向量）

---

## 7. 数据模型层 (`app/models/`)

所有模型基于 SQLAlchemy 2.0 声明式映射风格，继承自 `Base`（`DeclarativeBase`），对应元数据库（meta）中的表。

### 7.1 基类 (`base.py`)

```python
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass
```

### 7.2 模型清单

| 模型类 | 表名 | 用途 | 主要字段 |
|--------|------|------|----------|
| `TableInfoMySQL` | `table_info` | 表元数据 | `id`(PK), `name`, `role`(fact/dim), `description` |
| `ColumnInfoMySQL` | `column_info` | 字段元数据 | `id`(PK), `name`, `type`, `role`(primary_key/foreign_key/measure/dimension), `examples`(JSON), `description`, `alias`(JSON), `table_id` |
| `MetricInfoMySQL` | `metric_info` | 指标元数据 | `id`(PK), `name`, `description`, `relevant_columns`(JSON), `alias`(JSON) |
| `ColumnMetricMySQL` | `column_metric` | 字段-指标关联 | `column_id`(PK), `metric_id`(PK) 联合主键 |

### 7.3 实体关系图（ER）

```
table_info (表信息)
    │
    │ 1:N
    ▼
column_info (列信息) ──N:M── column_metric ──N:M── metric_info (指标信息)
```

---

## 8. 业务实体层 (`app/entities/`)

纯数据业务对象（`dataclass`），与 ORM 模型解耦，供业务层/持久层/向量库通用使用。

| 实体类 | 字段 | 说明 |
|--------|------|------|
| `TableInfo` | `id`, `name`, `role`, `description` | 表信息业务对象 |
| `ColumnInfo` | `id`, `name`, `type`, `role`, `examples`, `description`, `alias`, `table_id` | 字段信息业务对象 |
| `MetricInfo` | `id`, `name`, `description`, `relevant_columns`, `alias` | 指标信息业务对象 |
| `ColumnMetric` | `column_id`, `metric_id` | 字段-指标关系业务对象 |
| `ValueInfo` | `id`, `value`, `column_id` | 字段取值文档对象（存入 ES） |

---

## 9. 对象映射层 (`app/mappers/`)

负责业务实体（entity）与 ORM 模型（model）之间的双向转换。每个 Mapper 提供两个静态方法：

| Mapper 类 | `to_entity` | `to_model` |
|-----------|-------------|------------|
| `TableInfoMapper` | `TableInfoMySQL` → `TableInfo` | `TableInfo` → `TableInfoMySQL` |
| `ColumnInfoMapper` | `ColumnInfoMySQL` → `ColumnInfo` | `ColumnInfo` → `ColumnInfoMySQL` |
| `MetricInfoMapper` | `MetricInfoMySQL` → `MetricInfo` | `MetricInfo` → `MetricInfoMySQL` |
| `ColumnMetricMapper` | `ColumnMetricMySQL` → `ColumnMetric` | `ColumnMetric` → `ColumnMetricMySQL` |

> `to_entity` 采用手动赋值；`to_model` 采用 `dataclasses.asdict` 解包构造。

---

## 10. 持久层 (`app/repositories/`)

屏蔽底层存储细节，向上层提供领域化 API。按存储类型组织。

### 10.1 MySQL 持久层

#### `MetaMySQLRepository` (`repositories/mysql/meta/meta_mysql_repository.py`)

与元数据库（meta）交互，必须通过 `AsyncSession` 进行 CRUD。

| 方法 | 说明 |
|------|------|
| `save_table_infos(table_infos)` | 批量保存表信息（entity → model 转换后 `add_all`） |
| `save_column_infos(column_infos)` | 批量保存字段信息 |
| `save_metric_info_to_meta_db(metric_infos)` | 批量保存指标信息 |
| `save_column_metric_info_to_meta_db(column_metrics)` | 批量保存字段-指标关系 |

#### `DWMySQLRepository` (`repositories/mysql/dw/dw_mysql_repository.py`)

与数仓（dw）交互，通过原生 SQL 查询数仓元信息。

| 方法 | 说明 |
|------|------|
| `get_column_type_by_table_id(table_id)` | `show columns from <table>`，返回 `{字段名: 数据类型}` |
| `get_column_values_by_table_id(table_id, column_name, limit=10)` | `SELECT distinct <col> from <table> limit <n>`，返回字段取值列表 |

---

### 10.2 Qdrant 向量库持久层

#### `ColumnQdrantRepository` (`repositories/qdrant/column_qdrant_repository.py`)

操作字段向量集合，**集合名**: `data-agent-column`。

| 方法 | 说明 |
|------|------|
| `ensure_collection()` | 确保集合存在（维度 1024，Cosine 距离） |
| `upsert(ids, embeddings, payloads, batch_size=10)` | 分批 upsert 向量点（id + vector + payload） |
| `search(embedding, score_threshold=0.6, limit=10)` | 语义检索，返回 `list[ColumnInfo]`（payload 解构为实体） |

#### `MetricQdrantRepository` (`repositories/qdrant/metric_qdrant_repository.py`)

操作指标向量集合，**集合名**: `data-agent-metric`。

| 方法 | 说明 |
|------|------|
| `ensure_collection()` | 确保集合存在 |
| `upsert(ids, embeddings, payloads, batch_size=10)` | 分批 upsert 指标向量点 |

---

### 10.3 Elasticsearch 持久层

#### `ValueESRepository` (`repositories/es/value_es_repository.py`)

操作字段取值全文索引，**索引名**: `data-agent-column`。

**索引 Mapping**（IK 中文分词）:
```python
{
  "dynamic": False,
  "properties": {
    "id":        {"type": "keyword"},
    "value":     {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word"},
    "column_id": {"type": "keyword"}
  }
}
```

| 方法 | 说明 |
|------|------|
| `ensure_index()` | 确保索引存在 |
| `upsert(value_infos, batch_size=10)` | 分批 bulk 写入文档（`_id` = `value_info.id`） |

---

## 11. 业务服务层 (`app/services/`)

### `MetaKnowledgeService` (`services/meta_knowledge_service.py`)

**职责**: 元数据知识库构建的业务编排，将人工配置的元信息同步到三类存储（MySQL meta、Qdrant、ES）。

**依赖注入**（构造函数）:
`meta_mysql_repository`, `dw_mysql_repository`, `column_qdrant_repository`, `embedding_client`, `value_es_repository`, `metric_qdrant_repository`

**核心方法 `build(meta_config_path)`** 流程：

1. 通过 OmegaConf 读取 `meta_config.yaml` 并转为 `MetaConfig` 对象
2. **处理表信息**（`if meta_config.tables`）：
   - `_save_table_info_to_meta_db()` — 从 DW 查询字段类型与示例值，构建 `TableInfo`/`ColumnInfo`，事务内批量写入 meta 库
   - `_save_column_info_to_qdrant()` — 为字段名/描述/别名分别生成向量点，批量 upsert 到 Qdrant
   - `_save_value_info_to_es()` — 对 `sync=true` 的字段查询枚举值（limit=100000），构建 `ValueInfo` 写入 ES
3. **处理指标信息**（`if meta_config.metrics`）：
   - `_save_metric_info_to_meta_db()` — 构建 `MetricInfo`/`ColumnMetric`，事务内批量写入 meta 库
   - `_save_metric_info_to_qdrant()` — 为指标名/描述/别名生成向量点，批量 upsert 到 Qdrant

**向量化批次**: `batch_size=10`，使用 `embedding_client.aembed_documents`。

---

## 12. 提示词系统 (`app/prompt/` + `prompts/`)

### 12.1 提示词加载器 (`app/prompt/prompt_loader.py`)

```python
def load_prompt(prompt_name: str) -> str:
    prompt_path = Path(__file__).parents[2] / 'prompts' / f"{prompt_name}.prompt"
    return prompt_path.read_text(encoding="utf-8")
```

按名称从 `prompts/` 目录加载 `.prompt` 文本文件。

### 12.2 提示词模板清单

| 模板文件 | 输入变量 | 用途 |
|---------|----------|------|
| `extend_keywords_for_column_recall.prompt` | `{query}` | 字段召回：LLM 推断回答问题所必需的字段名列表（JSON 数组） |
| `extend_keywords_for_metric_recall.prompt` | `{query}` | 指标召回：LLM 生成指标检索关键词（JSON 数组） |
| `extend_keywords_for_value_recall.prompt` | `{query}` | 取值召回：LLM 生成字段取值候选（JSON 数组） |
| `filter_table_info.prompt` | `{query}`, `{table_infos}` | 过滤表：从候选表中裁剪出必需的表与字段（JSON 对象） |
| `filter_metric_info.prompt` | `{query}`, `{metric_infos}` | 过滤指标：从候选指标中筛选必需指标（JSON 数组，可为空） |
| `generate_sql.prompt` | `{query}`, `{table_infos}`, `{metric_infos}`, `{date_info}`, `{db_info}` | 生成 SQL：自然语言 → SQL 纯文本 |
| `correct_sql.prompt` | `{query}`, `{table_infos}`, `{metric_infos}`, `{date_info}`, `{db_info}`, `{sql}`, `{error}` | 校正 SQL：基于错误信息最小修复 SQL |

---

## 13. 智能体工作流 (`app/agent/`)

### 13.1 状态定义 (`state.py`)

```python
class DataAgentState(TypedDict):
    query: str                              # 用户原始问题
    keywords: list[str]                     # 抽取关键字节点结果
    retrieved_columns: list[ColumnInfo]     # 召回字段节点结果
    error: str                              # 校验SQL节点 SQL错误信息（None 表示无错误）
```

### 13.2 运行时上下文 (`context.py`)

```python
class DataAgentContext(TypedDict):
    """runtime context 数据结构,存放静态依赖：操作不同库持久层对象（对节点而言只读）"""
    meta_mysql_repository: MetaMySQLRepository
    dw_mysql_repository: DWMySQLRepository
    embedding_client: HuggingFaceEndpointEmbeddings
    column_qdrant_repository: ColumnQdrantRepository
    metric_qdrant_repository: MetricQdrantRepository
    value_es_repository: ValueESRepository
```

> `State` 为节点可读写的流转数据；`Context` 为整个工作流运行期间只读的静态依赖注入对象。

### 13.3 LLM 实例 (`llm.py`)

```python
from langchain.chat_models import init_chat_model
llm = init_chat_model(
    model=app_config.llm.model_name,   # deepseek-v4-pro
    api_key=app_config.llm.api_key,
    temperature=0
)
```

通过 `langchain` 的 `init_chat_model` 统一初始化 DeepSeek LLM（温度 0 保证稳定输出）。

### 13.4 图定义 (`graph.py`)

使用 `langgraph.graph.StateGraph` 构建，`state_schema=DataAgentState`，`context_schema=DataAgentContext`。

**节点注册（12 个）：**

| 节点名 | 节点函数 | 说明 |
|--------|----------|------|
| `extract_keywords` | `extract_keywords` | 入口节点，jieba 抽取关键词 |
| `recall_column` | `recall_column` | 字段向量召回 |
| `recall_metric` | `recall_metric` | 指标向量召回 |
| `recall_value` | `recall_value` | 取值全文召回 |
| `merge_retrieved_info` | `merge_retrieved_info` | 合并召回信息 |
| `filter_table` | `filter_table` | 过滤表/字段 |
| `filter_metric` | `filter_metric` | 过滤指标 |
| `add_extra_context` | `add_extra_context` | 补充上下文 |
| `generate_sql` | `generate_sql` | LLM 生成 SQL |
| `validate_sql` | `validate_sql` | 校验 SQL |
| `correct_sql` | `correct_sql` | LLM 校正 SQL |
| `execute_sql` | `execute_sql` | 执行 SQL |

**边定义：**

```python
START → extract_keywords
extract_keywords → recall_column   (并行 fan-out)
extract_keywords → recall_metric
extract_keywords → recall_value
recall_column   ↘
recall_metric   → merge_retrieved_info   (fan-in)
recall_value    ↗
merge_retrieved_info → filter_table      (并行)
merge_retrieved_info → filter_metric
filter_table   ↘
                 → add_extra_context     (fan-in)
filter_metric  ↗
add_extra_context → generate_sql → validate_sql
validate_sql --(条件边)--> execute_sql      # error 为 None
validate_sql --(条件边)--> correct_sql      # error 有值
correct_sql → execute_sql
execute_sql → END
```

**条件边逻辑：**
```python
lambda state: "execute_sql" if state["error"] is None else "correct_sql"
```

**编译与调用：**
```python
graph = graph_builder.compile()
# 流式调用（自定义数据）
async for chunk in graph.astream(input=state, context=context, stream_mode="custom"):
    print(chunk)
```

### 13.5 节点实现详情 (`app/agent/nodes/`)

所有节点为 `async` 函数，签名统一为 `async def node(state: DataAgentState, runtime: Runtime[DataAgentContext])`，通过 `get_stream_writer()` 或 `runtime.stream_writer` 推送进度（`{"type":"progress","step":"...","status":"running|success|error"}`）。

| 节点 | 实现状态 | 关键逻辑 |
|------|----------|----------|
| `extract_keywords` | ✅ 已实现 | jieba.analyse.extract_tags（topK=10，限定词性 n/nr/ns/nt/nz/v/vn/a/an/eng/i/l），与原 query 拼接去重 |
| `recall_column` | ✅ 已实现 | LLM(`extend_keywords_for_column_recall`) 扩展关键词 → 与 jieba 关键词去重合并 → 逐词 `aembed_query` → Qdrant `search`(score_threshold=0.6) → 按 id 去重 → 返回 `retrieved_columns` |
| `recall_metric` | 🚧 骨架 | 仅推送进度，待实现 |
| `recall_value` | 🚧 骨架 | 仅推送进度，待实现 |
| `merge_retrieved_info` | 🚧 骨架 | 仅打印 state，待实现 |
| `filter_table` | 🚧 骨架 | 仅推送进度，待实现 |
| `filter_metric` | 🚧 骨架 | 仅推送进度，待实现 |
| `add_extra_context` | 🚧 骨架 | 仅推送进度，待实现 |
| `generate_sql` | 🚧 骨架 | 仅推送进度，待实现 |
| `validate_sql` | 🚧 骨架 | 直接 `return {"error": None}`，待实现 |
| `correct_sql` | 🚧 骨架 | 仅推送进度，待实现 |
| `execute_sql` | 🚧 骨架 | 仅推送进度，待实现 |

**`recall_column` 节点链式调用示例（LangChain LCEL）：**
```python
prompt = PromptTemplate(template=load_prompt("extend_keywords_for_column_recall"), input_variables=["query"])
output = JsonOutputParser()
chain = prompt | llm | output
result = await chain.ainvoke({"query": query})
```

### 13.6 流式输出模式

`graph.astream` 支持 `stream_mode`：
- `values` — 每个节点输出 state 全部数据
- `updates` — 每个节点 state 被更新的字段
- `custom` — 节点通过 `stream_writer` 写入的自定义数据（进度推送）

---

## 14. 脚本与工具 (`app/scripts/`)

### `build_meta_knowledge.py`

**用途**: 离线构建元数据知识库的命令行入口。

**使用方式**:
```bash
python -m app.scripts.build_meta_knowledge -c <meta_config.yaml 路径>
```

**流程（`build(meta_config_path)`）：**
1. 初始化所有客户端管理器（dw / meta / qdrant / embedding / es）
2. 通过 `session_factory` 创建 dw / meta Session
3. 实例化各持久层对象，注入 `MetaKnowledgeService`
4. 调用 `meta_knowledge_service.build(meta_config_path)`
5. 关闭所有连接

**参数解析**: 使用 `argparse`，`-c/--conf` 指定元数据配置文件路径。

---

## 15. 依赖关系

### 15.1 外部依赖 (`pyproject.toml`)

| 包名 | 版本 | 用途 |
|------|------|------|
| `fastapi[standard]` | 0.128.0 | Web 框架（预留） |
| `sqlalchemy` | 2.0.46 | 异步 ORM |
| `asyncmy` | 0.2.11 | MySQL 异步驱动 |
| `elasticsearch[async]` | >=8,<9 | ES 异步客户端 |
| `qdrant-client` | 1.16.2 | Qdrant 向量库客户端 |
| `langchain` | 1.2.7 | LLM 应用框架 |
| `langchain-deepseek` | 1.0.1 | DeepSeek LLM 集成 |
| `langchain-huggingface` | 1.2.1 | HuggingFace Embedding 集成 |
| `langgraph` | 1.0.7 | LLM 工作流编排 |
| `huggingface-hub` | 0.36.0 | HuggingFace 模型 Hub |
| `loguru` | 0.7.3 | 日志库 |
| `omegaconf` | 2.3.0 | 配置管理 |
| `pyyaml` | 6.0.3 | YAML 解析 |
| `jieba` | 0.42.1 | 中文分词 |
| `cryptography` | 46.0.4 | 加密支持 |

### 15.2 模块依赖关系图

```
app/conf/app_config.py ◄── 几乎所有模块（全局配置）
app/conf/meta_config.py ◄── app/services/meta_knowledge_service.py
app/core/context.py    ◄── app/core/log.py
app/core/log.py        ◄── 所有业务模块（日志）

app/clients/*
  ├─ mysql_client_manager      ◄── app/agent/graph.py, app/scripts/build_meta_knowledge.py
  ├─ es_client_manager         ◄── app/agent/graph.py, app/scripts/build_meta_knowledge.py
  ├─ qdrant_client_manager     ◄── app/agent/graph.py, app/scripts/build_meta_knowledge.py
  └─ embedding_client_manager  ◄── app/agent/graph.py, app/scripts/build_meta_knowledge.py

app/models/base.py ◄── app/models/{table,column,metric,column_metric}_info_mysql.py
app/entities/*     ◄── app/repositories/*, app/services/*, app/agent/*

app/mappers/*       ◄── app/repositories/mysql/meta/meta_mysql_repository.py
app/repositories/*  ◄── app/services/meta_knowledge_service.py, app/agent/context.py

app/prompt/prompt_loader.py ◄── app/agent/nodes/recall_column.py（及待实现节点）
app/agent/llm.py           ◄── app/agent/nodes/recall_column.py（及待实现节点）
app/agent/{state,context}  ◄── app/agent/nodes/*, app/agent/graph.py
app/agent/nodes/*          ◄── app/agent/graph.py
```

### 15.3 智能体工作流依赖注入

`graph.py` 在运行时通过 `DataAgentContext` 向所有节点注入只读依赖：

```python
context = DataAgentContext(
    meta_mysql_repository=MetaMySQLRepository(meta_session),
    dw_mysql_repository=DWMySQLRepository(dw_session),
    embedding_client=embedding_client_manager.client,
    column_qdrant_repository=ColumnQdrantRepository(qdrant_client_manager.client),
    metric_qdrant_repository=MetricQdrantRepository(qdrant_client_manager.client),
    value_es_repository=ValueESRepository(es_client_manager.client)
)
async for chunk in graph.astream(input=state, context=context, stream_mode="custom"):
    ...
```

---

## 16. 项目运行方式

### 16.1 环境准备

```bash
# 1. 进入项目目录
cd sgg_data-agent

# 2. 安装依赖（使用 uv）
uv sync

# 3. 配置外部服务
#    编辑 conf/app_config.yaml，确保 MySQL / ES / Qdrant / Embedding / LLM 服务地址正确
#    注意：需要填写有效的 DeepSeek API Key
```

### 16.2 初始化数据库

```bash
# 在 MySQL 中执行建表脚本（meta 元数据库）
mysql -h 192.168.200.10 -u atguigu -p < 笔记/4.SQL脚本/meta-schema.sql
mysql -h 192.168.200.10 -u atguigu -p < 笔记/4.SQL脚本/meta-schema-data.sql

# 数仓数据库
mysql -h 192.168.200.10 -u atguigu -p < 笔记/4.SQL脚本/dw-schema.sql
mysql -h 192.168.200.10 -u atguigu -p < 笔记/4.SQL脚本/dw-schema-data.sql
```

### 16.3 构建元数据知识库（离线）

```bash
# 将 conf/meta_config.yaml 中的人工元信息同步到 MySQL meta / Qdrant / ES
python -m app.scripts.build_meta_knowledge -c conf/meta_config.yaml
```

### 16.4 运行问数智能体工作流（在线）

```bash
# 直接运行 graph.py 的测试入口（流式输出）
python -m app.agent.graph
```

测试入口会：
1. 初始化所有客户端管理器
2. 创建 dw / meta Session 与 `DataAgentContext`
3. 以 `query="华北地区去年卖了多少钱"` 为输入，`stream_mode="custom"` 流式执行
4. 关闭所有连接

### 16.5 单模块自测

```bash
python -m app.conf.app_config          # 测试配置加载
python -m app.core.log                 # 测试日志系统
python -m app.clients.mysql_client_manager   # 测试 MySQL 连接
python -m app.clients.es_client_manager      # 测试 ES 连接
python -m app.clients.qdrant_client_manager  # 测试 Qdrant 连接
python -m app.clients.embedding_client_manager # 测试 Embedding 服务
python -m app.prompt.prompt_loader      # 测试提示词加载
```

### 16.6 启动 FastAPI 服务（预留）

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> 当前 `main.py` 为 PyCharm 默认模板，FastAPI 路由与 HTTP 接入层待后续实现。问数能力目前通过 `app/agent/graph.py` 直接调用。

---

## 17. 附录：技术栈总览

| 类别 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | >= 3.12 |
| Web 框架 | FastAPI | 0.128.0（预留） |
| ORM | SQLAlchemy (async) | 2.0.46 |
| 关系数据库 | MySQL | - |
| 全文检索 | Elasticsearch | 8.x |
| 向量数据库 | Qdrant | 1.16.2 |
| Embedding 模型 | BAAI/bge-large-zh-v1.5 | 1024 维 |
| LLM 框架 | LangChain + LangGraph | 1.2.7 / 1.0.7 |
| LLM 模型 | DeepSeek V4 Pro | - |
| 配置管理 | OmegaConf | 2.3.0 |
| 日志 | Loguru | 0.7.3 |
| 中文分词 | Jieba | 0.42.1 |
| 包管理 | uv | - |

### 关键设计约定

1. **配置即 dataclass**：所有配置通过 OmegaConf + dataclass 强类型化，模块加载即实例化全局单例
2. **依赖注入**：持久层对象通过构造函数注入服务层 / Context，便于测试与解耦
3. **entity / model 分离**：业务实体（dataclass）与 ORM 模型分离，由 Mapper 层转换
4. **State / Context 分离**：LangGraph 工作流中 State 为流转数据（可读写），Context 为运行时静态依赖（只读）
5. **流式进度推送**：节点统一通过 `stream_writer` 推送 `{type, step, status}` 进度，前端可消费 `stream_mode="custom"`
6. **异步优先**：所有 I/O（DB / ES / Qdrant / Embedding / LLM）均采用 async 接口
