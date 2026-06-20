import asyncio
from typing import Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct, UpdateResult, QueryResponse, Filter, \
    FieldCondition, MatchValue
from app.clients.embedding_client_manager import embedding_client_manager
from app.conf.app_config import QdrantConfig, app_config


class QdrantClientManager:

    def __init__(self, config: QdrantConfig):
        self.config = config
        self.client: Optional[AsyncQdrantClient] = None

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncQdrantClient(
            url=self._get_url()
        )

    async def close(self):
        if self.client:
            await self.client.close()


qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == '__main__':
    # 初始化
    qdrant_client_manager.init()
    client = qdrant_client_manager.client

    embedding_client_manager.init()
    embedding_client = embedding_client_manager.client

    # 集合名称
    coll_name = "test"


    async def test_collection():
        """需求：判断集合是否存在，如果不存在则创建集合"""
        flag = await client.collection_exists(collection_name=coll_name)
        print("是否存在集合：", flag)
        if not flag:
            flag = await client.create_collection(
                collection_name=coll_name,
                vectors_config=VectorParams(
                    # 向量维度 大小
                    size=app_config.qdrant.embedding_size,
                    # 距离算法 余弦相似度
                    distance=Distance.COSINE
                )
            )
            print("创建集合结果：", flag)


    # asyncio.run(test_collection())

    async def test_add_points():
        """写入若干个有关或者不相关关键词 存入向量索引库集合中"""
        keywords = [
            "苹果", "香蕉", "橘子", "芒果", "开发工程师", "Java开发工程师", "C++开发工程师", "嵌入式开发工程师",
            "机器学习", "深度学习", "数据科学", "数据处理",
            "数据可视化", "汽车", "小米", "大米"
        ]
        # 构建向量点集合 采用列表推导式 将 列表类型从字符串转为 PointStruct 得到向量点列表
        points = [PointStruct(
            id=i,
            vector=await embedding_client.aembed_query(keyword),
            payload={"keyword": keyword}
        ) for i, keyword in enumerate(keywords)]

        # 调用Qdrant客户端对象写入数据
        result: UpdateResult = await client.upsert(
            collection_name=coll_name,
            points=points
        )
        print(result)


    # asyncio.run(test_add_points())

    async def test_search():
        """查询出跟 西瓜 语义相近的向量点"""
        embeded_query = await embedding_client.aembed_query("西瓜")
        # 执行查询
        result: QueryResponse = await client.query_points(
            collection_name=coll_name,
            query=embeded_query,
            limit=10,
            score_threshold=0.6,
            query_filter=Filter(
                must=[FieldCondition(key="keyword", match=MatchValue(value="橘子"))]
            ),
        )
        # 获取查询结果
        payload_list = [point.payload for point in result.points]
        print(payload_list)


    asyncio.run(test_search())
