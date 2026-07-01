from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.entities.value_info import ValueInfo
from app.prompt.prompt_loader import load_prompt


async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回字段取值", "status": "running"})
    try:
        # 1.通过大模型扩充关键词
        query = state["query"]
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_value_recall"), input_variables=["query"])
        chain = prompt | llm | JsonOutputParser()
        result = await chain.ainvoke({"query": query})

        # 2.关键词列表 已抽取关键词+扩充后的
        keywords = state["keywords"]
        keywords = list(set(keywords + result))

        # 3.遍历关键词列表 采用全文查询ES获取值信息ValueInfo
        retrieved_value_map: dict[str, ValueInfo] = {}
        value_es_repository = runtime.context["value_es_repository"]
        for keyword in keywords:
            value_infos: list[ValueInfo] = await value_es_repository.search(keyword)
            for value_info in value_infos:
                value_info_id = value_info.id
                if value_info_id not in retrieved_value_map:
                    retrieved_value_map[value_info_id] = value_info
        writer({"type": "progress", "step": "召回字段取值", "status": "success"})
        logger.info(f"召回字段取值成功：{list(retrieved_value_map.keys())}")
        # 4.更新state中召回字段信息列表
        return {"retrieved_values": list(retrieved_value_map.values())}
    except Exception as e:
        writer({"type": "progress", "step": "召回字段取值", "status": "error"})
        logger.error(f"召回字段取值失败, 错误信息: {str(e)}")
        raise
