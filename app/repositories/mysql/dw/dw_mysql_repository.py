from sqlalchemy import Result
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import text


class DWMySQLRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_types(self, table_name: str) -> dict[str, str]:
        # 定义sql
        sql = f"show columns  from {table_name}"
        # 执行sql
        result = await self.session.execute(text(sql))
        # 解析结果[(),()]
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_column_values(self, table_name: str, column_name: str, limit: int = 10) -> list[str]:
        # 定义sql
        sql = f"select distinct  {column_name} from {table_name} limit {limit}"
        # 执行sql
        result: Result = await self.session.execute(text(sql))
        # 解析结果
        return result.scalars().fetchall()

    async def get_db_info(self):
        """
        查询数据库环境信息，版本、方言
        :return:
        """
        # 查询数据版本
        result = await self.session.execute(text("select version()"))
        # 解析结果
        version = result.scalar()

        # 查询数据方言
        dialect = self.session.get_bind().dialect.name
        return {"version": version, "dialect": dialect}

    async def validate_sql(self, sql: str):
        """
        验证执行sql
        :param sql:
        :return: 如果sql语法不合法，会抛出异常
        """
        await self.session.execute(text(f"explain {sql}"))

    async def execute_sql(self, sql: str):
        result: Result = await self.session.execute(text(sql))
        return [dict(row_mapping) for row_mapping in result.mappings().fetchall()]
