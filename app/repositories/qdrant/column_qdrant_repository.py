from dataclasses import asdict

from qdrant_client import AsyncQdrantClient, models
from qdrant_client.conversions.common_types import VectorParams, PointStruct, QueryResponse

from app.conf.app_config import app_config
from app.entities.column_info import ColumnInfo


class ColumnQdrantRepository:
    """用于操作字段信息向量集合持久层"""

    collection_name = "data-agent-column"

    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def ensure_collection(self):
        # 1.判断集合是否存在
        if not await self.client.collection_exists(collection_name=self.collection_name):
            # 2.创建集合
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=app_config.qdrant.embedding_size,
                    distance=models.Distance.COSINE
                )
            )

    async def upsert(self, ids: list[str], embeddings: list[list[float]], payloads: list[ColumnInfo],
                     batch_size: int = 10):
        # 1. 使用zip函数 按索引“打包”为元组迭代器 [(id,vector,column_info)]
        zipped = list(zip(ids, embeddings, payloads))
        # 2. 分批次插入向量数据
        for i in range(0, len(zipped), batch_size):
            batch = zipped[i:i + batch_size]
            points = [PointStruct(
                id=id,
                vector=embedding,
                payload=asdict(payload)  # name = region_nanme ---> name:region_nanme
            ) for id, embedding, payload in batch]
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

    async def search(self, embedding: list[float], score: float = 0.6, limit: int = 10):
        result: QueryResponse = await self.client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            score_threshold=score,
            limit=limit
        )
        return [ColumnInfo(**point.payload) for point in result.points]
