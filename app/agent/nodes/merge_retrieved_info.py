from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, MetricInfoState, TableInfoState, ColumnInfoState
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo


async def merge_retrieved_info(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """从已召回信息+手动补齐信息 得到回答用户问题需要表（包含字段列表）以及指标"""
    write = runtime.stream_writer
    write({"type": "progress", "step": "合并召回信息", "status": "running"})
    try:
        # 1.准备工作
        # 1.1 从state获取已召回信息: 已召回字段、已召回指标、已召回字段取值
        retrieved_columns: list[ColumnInfo] = state["retrieved_columns"]
        retrieved_metrics: list[MetricInfo] = state["retrieved_metrics"]
        retrieved_values: list[ValueInfo] = state["retrieved_values"]
        # 1.2 从runtime中获取操作meta数据库持久层对象
        meta_mysql_repository = runtime.context["meta_mysql_repository"]

        # 2. 封装已召回信息中包含所有字段信息 考虑重复问题
        # 2.1 已召回字段列表转为字典，得到字段字典 字典key:字段ID Value:字段信息ColumnInfo
        column_id_column_info_dict = {column_info.id: column_info for column_info in retrieved_columns}
        # 2.2 从已召回指标列表中，得到指标相关字段ID，将字段信息加入到“字段字典”中
        for retrieved_metric in retrieved_metrics:
            for column_id in retrieved_metric.relevant_columns:
                # 2.2.1 判断指标包含字段ID知否存在于字典中
                if column_id not in column_id_column_info_dict:
                    # 2.2.2 从meta数据库中column_info表查询字段信息
                    column_info: ColumnInfo = await meta_mysql_repository.get_column_info_by_id(column_id)
                    column_id_column_info_dict[column_id] = column_info

        # 2.3 从已召回字段取值列表中，得到字段取值对应 字段ID，将字段信息加入到“字段字典”中 注意：为字段增加实例值
        for value_info in retrieved_values:
            column_id = value_info.column_id
            if column_id not in column_id_column_info_dict:
                # 说明字段ID不在字段字典中，根据字段ID查询字段信息
                column_info: ColumnInfo = await meta_mysql_repository.get_column_info_by_id(column_id)
                column_id_column_info_dict[column_id] = column_info
            # 字段取值（枚举值）
            value = value_info.value
            if value not in column_id_column_info_dict[column_id].examples:
                column_id_column_info_dict[column_id].examples.append(value)

        # 3 将所有字段信息 转为 “表-字段列表”字典 key:table_id value:字段信息列表
        table_id_columns_dict: dict[str, list[ColumnInfo]] = {}
        # 3.1 遍历"字段字典"的Value
        for column_info in column_id_column_info_dict.values():
            # 3.2 得到字段中所属表的ID
            table_id = column_info.table_id
            # 3.3 判断“表-字段列表”字典 是否包含字段ID，创建字段列表，将字段加入到列表中
            if table_id not in table_id_columns_dict:
                table_id_columns_dict[table_id] = []
            table_id_columns_dict[table_id].append(column_info)

        # 4. 补齐主外键字段信息
        # 4.1 遍历“表-字段列表”中key 得到每张表ID
        for table_id in table_id_columns_dict.keys():
            # 4.2 获取到当前表已召回所有字段ID
            column_ids = [column.id for column in table_id_columns_dict[table_id]]
            # 4.3 根据表ID查询meta库中column_info表 获取主外键字段
            key_columns: list[ColumnInfo] = await meta_mysql_repository.get_key_columns_by_table_id(table_id)
            # 4.4 遍历主外键列表 是否需要将查询到主外键字段信息加入 对应表的字段列表中
            for key_column in key_columns:
                # 4.4.1 判断是否已经包含主外键
                if key_column.id not in column_ids:
                    # 4.4.2 暂未包含主外键字段信息，则添加
                    table_id_columns_dict[table_id].append(key_column)

        # 5 处理表信息封装table_infos:list[TableInfoState]
        table_infos: list[TableInfoState] = []
        # 5.1 遍历“表-字段列表”字典
        for table_id, column_infos in table_id_columns_dict.items():
            # 5.2 封装表state 表信息从meta数据库table_info查询 TODO
            table_info: TableInfo = await meta_mysql_repository.get_table_info_by_id(table_id)
            # 5.3 封装表中字段state
            table_info_state = TableInfoState(
                name=table_info.name,
                role=table_info.role,
                description=table_info.description,
                columns=[ColumnInfoState(
                    name=column_info.name,
                    type=column_info.type,
                    role=column_info.role,
                    examples=column_info.examples,
                    description=column_info.description,
                    alias=column_info.alias
                ) for column_info in column_infos]
            )
            # 5.4 将表state加入到table_infos
            table_infos.append(table_info_state)
        # 6. 初始存放指标信息列表
        # 处理指标信息state 从已召回指标获取封装
        metric_infos: list[MetricInfoState] = []
        if retrieved_metrics:
            for metric_info in retrieved_metrics:
                metric_info_state = MetricInfoState(
                    name=metric_info.name,
                    description=metric_info.description,
                    relevant_columns=metric_info.relevant_columns,
                    alias=metric_info.alias
                )
                metric_infos.append(metric_info_state)
        write({"type": "progress", "step": "合并召回信息", "status": "success"})
        logger.info(f"合并召回信息成功，表：{table_id_columns_dict.keys()}")
        logger.info(f"合并召回信息成功，字段：{ [column['name'] for ti in table_infos for column in ti['columns']]}")
        logger.info(f"合并召回信息成功，指标：{[metric_info['name'] for metric_info in metric_infos]}")
        return {"table_infos": table_infos, "metric_infos": metric_infos}
    except Exception as e:
        logger.error(f"合并召回信息发生异常：{e}")
        write({"type": "progress", "step": "合并召回信息", "status": "error"})
        raise
