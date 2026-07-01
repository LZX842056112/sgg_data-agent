import asyncio
from typing import Optional, Union

from sqlalchemy import text, Result
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker

from app.conf.app_config import DBConfig, app_config


class MySQLClientManager:
    def __init__(self, db_config: DBConfig):
        self.db_config = db_config
        # self.engine: AsyncEngine = None
        # self.engine: AsyncEngine | None = None
        # self.engine: Optional[AsyncEngine] = None
        self.engine: Union[AsyncEngine, None] = None
        self.session_factory = None

    def _get_url(self):
        return f"mysql+asyncmy://{self.db_config.user}:{self.db_config.password}@{self.db_config.host}/{self.db_config.database}?charset=utf8mb4"

    def init(self):
        self.engine = create_async_engine(url=self._get_url(), echo=True, pool_size=10, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(bind=self.engine, expire_on_commit=False, autoflush=False)

    async def close(self):
        if self.engine:
            await self.engine.dispose()


dw_mysql_client_manager = MySQLClientManager(db_config=app_config.db_dw)
meta_mysql_client_manager = MySQLClientManager(db_config=app_config.db_meta)

if __name__ == '__main__':
    async def db_test():
        dw_mysql_client_manager.init()
        async with AsyncSession(dw_mysql_client_manager.engine) as dw_session:
            # sql = "show tables"
            sql = "select * from fact_order"
            result: Result = await dw_session.execute(text(sql))
            # 单列单行用scalar() str
            # print(type(result.scalar()))
            # 单列多行用scalars() ScalarResult .fetchall() 得到的是列表
            # print(result.scalars().fetchall())
            # print(result.fetchall())
            print(result.fetchmany())
            print(result.mappings().fetchall())
        await dw_mysql_client_manager.close()


    asyncio.run(db_test())
