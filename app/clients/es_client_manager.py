import asyncio
from typing import Optional

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    def __init__(self, config: ESConfig):
        self.config = config
        self.client: Optional[AsyncElasticsearch] = None

    def init(self):
        self.client = AsyncElasticsearch(
            hosts=self._get_url()
        )

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    async def close(self):
        if self.client:
            await self.client.close()


es_client_manager = ESClientManager(app_config.es)

if __name__ == '__main__':
    es_client_manager.init()


    async def test():
        await es_client_manager.client.indices.create(
            index="test",
            mappings={
                "dynamic": False,
                "properties": {
                    "name": {
                        "type": "text"
                    },
                    "author": {
                        "type": "text"
                    },
                    "release_date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "page_count": {
                        "type": "integer"
                    }
                }
            }
        )


    # asyncio.run(test())

    async def bulk_insert():
        operations = [
            {"index": {"_index": "test"}},
            {
                "name": "Revelation Space",
                "author": "Alastair Reynolds",
                "release_date": "2000-03-15",
                "page_count": 585
            },
            {"index": {"_index": "test"}},
            {
                "name": "The Handmaids Tale",
                "author": "Margaret Atwood",
                "release_date": "1985-06-01",
                "page_count": 311
            }
        ]
        await es_client_manager.client.bulk(operations=operations)
        await es_client_manager.close()


    asyncio.run(bulk_insert())
