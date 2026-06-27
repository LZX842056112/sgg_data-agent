from dataclasses import asdict

from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch
from watchfiles import awatch

from app.entities.value_info import ValueInfo


class ValueESRepository:
    """操作字段取值ES持久层类"""
    idx_name = "data-agent-column"
    es_index_mappings = {
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
        # 判断索引库是否存在
        if not await self.client.indices.exists(index=self.idx_name):
            # 创建索引库
            await self.client.indices.create(
                index=self.idx_name,
                mappings=self.es_index_mappings
            )

    async def upsert(self, value_infos: list[ValueInfo], batch_size=10):
        for i in range(0, len(value_infos), batch_size):
            batch = value_infos[i:i + batch_size]
            operations: list = []
            for value_info in batch:
                # 指定操作的索引库以及文档ID
                operations.append({
                    "index": {
                        "_index": self.idx_name,
                        "_id": value_info.id
                    }
                })
                # 指定文档内容
                operations.append(asdict(value_info))
                # 将本批次数据批量写入ES
                await self.client.bulk(operations=operations)

    """
    #条件检索 采用全文查询match 特点：先对文本进行分词，根据分词后词条进行检索
        POST data-agent-column/_search
        {
          "from":0,
          "size": 10,
          "query": {
            "match": {
              "value": "广东地区"
            }
          },
          "min_score": 0.6
        }
    """

    async def search(self, keyword: str, score_threshold: float = 0.6, limit: int = 10) -> list[ValueInfo]:
        # 1.执行全文检索
        result: ObjectApiResponse = await self.client.search(
            # 索引库名称 不指定会查询所有索引库
            index=self.idx_name,
            # 查询条件，采用match全文查询
            query={
                "match": {
                    "value": keyword
                }
            },
            # 相关性得分
            min_score=score_threshold,
            # 返回记录数
            size=limit
        )
        # 2.解析ES结果
        return [ValueInfo(**hit["_source"]) for hit in result["hits"]["hits"]]
