from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from app.prompt.prompt_loader import load_prompt


async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回字段", "status": "running"})
    try:

        # 1.调用llm 对原query问题进行增强 扩展关键词
        query = state["query"]

        # 1.1 提示词运行单元
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_column_recall"), input_variables=["query"])

        # 1.2 定义JSON解析器对象 通过"管道符"|组合运行多个运行单元
        parser = JsonOutputParser()
        chain = prompt | llm | parser
        result = await chain.ainvoke({"query": query})

        # 2.关键词列表：抽取关键词+扩展后
        logger.info(f"对原查询llm扩展后字段列表：{result}")
        keywords = state["keywords"]
        keywords = list(set(keywords + result))

        # 3.遍历关键词列表，根据关键词查询qdrant进行语义相近检索
        retrieved_column_map: dict[str, ColumnInfo] = {}
        embedding_client = runtime.context["embedding_client"]
        column_qdrant_repository = runtime.context["column_qdrant_repository"]
        for keyword in keywords:
            embedding = await embedding_client.aembed_query(keyword)
            column_infos: list[ColumnInfo] = await column_qdrant_repository.search(embedding)
            for column_info in column_infos:
                column_id = column_info.id
                if column_id not in retrieved_column_map:
                    retrieved_column_map[column_id] = column_info
        writer({"type": "progress", "step": "召回字段", "status": "success"})
        logger.info(f"召回字段成功：{list(retrieved_column_map.keys())}")
        # 4.将结果写入到state
        return {"retrieved_columns": list(retrieved_column_map.values())}
    except Exception as e:
        writer({"type": "progress", "step": "召回字段", "status": "error"})
        logger.error(f"召回字段失败, 错误信息: {str(e)}")
        raise
