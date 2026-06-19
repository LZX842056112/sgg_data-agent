import asyncio
from typing import Union, Optional
from sqlalchemy import text, Result
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from app.conf.app_config import DBConfig, app_config


class MysqlClientManager:
    """
    用于操作dw,meta数据客户端管理器
    """

    def __init__(self, db_config: DBConfig):
        self.db_config = db_config
        # self.engine:AsyncEngine = None #警告
        # self.engine:AsyncEngine | None = None
        # self.engine:Union[AsyncEngine, None] = None
        self.engine: Optional[AsyncEngine, None] = None

    def _get_url(self):
        return f"mysql+asyncmy://{self.db_config.user}:{self.db_config.password}@{self.db_config.host}:{self.db_config.port}/{self.db_config.database}?charset=utf8mb4"

    def init(self):
        """创建引擎对象，用于创建数据库连接"""
        self.engine: AsyncEngine = create_async_engine(
            url=self._get_url(),
            echo=False
        )

    async def close(self):
        if self.engine:
            await self.engine.dispose()


# 操作数仓mySQL客户端管理器对象
dw_mysql_client_manager = MysqlClientManager(app_config.db_dw)
# 操作元数据库mySQL客户端管理器对象
meta_mysql_client_manager = MysqlClientManager(app_config.db_meta)

if __name__ == '__main__':
    # 操作数仓MySQL
    dw_mysql_client_manager.init()


    async def test():
        # 获取操作DBSession对象
        async with AsyncSession(dw_mysql_client_manager.engine) as dw_session:
            ## 案例一
            # sql = "show tables"
            # # 执行自定义SQL
            # result:Result =  await dw_session.execute(text(sql))
            # # 获取结果 一列多行采用 .scalars().fetchall()
            # print(result.scalars().fetchall())
            ## 案例二
            # sql = "select md5('abc')"
            # result:Result = await dw_session.execute(text(sql))
            # #  获取结果 一列一行采用 .scalar()
            # print(result.scalar())
            # 案例三
            sql = "show tables"
            # 执行自定义SQL
            result: Result = await dw_session.execute(text(sql))
            # 获取结果 如果获取字段名称对应字段取值 采用.mappings().fetchall()
            print(result.mappings().fetchall())


    asyncio.run(test())
