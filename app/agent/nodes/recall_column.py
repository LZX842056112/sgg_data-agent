import asyncio

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime
from typing_extensions import runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from app.prompt.prompt_loader import load_prompt


async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = get_stream_writer()
    writer({"type": "progress", "step": "召回字段", "status": "running"})

    try:
        # 1.基于原query通过Langchain，llm进行扩展
        query = state["query"]
        # 1.1 构建提示词运行单元
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_column_recall"), input_variables=["query"])
        # 1.2 大模型运行单元
        # 1.3 结果处理运行单元
        output = JsonOutputParser()
        # 1.4 构建链，执行异步调用
        chain = prompt | llm | output
        result = await chain.ainvoke({"query": query})
        logger.info(f"recall_column节点，大模型扩充字段结果：{result}")
        # 2.去重拼接 抽取关键词列表
        keywords = state["keywords"]
        keywords = list(set(result + keywords))
        # 3.遍历关键词列表，根据每个关键词进行向量检索 将得分大于0.6的向量点
        # 3.1 创建字段信息字典 key:字段ID value：字段信息
        retrieved_columns_map: dict[str, ColumnInfo] = {}
        # 3.2 从runtime获取embeding客户端
        embedding_client = runtime.context["embedding_client"]
        column_qdrant_repository = runtime.context["column_qdrant_repository"]

        for keyword in keywords:
            # 3.1 对关键词转为向量
            embedding = await embedding_client.aembed_query(keyword)
            # 3.2 检索字段信息向量集合
            colunm_infos: list[ColumnInfo] = await column_qdrant_repository.search(embedding)
            # 3.3 获取检索结果
            for colunm_info in colunm_infos:
                colunm_id = colunm_info.id
                if colunm_id not in retrieved_columns_map:
                    retrieved_columns_map[colunm_id] = colunm_info
        # 4.获取可能需要字段信息
        writer({"type": "progress", "step": "召回字段", "status": "success"})
        logger.info(f"召回字段成功，字段信息：{list(retrieved_columns_map.keys())}")
        return {"retrieved_columns": list(retrieved_columns_map.values())}
    except Exception as e:
        logger.error(f"召回字段节点执行异常:{e}")
        writer({"type": "progress", "step": "召回字段", "status": "error"})
        raise
