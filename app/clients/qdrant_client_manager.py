import asyncio
from typing import Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.conversions.common_types import VectorParams
from qdrant_client.http.models import PointStruct, Distance

from app.clients.embedding_client_manager import embedding_client_manager
from app.conf.app_config import QdrantConfig, app_config


class QdrantClientManager:
    def __init__(self, config: QdrantConfig):
        self.config = config
        self.client: Optional[AsyncQdrantClient] = None

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncQdrantClient(url=self._get_url())

    async def close(self):
        if self.client:
            await self.client.close()


qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == '__main__':
    qdrant_client_manager.init()
    client = qdrant_client_manager.client

    embedding_client_manager.init()
    embedding_client = embedding_client_manager.client


    async def batch_save_to_qdrant(ids: list[int], payloads: list[str], embeddings: list[list[float]],
                                   batch_size: int = 100):
        if await client.collection_exists(collection_name="test"):
            await client.delete_collection(collection_name="test")
            await client.create_collection(collection_name="test", vectors_config=VectorParams(
                size=app_config.qdrant.embedding_size,
                distance=Distance.COSINE
            ))
            zipped = list(zip(ids, payloads, embeddings))
            for i in range(0, len(zipped), batch_size):
                batch = zipped[i:i + batch_size]
                points = [PointStruct(
                    id=id,
                    vector=embedding,
                    payload={"key": payload}
                ) for id, payload, embedding in batch]
                await client.upsert(collection_name="test", points=points)


    async def test(texts: list[str]):
        points = []
        for i, text in enumerate(texts):
            points.append({
                "id": i,
                "payload": text,
                "embedding_text": text
            })
        embeddings = []
        embedding_texts = [point["embedding_text"] for point in points]
        batch_size: int = 5
        for i in range(0, len(embedding_texts), batch_size):
            batch_embedding_text = embedding_texts[i:i + batch_size]
            batch_embeddings = await embedding_client.aembed_documents(batch_embedding_text)
            embeddings.extend(batch_embeddings)

        ids = [point["id"] for point in points]
        payloads = [point["payload"] for point in points]
        await batch_save_to_qdrant(ids, payloads, embeddings)


    keywords = ["人工智能", "机器学习", "数据挖掘", "深度学习", "自然语言", "计算机", "大数据", "云计算", "物联网",
                "区块链", "FastAPI", "数据库", "Qdrant", "LangChain", "模型", "ORM", "向量", "协程", "Prompt", "文档",
                "早餐", "周末", "雨天", "晚上", "温水", "阅读", "地铁", "冬季", "花草", "聚会", "Python", "MySQL",
                "Jieba", "Loguru", "加密", "接口", "检索", "分词", "嵌入"]
    asyncio.run(test(keywords))
