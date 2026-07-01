import json

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.agent.context import DataAgentContext
from app.agent.graph import graph
from app.agent.state import DataAgentState
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import meta_mysql_client_manager, dw_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class QueryService:

    def __init__(
            self,
            embedding_client: HuggingFaceEndpointEmbeddings,
            column_qdrant_repository:ColumnQdrantRepository,
            metric_qdrant_repository:MetricQdrantRepository,
            value_es_repository:ValueESRepository,
            meta_mysql_repository:MetaMySQLRepository,
            dw_mysql_repository:DWMySQLRepository
    ):
        self.embedding_client = embedding_client
        self.column_qdrant_repository = column_qdrant_repository
        self.metric_qdrant_repository = metric_qdrant_repository
        self.value_es_repository = value_es_repository
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository

    async def query_answer(self, question: str):
        # async with (meta_mysql_client_manager.session_factory() as meta_session, dw_mysql_client_manager.session_factory() as dw_session):
        context = DataAgentContext(
            embedding_client=self.embedding_client,
            column_qdrant_repository=self.column_qdrant_repository,
            metric_qdrant_repository=self.metric_qdrant_repository,
            value_es_repository=self.value_es_repository,
            meta_mysql_repository=self.meta_mysql_repository,
            dw_mysql_repository=self.dw_mysql_repository
        )
        print(f"embedding_client:{self.embedding_client}")
        print(f"meta_mysql_repository:{self.meta_mysql_repository}")
        async for chunk in graph.astream(input=DataAgentState(query=question), context=context,
                                         stream_mode="custom"):
            # 查询结果是一个列表[字典] 这里转为JSON对象响应 ensure_ascii解决中文乱码问题，default遇上无法转JSON数据，采用字符串处理
            yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n"
