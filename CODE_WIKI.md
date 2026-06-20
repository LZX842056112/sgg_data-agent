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
5. [核心模块](#5-核心模块)
   - [5.1 日志系统 (`app/core/log.py`)](#51-日志系统-appcorelogpy)
   - [5.2 上下文变量 (`app/core/context.py`)](#52-上下文变量-appcorecontextpy)
6. [客户端管理器 (`app/clients/`)](#6-客户端管理器-appclients)
   - [6.1 MySQL 客户端管理器](#61-mysql-客户端管理器)
   - [6.2 Elasticsearch 客户端管理器](#62-elasticsearch-客户端管理器)
   - [6.3 Qdrant 向量数据库客户端管理器](#63-qdrant-向量数据库客户端管理器)
   - [6.4 Embedding 客户端管理器](#64-embedding-客户端管理器)
7. [数据模型 (`app/models/`)](#7-数据模型-appmodels)
8. [脚本与工具 (`app/scripts/`)](#8-脚本与工具-appscripts)
9. [依赖关系图](#9-依赖关系图)
10. [项目运行方式](#10-项目运行方式)

---

## 1. 项目概述

`data-agent` 是 **尚硅谷大模型项目之掌柜问数** 的后端数据智能体服务。该项目面向企业数仓场景，结合大模型（LLM）、向量检索、全文检索等技术，实现自然语言到 SQL 的智能转换与数据查询。

**核心能力：**
- 连接 MySQL 数仓（dw）与元数据库（meta），管理表/字段/指标元数据
- 集成 Elasticsearch 提供全文检索能力
- 集成 Qdrant 向量数据库 + HuggingFace Embedding 模型实现语义检索
- 基于 LangChain / LangGraph 构建 LLM 工作流
- 集成 DeepSeek 大模型进行自然语言理解与 SQL 生成

**涉及的外部服务（均部署于 `192.168.200.10`）：**

| 服务 | 端口 | 用途 |
|------|------|------|
| MySQL (meta) | 3306 | 元数据存储（表、字段、指标信息） |
| MySQL (dw) | 3306 | 数仓数据存储 |
| Elasticsearch | 9200 | 全文检索 |
| Qdrant | 6333 | 向量语义检索 |
| Embedding Service | 8081 | 文本向量化（BAAI/bge-large-zh-v1.5） |
| DeepSeek LLM | API | 大模型推理 |

---

## 2. 整体架构

```
┌─────────────────────────────────────────────────────┐
│                     main.py                          │
│                  (FastAPI 入口)                       │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│                  app/conf/                            │
│   ┌──────────────┐     ┌───────────────┐             │
│   │ app_config   │     │ text_config   │             │
│   │ (OmegaConf + │     │               │             │
│   │  dataclass)  │     │               │             │
│   └──────────────┘     └───────────────┘             │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│                  app/core/                            │
│   ┌──────────────┐     ┌───────────────┐             │
│   │    log.py     │     │  context.py   │             │
│   │ (loguru日志)  │     │ (ContextVar)  │             │
│   └──────────────┘     └───────────────┘             │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│                app/clients/                           │
│   ┌─────────────────────────────────────────────┐    │
│   │  MySQL Client Manager (dw / meta)            │    │
│   │  Elasticsearch Client Manager                │    │
│   │  Qdrant Client Manager                      │    │
│   │  Embedding Client Manager                   │    │
│   └─────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│                app/models/                            │
│   ┌─────────────────────────────────────────────┐    │
│   │  ColumnInfoMySQL  /  TableInfoMySQL          │    │
│   │  MetricInfoMySQL  /  ColumnMetricMySQL       │    │
│   └─────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│              app/scripts/                             │
│   ┌─────────────────────────────────────────────┐    │
│   │  build_meta_knowledge.py                     │    │
│   └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

**分层架构说明：**

| 层级 | 目录 | 职责 |
|------|------|------|
| 入口层 | `main.py` | FastAPI 应用入口，路由注册 |
| 配置层 | `app/conf/` | 统一配置管理，支持 YAML + dataclass 结构化 |
| 核心层 | `app/core/` | 日志系统、请求上下文变量 |
| 客户端层 | `app/clients/` | 外部服务连接管理（MySQL / ES / Qdrant / Embedding） |
| 模型层 | `app/models/` | 元数据库 ORM 模型定义 |
| 脚本层 | `app/scripts/` | 数据构建/知识库初始化脚本 |

---

## 3. 目录结构

```
sgg_data-agent/
├── main.py                          # 应用入口（FastAPI 预留）
├── pyproject.toml                   # 项目元数据与依赖声明
├── uv.lock                          # uv 依赖锁定文件
├── README.md                        # 项目说明（空）
├── .gitignore
│
├── conf/                            # 配置文件目录
│   ├── app_config.yaml              # 应用主配置（数据库、ES、Qdrant、LLM等）
│   └── text_config.yaml             # 文本配置示例
│
├── app/                             # 应用主包
│   ├── __init__.py
│   │
│   ├── conf/                        # 配置加载模块
│   │   ├── app_config.py            # 应用配置加载器（OmegaConf）
│   │   └── text_config.py           # 文本配置加载器（示例）
│   │
│   ├── core/                        # 核心基础设施
│   │   ├── __init__.py
│   │   ├── log.py                   # 日志系统（loguru）
│   │   └── context.py               # 请求上下文变量（ContextVar）
│   │
│   ├── clients/                     # 外部服务客户端管理器
│   │   ├── mysql_client_manager.py   # MySQL 异步客户端
│   │   ├── es_client_manager.py      # Elasticsearch 异步客户端
│   │   ├── qdrant_client_manager.py  # Qdrant 向量数据库客户端
│   │   └── embedding_client_manager.py # HuggingFace Embedding 客户端
│   │
│   ├── models/                      # ORM 数据模型
│   │   ├── base.py                  # 声明式基类
│   │   ├── table_info_mysql.py      # 表信息模型
│   │   ├── column_info_mysql.py     # 列信息模型
│   │   ├── metric_info_mysql.py     # 指标信息模型
│   │   └── column_metric_mysql.py   # 列-指标关联模型
│   │
│   └── scripts/                     # 运维脚本
│       └── build_meta_knowledge.py  # 元数据知识库构建脚本
│
└── 笔记/                             # 课程资料（非代码）
    ├── 尚硅谷大模型项目之掌柜问数.md
    ├── Elasticsearch-随堂RestfulAPI.txt
    ├── *.html
    ├── *.drawio / *.png
    └── 4.SQL脚本/
        ├── meta-schema.sql          # 元数据库建表 DDL
        ├── meta-schema-data.sql     # 元数据库初始数据
        ├── dw-schema.sql            # 数仓建表 DDL
        └── dw-schema-data.sql       # 数仓初始数据
```

---

## 4. 配置系统

### 4.1 设计模式

配置系统采用 **OmegaConf + Python dataclass** 的组合模式，实现类型安全的配置管理：

1. 从 YAML 文件加载原始配置 (`OmegaConf.load`)
2. 从 dataclass 生成结构化 Schema (`OmegaConf.structured`)
3. 合并两者，转换为强类型 dataclass 对象 (`OmegaConf.to_object`)

### 4.2 配置类定义 (`app/conf/app_config.py`)

| 配置类 | 对应 YAML Key | 字段 | 说明 |
|--------|---------------|------|------|
| `LoggingConfig` | `logging` | `file: File`, `console: Console` | 日志配置（文件/控制台） |
| `File` | `logging.file` | `enable`, `level`, `path`, `rotation`, `retention` | 文件日志配置 |
| `Console` | `logging.console` | `enable`, `level` | 控制台日志配置 |
| `DBConfig` | `db_meta` / `db_dw` | `host`, `port`, `user`, `password`, `database` | 数据库连接配置 |
| `QdrantConfig` | `qdrant` | `host`, `port`, `embedding_size` | Qdrant 向量库配置 |
| `EmbeddingConfig` | `embedding` | `host`, `port`, `model` | Embedding 服务配置 |
| `ESConfig` | `es` | `host`, `port`, `index_name` | Elasticsearch 配置 |
| `LLMConfig` | `llm` | `model_name`, `api_key` | 大模型配置 |
| `AppConfig` | 根节点 | 聚合以上所有配置 | 应用总配置 |

### 4.3 全局配置实例

```python
# 在 app/conf/app_config.py 模块加载时自动实例化
app_config: AppConfig = OmegaConf.to_object(OmegaConf.merge(structured, context))
```

所有模块通过 `from app.conf.app_config import app_config` 获取全局唯一配置实例。

### 4.4 配置文件 (`conf/app_config.yaml`)

```yaml
logging:
  file:
    enable: true
    level: INFO
    path: logs
    rotation: "10 MB"
    retention: "7 days"
  console:
    enable: true
    level: INFO

db_meta:           # 元数据库连接
  host: 192.168.200.10
  port: 3306
  user: atguigu
  password: Atguigu.123
  database: meta

db_dw:             # 数仓数据库连接
  host: 192.168.200.10
  port: 3306
  user: atguigu
  password: Atguigu.123
  database: dw

qdrant:            # 向量数据库
  host: 192.168.200.10
  port: 6333
  embedding_size: 1024

embedding:         # 文本向量化服务
  host: 192.168.200.10
  port: 8081
  model: BAAI/bge-large-zh-v1.5

es:                # Elasticsearch 全文检索
  host: 192.168.200.10
  port: 9200
  index_name: data_agent

llm:               # 大模型配置
  model_name: deepseek-v4-pro
  api_key: <deepseek_api_key>
```

---

## 5. 核心模块

### 5.1 日志系统 (`app/core/log.py`)

**核心依赖**: `loguru`

**功能说明**:

- 移除 loguru 默认 handler，使用自定义格式
- 通过 `logger.patch(inject_request_id)` 为每条日志注入 `request_id`（来自 ContextVar）
- 支持双通道输出：控制台 + 文件
- 文件日志支持自动轮转（rotation）和保留策略（retention）

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

**功能说明**:

定义异步安全的请求上下文变量 `request_id_ctx_var`，用于在异步/多请求场景下追踪每个请求的唯一标识。

```python
request_id_ctx_var = ContextVar("request_id", default=1)
```

**使用方式**:
```python
from app.core.context import request_id_ctx_var

# 设置当前请求 ID
request_id_ctx_var.set("request-xxx")

# 获取当前请求 ID
req_id = request_id_ctx_var.get()
```

该变量在日志系统（`log.py`）中被自动消费，实现请求级别的日志追踪。

---

## 6. 客户端管理器 (`app/clients/`)

所有客户端管理器遵循统一设计模式：
- 构造函数接收配置对象
- 提供 `init()` 方法初始化连接
- 支持 `close()` 方法释放资源
- 模块级全局单例实例

### 6.1 MySQL 客户端管理器

**文件**: [app/clients/mysql_client_manager.py](file:///d:/Projects/SGG/sgg_data-agent/app/clients/mysql_client_manager.py)

**类**: `MysqlClientManager`

**核心依赖**: `sqlalchemy[asyncio]`, `asyncmy`

| 成员 | 类型 | 说明 |
|------|------|------|
| `db_config` | `DBConfig` | 数据库连接配置 |
| `engine` | `AsyncEngine` | SQLAlchemy 异步引擎，内置连接池（pool_size=10） |
| `session_factory` | `async_sessionmaker` | 异步 Session 工厂 |

**关键方法**:

| 方法 | 说明 |
|------|------|
| `_get_url()` | 构建 `mysql+asyncmy://` 连接字符串 |
| `init()` | 创建 `AsyncEngine` 和 `async_sessionmaker` |
| `close()` | 释放引擎连接池 |

**全局实例**:
- `dw_mysql_client_manager` — 连接数仓数据库（dw）
- `meta_mysql_client_manager` — 连接元数据库（meta）

**使用示例**:
```python
dw_mysql_client_manager.init()
async with dw_mysql_client_manager.session_factory() as session:
    result = await session.execute(text("show tables"))
    print(result.scalars().fetchall())
```

---

### 6.2 Elasticsearch 客户端管理器

**文件**: [app/clients/es_client_manager.py](file:///d:/Projects/SGG/sgg_data-agent/app/clients/es_client_manager.py)

**类**: `ESClientManager`

**核心依赖**: `elasticsearch[async]`

| 成员 | 类型 | 说明 |
|------|------|------|
| `config` | `ESConfig` | ES 连接配置 |
| `client` | `AsyncElasticsearch` | ES 异步客户端 |

**关键方法**:

| 方法 | 说明 |
|------|------|
| `_get_url()` | 构建 `http://host:port` 连接地址 |
| `init()` | 初始化 `AsyncElasticsearch` 客户端 |
| `close()` | 关闭客户端连接 |

**全局实例**: `es_client_manager`

**主要功能**: 提供索引管理（创建/删除索引）、文档 CRUD（index/bulk）、全文检索等能力。支持 IK 中文分词器。

---

### 6.3 Qdrant 向量数据库客户端管理器

**文件**: [app/clients/qdrant_client_manager.py](file:///d:/Projects/SGG/sgg_data-agent/app/clients/qdrant_client_manager.py)

**类**: `QdrantClientManager`

**核心依赖**: `qdrant-client`

| 成员 | 类型 | 说明 |
|------|------|------|
| `config` | `QdrantConfig` | Qdrant 连接配置 |
| `client` | `AsyncQdrantClient` | Qdrant 异步客户端 |

**关键方法**:

| 方法 | 说明 |
|------|------|
| `_get_url()` | 构建 `http://host:port` 连接地址 |
| `init()` | 初始化 `AsyncQdrantClient` |
| `close()` | 关闭客户端连接 |

**全局实例**: `qdrant_client_manager`

**主要功能**:
- 集合管理：创建/删除集合，配置向量维度（1024）和距离算法（Cosine）
- 向量写入：`upsert` 批量写入 `PointStruct`（id + vector + payload）
- 语义检索：`query_points` 支持相似度阈值过滤（score_threshold）和条件过滤（Filter）

**典型流程**:
```python
# 1. 向量化查询文本
embed_query = await embedding_client.aembed_query("西瓜")
# 2. 语义检索
result = await client.query_points(
    collection_name=coll_name,
    query=embed_query,
    limit=10,
    score_threshold=0.6,
)
```

---

### 6.4 Embedding 客户端管理器

**文件**: [app/clients/embedding_client_manager.py](file:///d:/Projects/SGG/sgg_data-agent/app/clients/embedding_client_manager.py)

**类**: `EmbeddingClientManager`

**核心依赖**: `langchain-huggingface`

| 成员 | 类型 | 说明 |
|------|------|------|
| `config` | `EmbeddingConfig` | Embedding 服务配置 |
| `client` | `HuggingFaceEndpointEmbeddings` | HuggingFace 远程 Embedding 客户端 |

**关键方法**:

| 方法 | 说明 |
|------|------|
| `_get_url()` | 构建 `http://host:port` 服务地址 |
| `init()` | 初始化 `HuggingFaceEndpointEmbeddings` |

**全局实例**: `embedding_client_manager`

**主要功能**:
- 同步单条向量化：`embed_query("你好")` → `List[float]`
- 同步批量向量化：`embed_documents(["你好", "世界"])` → `List[List[float]]`
- 异步单条向量化：`aembed_query("苹果")` → `List[float]`
- 异步批量向量化：`aembed_documents(["苹果", "香蕉"])` → `List[List[float]]`

**模型**: `BAAI/bge-large-zh-v1.5`（1024 维中文向量）

---

## 7. 数据模型 (`app/models/`)

所有模型均基于 SQLAlchemy 2.0 声明式映射风格，继承自 `Base`（`DeclarativeBase`），对应元数据库（meta）中的表。

### 7.1 基类 (`base.py`)

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

所有 ORM 模型的公共基类。

---

### 7.2 表信息模型 (`table_info_mysql.py`)

**类**: `TableInfoMySQL`  
**表名**: `table_info`  
**用途**: 存储数仓中所有表的元数据信息

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `String(64)`, PK | 表编号 |
| `name` | `String(128)`, nullable | 表名称 |
| `role` | `String(32)`, nullable | 表类型（fact 事实表 / dim 维度表） |
| `description` | `Text`, nullable | 表描述 |

---

### 7.3 列信息模型 (`column_info_mysql.py`)

**类**: `ColumnInfoMySQL`  
**表名**: `column_info`  
**用途**: 存储每个表的字段元数据信息

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `String(64)`, PK | 列编号 |
| `name` | `String(128)`, nullable | 列名称 |
| `type` | `String(64)`, nullable | 数据类型 |
| `role` | `String(32)`, nullable | 列角色（primary_key / foreign_key / measure / dimension） |
| `examples` | `JSON`, nullable | 数据示例 |
| `description` | `Text`, nullable | 列描述 |
| `alias` | `JSON`, nullable | 列别名（用于语义匹配） |
| `table_id` | `String(64)`, nullable | 所属表编号（关联 `table_info.id`） |

---

### 7.4 指标信息模型 (`metric_info_mysql.py`)

**类**: `MetricInfoMySQL`  
**表名**: `metric_info`  
**用途**: 存储业务指标元数据

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `String(64)`, PK | 指标编码 |
| `name` | `String(128)`, nullable | 指标名称 |
| `description` | `Text`, nullable | 指标描述 |
| `relevant_columns` | `JSON`, nullable | 关联字段列表 |
| `alias` | `JSON`, nullable | 指标别名 |

---

### 7.5 列-指标关联模型 (`column_metric_mysql.py`)

**类**: `ColumnMetricMySQL`  
**表名**: `column_metric`  
**用途**: 列与指标的多对多关联关系

| 字段 | 类型 | 说明 |
|------|------|------|
| `column_id` | `String(64)`, PK | 列编号（关联 `column_info.id`） |
| `metric_id` | `String(64)`, PK | 指标编号（关联 `metric_info.id`） |

> 联合主键：`(column_id, metric_id)`

---

### 7.6 实体关系图（ER）

```
table_info (表信息)
    │
    │ 1:N
    ▼
column_info (列信息) ──N:M── column_metric ──N:M── metric_info (指标信息)
```

---

## 8. 脚本与工具 (`app/scripts/`)

### 8.1 元数据知识库构建脚本 (`build_meta_knowledge.py`)

**用途**: 通过命令行参数传入人工配置文件路径，将表、字段、说明等元数据同步到知识库（向量库 + ES 索引）。

**入口函数**: `build()`

**使用方式**:
```bash
python -m app.scripts.build_meta_knowledge <config_path>
```

**当前状态**: 基础框架，核心同步逻辑待实现。`print(argv[2])` 和 `logger.info("构建知识库脚本执行了")` 为占位代码。

---

## 9. 依赖关系图

### 9.1 外部依赖 (`pyproject.toml`)

| 包名 | 版本 | 用途 |
|------|------|------|
| `fastapi[standard]` | 0.128.0 | Web 框架 |
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

### 9.2 模块间依赖关系

```
app/conf/app_config.py  ◄── app/core/log.py
        ▲                        ▲
        │                        │
        ├── app/clients/mysql_client_manager.py
        ├── app/clients/es_client_manager.py
        ├── app/clients/qdrant_client_manager.py
        ├── app/clients/embedding_client_manager.py
        │
        └── app/models/*.py

app/core/context.py ◄── app/core/log.py
app/core/log.py     ◄── app/scripts/build_meta_knowledge.py

app/clients/embedding_client_manager.py ◄── app/clients/qdrant_client_manager.py
app/models/base.py  ◄── app/models/table_info_mysql.py
                    ◄── app/models/column_info_mysql.py
                    ◄── app/models/metric_info_mysql.py
                    ◄── app/models/column_metric_mysql.py
```

---

## 10. 项目运行方式

### 10.1 环境准备

```bash
# 1. 克隆项目
cd sgg_data-agent

# 2. 安装依赖（使用 uv）
uv sync

# 3. 配置外部服务
# 编辑 conf/app_config.yaml，确保 MySQL / ES / Qdrant / Embedding / LLM 服务地址正确
# 注意：需要填写有效的 DeepSeek API Key
```

### 10.2 初始化数据库

```bash
# 在 MySQL 中执行建表脚本
mysql -h 192.168.200.10 -u atguigu -p < 笔记/4.SQL脚本/meta-schema.sql
mysql -h 192.168.200.10 -u atguigu -p < 笔记/4.SQL脚本/dw-schema.sql

# 导入初始数据
mysql -h 192.168.200.10 -u atguigu -p < 笔记/4.SQL脚本/meta-schema-data.sql
mysql -h 192.168.200.10 -u atguigu -p < 笔记/4.SQL脚本/dw-schema-data.sql
```

### 10.3 运行各模块

```bash
# 测试配置加载
python -m app.conf.app_config

# 测试日志系统
python -m app.core.log

# 测试 MySQL 连接
python -m app.clients.mysql_client_manager

# 测试 ES 连接
python -m app.clients.es_client_manager

# 测试 Qdrant 连接
python -m app.clients.qdrant_client_manager

# 测试 Embedding 服务
python -m app.clients.embedding_client_manager

# 构建元数据知识库
python -m app.scripts.build_meta_knowledge <config_path>
```

### 10.4 启动 FastAPI 服务（预留）

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> 当前 `main.py` 为 PyCharm 默认模板，FastAPI 路由与业务逻辑待后续实现。

---

## 附录：技术栈总览

| 类别 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | >= 3.12 |
| Web 框架 | FastAPI | 0.128.0 |
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