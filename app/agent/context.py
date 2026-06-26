from langchain_huggingface import HuggingFaceEndpointEmbeddings
from typing_extensions import TypedDict

from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class DataAgentContext(TypedDict):
    """runtime中context数据结构定义,存放静态依赖：操作不同库持久层对象 对于节点而言只读"""
    meta_mysql_repository: MetaMySQLRepository
    dw_mysql_repository: DWMySQLRepository
    embedding_client: HuggingFaceEndpointEmbeddings
    column_qdrant_repository: ColumnQdrantRepository
    metric_qdrant_repository: MetricQdrantRepository
    value_es_repository: ValueESRepository
