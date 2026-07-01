from langchain_huggingface import HuggingFaceEndpointEmbeddings
from typing_extensions import TypedDict

from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class DataAgentContext(TypedDict):
    """提供给节点需要使用依赖对象：查询数据库、向量库持久层对象"""
    dw_mysql_repository: DWMySQLRepository
    meta_mysql_repository: MetaMySQLRepository
    column_qdrant_repository: ColumnQdrantRepository
    embedding_client: HuggingFaceEndpointEmbeddings
    value_es_repository: ValueESRepository
    metric_qdrant_repository: MetricQdrantRepository
