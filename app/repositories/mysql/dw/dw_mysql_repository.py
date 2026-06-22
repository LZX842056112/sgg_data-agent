from sqlalchemy import text, Result
from sqlalchemy.ext.asyncio import AsyncSession


class DWMySQLRepository:
    """跟MySQL数据库（数仓数据库）交互持久层 必须通过Session对象进行CURD"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_type_by_table_id(self, table_id: str) -> dict[str, str]:
        """根据表ID/表名称查询该表下所有字段信息 目的获取字段数据类型"""
        sql = f"show columns from {table_id}"
        result: Result = await self.session.execute(text(sql))
        # 查询结果是多列多行 返回列表 包装对象
        return {row.Field: row.Type for row in result.fetchall()}

    async def get_column_values_by_table_id(self, table_id: str, column_name: str, limit: int = 10) -> list[str]:
        """查询指定个数某张表某个字段取值"""
        sql = f"SELECT distinct {column_name} from {table_id} limit {limit}"
        result: Result = await self.session.execute(text(sql))
        # 结果：一列多行
        return result.scalars().fetchall()
