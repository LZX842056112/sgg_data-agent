from typing import Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from app.entities.column_info import ColumnInfo
from app.entities.column_metric import ColumnMetric
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.mappers.column_info_mapper import ColumnInfoMapper
from app.mappers.column_metric_mapper import ColumnMetricMapper
from app.mappers.metric_info_mapper import MetricInfoMapper
from app.mappers.table_info_mapper import TableInfoMapper
from app.models.column_info_mysql import ColumnInfoMySQL
from app.models.table_info_mysql import TableInfoMySQL


class MetaMySQLRepository:
    """跟MySQL数据库（元数据库）交互持久层 必须通过Session对象进行CURD"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_table_infos(self, table_infos: list[TableInfo]):
        """批量保存表信息"""
        # 将业务实体对象TableInfo 转为 数据库ORM实体TableInfoMySQL
        models = [TableInfoMapper.to_model(table_info) for table_info in table_infos]
        self.session.add_all(models)

    async def save_column_infos(self, column_infos: list[ColumnInfo]):
        """批量保存字段信息"""
        models = [ColumnInfoMapper.to_model(column_info) for column_info in column_infos]
        self.session.add_all(models)

    async def save_metric_info_to_meta_db(self, metric_infos: list[MetricInfo]):
        models = [MetricInfoMapper.to_model(metric_info) for metric_info in metric_infos]
        self.session.add_all(models)

    async def save_column_metric_info_to_meta_db(self, column_metrics: list[ColumnMetric]):
        models = [ColumnMetricMapper.to_model(column_metric) for column_metric in column_metrics]
        self.session.add_all(models)

    async def get_column_info_by_id(self, column_id: str) -> ColumnInfo:
        """根据字段ID查询字段信息 框架提供根据主键查询函数get(查询返回类型, 主键ID)"""
        column_info_mysql: Optional[ColumnInfoMySQL, None] = await self.session.get(ColumnInfoMySQL, column_id)
        # 将ORM模型转为业务模型
        return ColumnInfoMapper.to_entity(column_info_mysql)

    async def get_key_columns_by_table_id(self, table_id) -> list[ColumnInfo]:
        """根据表ID查询指定表的主外键字段列表
        生成sql = SELECT *
            from column_info where table_id = 'fact_order'
            and role in ('primary_key', 'foreign_key')
        """
        stmt = (select(ColumnInfoMySQL)
                .where(ColumnInfoMySQL.table_id == table_id, ColumnInfoMySQL.role.in_(['primary_key', 'foreign_key'])))
        # ORM方式执行查询 将结果中每条记录封装为“单个元素”ColumnInfoMySQL对象 故采用scalars
        result = await self.session.scalars(stmt)
        return [ColumnInfoMapper.to_entity(column_info_mysql) for column_info_mysql in result]

    async def get_table_info_by_id(self, table_id:str) ->TableInfo:
        """根据表ID查询表信息"""
        table_info_mysql:Union[TableInfoMySQL, None] = await self.session.get(TableInfoMySQL, table_id)
        return TableInfoMapper.to_entity(table_info_mysql)
