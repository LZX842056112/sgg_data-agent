import asyncio
from typing import Optional
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingClientManager:
    """
    用于操作embedding客户端管理器
    """

    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.client: Optional[HuggingFaceEndpointEmbeddings] = None

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = HuggingFaceEndpointEmbeddings(
            model=self._get_url()
        )


embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == '__main__':
    embedding_client_manager.init()
    client = embedding_client_manager.client


    def test_sync_embedding():
        # embed_query = client.embed_query("你好")
        embed_query = client.embed_documents(["你好", "世界"])
        print(embed_query)  # [[],[]]
        print(len(embed_query))


    # test_sync_embedding()

    async def test_async_embedding():
        # query = await client.aembed_query("苹果")
        # print(query)
        aembed_documents_ = await client.aembed_documents(["苹果", "香蕉"])
        print(aembed_documents_)


    asyncio.run(test_async_embedding())


    async def test_async_batch_embedding(batch_size: int = 5):
        keywords = ["苹果", "香蕉", "橘子", "芒果", "开发工程师", "机器学习", "深度学习", "数据科学", "数据处理",
                    "数据可视化", "数据可视化", "数据可视化", "数据可视化", "数据可视化", "数据可视化", "数据可视化",
                    "数据可视化", "数据可视化", "数据可视化", "汽车", "小米", "大米"]
        for i in range(0, len(keywords), batch_size):
            print("处理批次", i, batch_size)
            batch = keywords[i:i + batch_size]
            batch_embed = await client.aembed_documents(batch)
            print(batch_embed)


    asyncio.run(test_async_batch_embedding())
