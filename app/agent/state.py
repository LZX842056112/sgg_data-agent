from typing import TypedDict

from app.entities.column_info import ColumnInfo


class DataAgentState(TypedDict):
    query: str
    # 抽取关键字节点结果
    keywords: list[str]
    # 召回字段节点结果
    retrieved_columns: list[ColumnInfo]
    # 校验SQL节点 SQL错误信息
    error: str
