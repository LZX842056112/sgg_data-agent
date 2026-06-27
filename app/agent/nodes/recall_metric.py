from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.entities.metric_info import MetricInfo
from app.prompt.prompt_loader import load_prompt


async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    # 1.获取流写入器对象
    write = runtime.stream_writer
    write({"type": "progress", "step": "召回指标", "status": "running"})
    # 2.具体逻辑
    try:
        # 2.1 从state获取用户问题、关键词列表(包含原query)
        query = state["query"]
        keywords = state["keywords"]
        # 2.2 先对原query问题通过llm进行扩展 获取回答问题可能需要指标列表
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_metric_recall"), input_variables=["query"])
        json_output = JsonOutputParser()
        chain = prompt | llm | json_output
        result = await chain.ainvoke({"query": query})

        # 2.3 得到最终关键词列表=llm扩展后关键词+state中jieba分词后关键词
        keywords = list(set(keywords + result))

        # 2.4 声明指标信息字典，字典Key=指标ID  Value=指标信息（MetricInfo） 方便去重
        retrieved_metrics_dict: dict[str, MetricInfo] = {}

        # 2.5 从runtime中获取Embedding客户端、指标向量持久层
        embedding_client = runtime.context["embedding_client"]
        metric_qdrant_repository = runtime.context["metric_qdrant_repository"]

        # 2.6 遍历关键词列表，执行向量检索
        for keyword in keywords:
            # 2.6.1 将关键词转为向量
            embedding = await embedding_client.aembed_query(keyword)
            # 2.6.2 执行向量索引库检索
            metric_infos: list[MetricInfo] = await metric_qdrant_repository.search(embedding)
            # 2.6.3 去重
            for metric_info in metric_infos:
                metric_id = metric_info.id
                if metric_id not in retrieved_metrics_dict:
                    retrieved_metrics_dict[metric_id] = metric_info

        # 2.7 更新State中召回指标列表
        write({"type": "progress", "step": "召回指标", "status": "success"})
        logger.info(f"召回指标信息成功：{list(retrieved_metrics_dict.keys())}")
        return {"retrieved_metrics": list(retrieved_metrics_dict.values())}
    except Exception as e:
        logger.error(f"召回指标发生异常：{e}")
        write({"type": "progress", "step": "召回指标", "status": "error"})
        raise
