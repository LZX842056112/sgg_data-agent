from dataclasses import asdict

from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch
from watchfiles import awatch

from app.entities.value_info import ValueInfo


class ValueESRepository:
    """用于操作字段取值ES索引库持久层"""

    index_name = "data-agent-column"
    index_mappings = {
        "dynamic": False,
        "properties": {
            "id": {"type": "keyword"},
            "value": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_max_word"},
            "column_id": {"type": "keyword"}
        }
    }

    def __init__(self, client: AsyncElasticsearch):
        self.client = client

    async def ensure_index(self):
        if not await self.client.indices.exists(index=self.index_name):
            await self.client.indices.create(
                index=self.index_name,
                mappings=self.index_mappings
            )

    async def upsert(self, value_infos: list[ValueInfo], batch_size: int = 10):
        for i in range(0, len(value_infos), batch_size):
            batch = value_infos[i:i + batch_size]
            operations = []
            for value_info in batch:
                operations.append({"index": {"_index": self.index_name, "_id": value_info.id}})
                operations.append(asdict(value_info))
            await self.client.bulk(operations=operations)

    """
        POST data-agent-column/_search
        {
          "query": {
            "match": {
              "value": "广东省"
            }
          },
          "size": 10,
          "min_score":0.7
        }
    """

    async def search(self, keyword: str, score: float = 0.6, limit: int = 10) -> list[ValueInfo]:
        # 1.执行全文检索
        result: ObjectApiResponse = await self.client.search(
            index=self.index_name,
            query={
                "match": {
                    "value": keyword
                }
            },
            min_score=score,
            size=limit
        )
        # 2.解析ES响应结果
        return [ValueInfo(**hit["_source"]) for hit in result["hits"]["hits"]]
