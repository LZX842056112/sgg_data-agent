import asyncio

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from app.agent.context import DataAgentContext
from app.agent.nodes.add_extra_context import add_extra_context
from app.agent.nodes.correct_sql import correct_sql
from app.agent.nodes.execute_sql import execute_sql
from app.agent.nodes.extract_keywords import extract_keywords
from app.agent.nodes.filter_metric import filter_metric
from app.agent.nodes.filter_table import filter_table
from app.agent.nodes.generate_sql import generate_sql
from app.agent.nodes.merge_retrieved_info import merge_retrieved_info
from app.agent.nodes.recall_column import recall_column
from app.agent.nodes.recall_metric import recall_metric
from app.agent.nodes.recall_value import recall_value
from app.agent.nodes.validate_sql import validate_sql
from app.agent.state import DataAgentState
from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository

# 1.创建graph构建器对象
graph_builder = StateGraph(state_schema=DataAgentState, context_schema=DataAgentContext)

# 2.添加节点
graph_builder.add_node("extract_keywords", extract_keywords)
graph_builder.add_node("recall_column", recall_column)
graph_builder.add_node("recall_metric", recall_metric)
graph_builder.add_node("recall_value", recall_value)
graph_builder.add_node("merge_retrieved_info", merge_retrieved_info)
graph_builder.add_node("filter_table", filter_table)
graph_builder.add_node("filter_metric", filter_metric)
graph_builder.add_node("add_extra_context", add_extra_context)
graph_builder.add_node("generate_sql", generate_sql)
graph_builder.add_node("validate_sql", validate_sql)
graph_builder.add_node("correct_sql", correct_sql)
graph_builder.add_node("execute_sql", execute_sql)

# 3.添加边
graph_builder.add_edge(START, "extract_keywords")
graph_builder.add_edge("extract_keywords", "recall_column")
graph_builder.add_edge("extract_keywords", "recall_metric")
graph_builder.add_edge("extract_keywords", "recall_value")

graph_builder.add_edge("recall_column", "merge_retrieved_info")
graph_builder.add_edge("recall_metric", "merge_retrieved_info")
graph_builder.add_edge("recall_value", "merge_retrieved_info")

graph_builder.add_edge("merge_retrieved_info", "filter_table")
graph_builder.add_edge("merge_retrieved_info", "filter_metric")

graph_builder.add_edge("filter_table", "add_extra_context")
graph_builder.add_edge("filter_metric", "add_extra_context")

graph_builder.add_edge("add_extra_context", "generate_sql")
graph_builder.add_edge("generate_sql", "validate_sql")

# 条件边 如果校验SQL节点更新error有值 执行校正SQL 没有值 执行执行SQL
graph_builder.add_conditional_edges("validate_sql", lambda state: "execute_sql" if state["error"] is None else "correct_sql", {"execute_sql":"execute_sql", "correct_sql":"correct_sql"})

graph_builder.add_edge("correct_sql", "execute_sql")
graph_builder.add_edge("execute_sql", END)

# 4.编译得到graph
graph = graph_builder.compile()

# 5.测试
if __name__ == '__main__':
    # print(graph.get_graph().draw_mermaid())

    # 调用执行graph
    async def test_run_graph():
        # 异步调用，一次性返回结果
        # result = await graph.ainvoke(input=state)
        # 实时返回节点状态以及数据。改为流式调用，流式响应自定义数据 参数：input
        state = DataAgentState(query="华北地区去年卖了多少钱")
        # stream_mode=values 每一个节点输出state所有数据
        # stream_mode=updates 每一个节点state被更新
        # stream_mode=custom 节点写自定义数据
        # TODO 利用上下文存放运行时依赖对象，用于节点使用
        # 1.初始化工作
        dw_mysql_client_manager.init()
        meta_mysql_client_manager.init()
        embedding_client_manager.init()
        qdrant_client_manager.init()
        es_client_manager.init()

        # 2.创建不同持久层对象
        async with (meta_mysql_client_manager.session_factory() as meta_session, dw_mysql_client_manager.session_factory() as dw_session):
            context = DataAgentContext(
                meta_mysql_repository=MetaMySQLRepository(meta_session),
                dw_mysql_repository=DWMySQLRepository(dw_session),
                embedding_client=embedding_client_manager.client,
                column_qdrant_repository=ColumnQdrantRepository(qdrant_client_manager.client),
                metric_qdrant_repository=MetricQdrantRepository(qdrant_client_manager.client),
                value_es_repository=ValueESRepository(es_client_manager.client)

            )
            async for chunk in graph.astream(input=state, context=context, stream_mode="custom"):
                print(chunk)

            # 3.关闭连接
            await dw_mysql_client_manager.close()
            await meta_mysql_client_manager.close()
            await es_client_manager.close()
            await qdrant_client_manager.close()
    asyncio.run(test_run_graph())
